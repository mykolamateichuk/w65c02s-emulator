import argparse

from modes import ACC, Immediate
from opcodes import OPCODES

# W65C02S Microprocessor
class W65C02S:
    def __init__(self, rom: bytes = None) -> None:
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

        self.MEMORY = [0x00] * 0x10000  # 64 KB
        self.STACK_START = 0x0100  # Stack start memory address
        self.STACK_END = 0x01FF  # Stack end memory address

        self.ROM = rom

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
        return self.MEMORY[addr]

    def mem_write(self, addr: int, val: int) -> None:
        self.MEMORY[addr] = val & 0xFF

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

    def execute_from_rom(self) -> None:
        while self.PC < len(self.ROM):
            opcode = self.ROM[self.PC]
            if opcode == 0x00:
                return

            op = OPCODES[opcode]
            operand = self.ROM[self.PC + 1:self.PC + op.size]
            print(op.mnemonic, *(f"{byte:02X}" for byte in operand))

            self.execute(opcode, operand)

if __name__ == "__main__":
    from cli import w65c02s_interface

    parser = argparse.ArgumentParser("W65C02S Emulator")
    parser.add_argument("--rom", dest="rom", type=str)
    parser.add_argument("--labels", dest="labels", type=str)
    _args = parser.parse_args()

    with open(_args.rom, "rb") as _rom_file:
        _rom = _rom_file.read()

    _proc = W65C02S(_rom)
    _proc.execute_from_rom()

    w65c02s_interface(_proc)
