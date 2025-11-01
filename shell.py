from w65c02s import W65C02S

from addr_modes.handler import handle_adm
import instructions as instr

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


def w65c02s_interface(proc: W65C02S) -> None:
    running = True
    while running:
        tokens = input("> ").split(maxsplit=1)

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

        is_opcode = False
        try:
            instruction = int(instruction, 16)
            is_opcode = True
        except ValueError:
            if instruction.upper() in proc.INSTRUCTION_SET.keys():
                is_opcode = True

        if is_opcode:
            is_indirect = False
            if len(args) != 0:
                is_indirect = "(" in args[0]

                if "(" in args[0]:
                    args[0] = args[0].split("(")[1]
                if ")" in args[0]:
                    args[0] = args[0].split(")")[0]
                if len(args) == 2:
                    if ")" in args[1]:
                        args[1] = args[1].split(")")[0]

                args[0] = args[0].strip()
                if len(args) == 2:
                    args[1] = args[1].strip()

            if isinstance(instruction, int):
                if instruction in proc.OPCODES:
                    # TODO: implement execute_opcode for all available instructions
                    getattr(instr, proc.OPCODES[instruction].lower()).execute_opcode(proc, *args)
                continue

            adm, operand = handle_adm(is_indirect, instruction, *args)
            getattr(instr, instruction.lower()).execute_adm(
                adm=adm, proc=proc, operand=operand
            )

        if instruction == "!exit":
            running = False

        elif instruction == "!flag":
            if len(args) == 0:
                draw_flags(proc.P)
                continue

            flags = {
                "C": None,
                "Z": None,
                "I": None,
                "D": None,
                "B": None,
                "V": None,
                "N": None
            }

            for arg in args:
                if "C" in arg or "c" in arg:
                    if "!" in arg:
                        flags["C"] = False
                    else:
                        flags["C"] = True
                if "Z" in arg or "z" in arg:
                    if "!" in arg:
                        flags["Z"] = False
                    else:
                        flags["Z"] = True
                if "I" in arg or "i" in arg:
                    if "!" in arg:
                        flags["I"] = False
                    else:
                        flags["I"] = True
                if "D" in arg or "d" in arg:
                    if "!" in arg:
                        flags["D"] = False
                    else:
                        flags["D"] = True
                if "B" in arg or "b" in arg:
                    if "!" in arg:
                        flags["B"] = False
                    else:
                        flags["B"] = True
                if "V" in arg or "v" in arg:
                    if "!" in arg:
                        flags["V"] = False
                    else:
                        flags["V"] = True
                if "N" in arg or "n" in arg:
                    if "!" in arg:
                        flags["N"] = False
                    else:
                        flags["N"] = True

            proc.set_flags(
                "C" if flags["C"] else "!C" if flags["C"] is False else None,
                "Z" if flags["Z"] else "!Z" if flags["Z"] is False else None,
                "I" if flags["I"] else "!I" if flags["I"] is False else None,
                "D" if flags["D"] else "!D" if flags["D"] is False else None,
                "B" if flags["B"] else "!B" if flags["B"] is False else None,
                "V" if flags["V"] else "!V" if flags["V"] is False else None,
                "N" if flags["N"] else "!N" if flags["N"] is False else None,
            )

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

                num_rows = (addr2 - addr1) // 16

                if num_rows == 0:
                    values = " ".join([f"{val:02X}" for val in proc.MEMORY[addr1:addr2 + 1]])
                    print(f"{addr1:04X}-{addr2:04X}: {values}")
                    continue

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


if __name__ == "__main__":
    _proc = W65C02S()

    w65c02s_interface(_proc)