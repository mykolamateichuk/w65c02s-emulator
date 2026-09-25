import re

from asm_to_bin import encode
from opcodes import MNEMONICS

RAW_BYTES = re.compile(r"\s*[0-9a-fA-F]{2}(\s+[0-9a-fA-F]{2})*\s*")  # e.g. "A9 05"

def draw_flags(flags: int) -> None:
    c = int(bool(flags & 0b00000001))
    z = int(bool(flags & 0b00000010))
    i = int(bool(flags & 0b00000100))
    d = int(bool(flags & 0b00001000))
    b = int(bool(flags & 0b00010000))
    v = int(bool(flags & 0b01000000))
    n = int(bool(flags & 0b10000000))

    print("=============================")
    print("| N | V | B | D | I | Z | C |")
    print("=============================")
    print(f"| {n} | {v} | {b} | {d} | {i} | {z} | {c} |")
    print("=============================")


def draw_registers(a: int, x: int, y: int) -> None:
    a = f"{a:02X}"
    x = f"{x:02X}"
    y = f"{y:02X}"

    print("================")
    print("| A  | X  | Y  |")
    print("================")
    print(f"| {a} | {x} | {y} |")
    print("================")


def print_memory(proc: "W65C02S", addr1: int, addr2: int) -> None:
    num_rows = (addr2 - addr1) // 16

    if num_rows == 0:
        values = " ".join([f"{val:02X}" for val in proc.MEMORY[addr1:addr2 + 1]])
        print(f"{addr1:04X}-{addr2:04X}: {values}")

    if num_rows >= 1:
        row_end_addr = addr1 - 1

        addr1_offset = addr1 & 0x000F
        if addr1_offset != 0:
            row_end_addr = addr1 + (0x000F - addr1_offset)

            spaces = " ".join(["  " for _ in range(addr1_offset)])
            values = " ".join([f"{val:02X}" for val in proc.MEMORY[addr1:row_end_addr + 1]])

            print(f"{addr1:04X}-{row_end_addr:04X}: {spaces} {values}")

        row_start_addr = row_end_addr + 0x0001
        for _ in range(num_rows + 1):
            row_end_addr = row_start_addr + 0x000F

            values = " ".join([f"{val:02X}" for val in proc.MEMORY[row_start_addr:row_end_addr + 1]])
            print(f"{row_start_addr:04X}-{row_end_addr:04X}: {values}")

            row_start_addr = row_end_addr + 0x0001

        addr2_offset = addr2 & 0x000F
        if addr2_offset != 0x000F:
            row_start_addr = addr2 - addr2_offset

            spaces = " ".join(["  " for _ in range(0x000F - addr2_offset)])
            values = " ".join([f"{val:02X}" for val in proc.MEMORY[row_start_addr:addr2 + 1]])

            print(f"{row_start_addr:04X}-{addr2:04X}: {values} {spaces}")


def run_instruction(proc: "W65C02S", code: bytes) -> None:
    """Execute one instruction given as machine code. PC only changes if the instruction jumps."""
    start = proc.PC
    proc.execute(code[0], code[1:])
    if proc.PC == (start + len(code)) & 0xFFFF:
        proc.PC = start


def w65c02s_interface(proc: "W65C02S") -> None:
    running = True
    while running:
        line = input("> ")
        tokens = line.split(maxsplit=1)

        instruction = tokens[0]
        args = []

        if len(tokens) == 2:
            args = tokens[1]

            if "," in args:
                args = args.split(",")
            elif " " in args:
                args = args.split()

            if not isinstance(args, list):
                args = [args]

        if RAW_BYTES.fullmatch(line) or instruction.upper() in MNEMONICS:
            try:
                code = bytes.fromhex(line) if RAW_BYTES.fullmatch(line) else encode(line)
                run_instruction(proc, code)
            except (ValueError, NotImplementedError) as err:
                print(f"error: {err}")
            continue

        if instruction == "!exit":
            running = False

        elif instruction == "!flag":
            if len(args) == 0:
                draw_flags(proc.P)
                continue

            for arg in args:
                for name in "CZIDBVN":
                    if name in arg.upper():
                        setattr(proc, name, "!" not in arg)

        elif instruction == "!reg":
            if len(args) == 0:
                draw_registers(a=proc.A, x=proc.X, y=proc.Y)
                continue

            for arg in args:
                if "=" not in arg:
                    continue

                reg, val = arg.split("=")
                if reg in ["A", "a"]:
                    proc.A = int(val, 16)
                if reg in ["X", "x"]:
                    proc.X = int(val, 16)
                if reg in ["Y", "y"]:
                    proc.Y = int(val, 16)

        elif instruction == "!mem":
            if len(args) == 1:
                try:
                    addr = int(args[0], 16)
                    print(f"{addr:04X}: {proc.MEMORY[addr]:02X}")
                    continue
                except ValueError:
                    if "=" not in args[0]:
                        continue

                    addr, val = args[0].split("=")

                    try:
                        addr = int(addr, 16)
                        val = int(val, 16)
                    except ValueError:
                        continue

                    proc.mem_write(addr, val)
                    continue

            if len(args) == 2:
                try:
                    addr1 = int(args[0], 16)
                    addr2 = int(args[1], 16)
                except ValueError:
                    continue

                print_memory(proc, addr1, addr2)

        elif instruction == "!stk":
            STACK = proc.MEMORY[proc.STACK_START:proc.STACK_END + 1]

            if len(args) == 1:
                if args[0] == "pull":
                    val = proc.stk_pull()
                    print(f"{val:02X}")
                    continue
                if args[0] == "ptr":
                    print(f"{proc.S:02X}")
                    continue

                try:
                    addr = int(args[0], 16)
                    print(f"{addr:02X}: {STACK[addr]:02X}")
                    continue
                except ValueError:
                    if args[0][0] == "/":
                        addr = int(args[0][1:], 16)
                        print(f"{(0x0100 + addr):04X}: {proc.MEMORY[0x0100 + addr]:02X}")
                        continue

            if len(args) == 2:
                if args[0] == "push":
                    try:
                        val = int(args[1], 16)
                    except ValueError:
                        continue

                    proc.stk_push(val)

        elif instruction == "!flush":
            allowed_fields = {
                "A": 0x00,
                "X": 0x00,
                "Y": 0x00,
                "PC": 0x0000,
                "S": 0xFD,
                "P": 0b00100100,
                "MEMORY": [0x00] * 0x10000
            }

            if len(args) == 0:
                proc.A = 0x00
                proc.Y = 0x00
                proc.X = 0x00

                proc.PC = 0x0000
                proc.S = 0xFD
                proc.P = 0b00100100

                proc.MEMORY = [0x00] * 0x10000
                continue

            for arg in args:
                if arg.upper() in allowed_fields.keys():
                    proc.__setattr__(arg.upper(), allowed_fields[arg.upper()])
