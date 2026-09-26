import argparse

from bus import Bus, SIZE
from modes import ACC, Immediate
from opcodes import OPCODES

RESET_VECTOR = 0xFFFC  # the CPU loads PC from $FFFC/$FFFD on reset
DEFAULT_ORG = 0x8000   # ROM sits in the top half of the address space, RAM in the bottom

# W65C02S Microprocessor
class W65C02S:
    def __init__(self, rom: bytes = None, org: int = None) -> None:
        """A CPU on a 64 KB bus. With a ROM image, it's loaded (see load_rom) and the CPU boots from it."""
        self.A = 0x00  # Accumulator A
        self.Y = 0x00  # Index register Y
        self.X = 0x00  # Index register X

        self.PC = 0x0000  # Program counter PC
        self.S = 0xFD  # Stack Pointer S

        # Processor status flags. P is built from them on demand.
        self.N = False  # Negative
        self.V = False  # Overflow
        self.B = False  # BRK command 1 = BRK, 0 = IRQB
        self.D = False  # Decimal mode
        self.I = True   # IRQB disable
        self.Z = False  # Zero
        self.C = False  # Carry

        self.stopped = False  # set by STP; only a reset starts the CPU again

        self.bus = Bus()
        self.STACK_START = 0x0100  # Stack start memory address
        self.STACK_END = 0x01FF  # Stack end memory address

        if rom is not None:
            self.load_rom(rom, org)
        self.reset()

    @property
    def MEMORY(self) -> bytearray:
        """The raw 64 KB. Writing here bypasses ROM protection, like a debugger poke."""
        return self.bus.mem

    @MEMORY.setter
    def MEMORY(self, image) -> None:
        """Replace the whole address space with a RAM image (any ROM mapping is dropped)."""
        self.bus = Bus(image)

    def load_rom(self, data: bytes, org: int = None) -> int:
        """Map a ROM image into the address space, read-only, and return where it starts.

        By default it's loaded at $8000, or lower if it's larger than 32 KB, so a
        full-size image ends at $FFFF and its own reset vector is used. If the image
        doesn't cover the reset vector, the vector is pointed at the image's first
        byte, like a monitor ROM that jumps straight into the program.
        """
        if org is None:
            org = min(DEFAULT_ORG, SIZE - len(data))
        self.bus.load(data, org, rom=True)
        if not (org <= RESET_VECTOR and RESET_VECTOR + 1 < org + len(data)):
            self.bus.mem[RESET_VECTOR] = org & 0xFF
            self.bus.mem[RESET_VECTOR + 1] = org >> 8
        return org

    def reset(self) -> None:
        """The RESB sequence: load PC from the reset vector, disable IRQs, leave decimal mode."""
        self.PC = self.bus.read(RESET_VECTOR) | self.bus.read(RESET_VECTOR + 1) << 8
        self.S = 0xFD
        self.I = True
        self.D = False
        self.stopped = False

    @property
    def P(self) -> int:
        """Processor status register. Bit 5 is unused and always reads 1."""
        return (self.N << 7 | self.V << 6 | 1 << 5 | self.B << 4
                | self.D << 3 | self.I << 2 | self.Z << 1 | self.C)

    @P.setter
    def P(self, val: int) -> None:
        self.N = bool(val & 0x80)
        self.V = bool(val & 0x40)
        self.B = bool(val & 0x10)
        self.D = bool(val & 0x08)
        self.I = bool(val & 0x04)
        self.Z = bool(val & 0x02)
        self.C = bool(val & 0x01)

    def set_nz(self, val: int) -> int:
        """Set N and Z from an 8-bit result, and return the result."""
        self.N = bool(val & 0x80)
        self.Z = val == 0
        return val

    def mem_read(self, addr: int) -> int:
        return self.bus.read(addr)

    def mem_write(self, addr: int, val: int) -> None:
        self.bus.write(addr, val)

    def load(self, loc) -> int:
        """Read the value at a location returned by an addressing mode."""
        if loc is ACC:
            return self.A
        if isinstance(loc, Immediate):
            return loc.value
        return self.mem_read(loc)

    def store(self, loc, val: int) -> None:
        """Write a value to a location returned by an addressing mode."""
        if loc is ACC:
            self.A = val & 0xFF
        elif isinstance(loc, Immediate):
            raise TypeError("can't store to an immediate operand")
        else:
            self.mem_write(loc, val)

    def stk_pull(self) -> int:
        self.S = (self.S + 0x01) & 0xFF  # Increment S (if >255 wrap around to 0)
        return self.mem_read(self.STACK_START + self.S)

    def stk_push(self, val: int) -> None:
        self.mem_write(self.STACK_START + self.S, val)
        self.S = (self.S - 0x01) & 0xFF  # Decrement S (if <0 wrap around to 255)

    def execute(self, opcode: int, operand: bytes = b"") -> None:
        """Execute one instruction that starts at PC.

        `operand` holds the bytes after the opcode. PC is left at the next
        instruction, or wherever the instruction jumped to.
        """
        op = OPCODES[opcode]
        if op.fn is None:
            raise NotImplementedError(f"unimplemented opcode ${opcode:02X} ({op}) at ${self.PC:04X}")
        if len(operand) != op.size - 1:
            raise ValueError(f"{op} takes {op.size - 1} operand byte(s), got {len(operand)} at ${self.PC:04X}")

        self.PC = (self.PC + op.size) & 0xFFFF
        op.fn(self, op.mode.resolve(self, int.from_bytes(bytes(operand), "little")))

    def step(self, trace: bool = False) -> None:
        """Fetch the instruction at PC from the bus and execute it."""
        op = OPCODES[self.mem_read(self.PC)]
        operand = bytes(self.mem_read((self.PC + i) & 0xFFFF) for i in range(1, op.size))
        if trace:
            print(f"{self.PC:04X}  {op.mnemonic}", *(f"{byte:02X}" for byte in operand))
        self.execute(op.opcode, operand)

    def run(self, traps=(), max_steps: int = None, trace: bool = False) -> str:
        """Execute from PC until something stops the CPU, and return what did:

        "STP"        an STP instruction ran (or had run before)
        "BRK"        PC reached a BRK ($00); BRK isn't implemented yet, so it ends the program
        "trap"       PC reached one of the `traps` addresses
        "loop"       an instruction jumped or branched to itself
        "max steps"  `max_steps` instructions ran
        """
        traps, steps = set(traps), 0
        while True:
            if self.stopped:
                return "STP"
            if self.PC in traps:
                return "trap"
            if self.mem_read(self.PC) == 0x00 and OPCODES[0x00].fn is None:
                return "BRK"
            if max_steps is not None and steps >= max_steps:
                return "max steps"
            start = self.PC
            self.step(trace)
            steps += 1
            if self.PC == start and not self.stopped:
                return "loop"

    def execute_from_rom(self) -> str:
        """Run from PC with a trace of every instruction."""
        return self.run(trace=True)

if __name__ == "__main__":
    from cli import w65c02s_interface

    parser = argparse.ArgumentParser("W65C02S Emulator")
    parser.add_argument("--rom", dest="rom", type=str)
    parser.add_argument("--org", dest="org", type=lambda v: int(v, 16),
                        help="hex load address of the ROM (default 8000)")
    parser.add_argument("--trap", dest="traps", type=lambda v: int(v, 16), action="append", default=[],
                        help="hex address to stop at; repeatable")
    parser.add_argument("--labels", dest="labels", type=str)
    _args = parser.parse_args()

    if _args.rom:
        with open(_args.rom, "rb") as _rom_file:
            _rom = _rom_file.read()

        _proc = W65C02S(_rom, _args.org)
        print(f"reset: PC = ${_proc.PC:04X}")
        _reason = _proc.run(traps=_args.traps, trace=True)
        print(f"stopped: {_reason} at ${_proc.PC:04X}")
    else:
        _proc = W65C02S()

    w65c02s_interface(_proc)
