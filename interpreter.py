import argparse

import re

from w65c02s import W65C02S
from addr_modes.handler import handle_adm
import instructions as instr

from cli import draw_flags, draw_registers, print_memory


def preprocess(lines: list) -> tuple[list, dict]:
    labels = {}

    # Strip lines of any whitespace
    for i, line in enumerate(lines):
        lines[i] = line.strip()

    # Remove comments
    for i, line in enumerate(lines):
        if ";" in line:
            if line.find(";") == 0:
                lines[i] = ""
            lines[i] = line[:line.find(";")]

    # Remove empty lines
    empty_lines = lines.count("")
    for i in range(0, empty_lines):
        lines.remove("")

    # Parse and remove labels
    for i, line in enumerate(lines):
        if re.match(re.compile(r"[a-zA-Z][a-zA-Z0-9]*:"), line):
            lines[i] = line[:line.find(":")].strip()
            labels[lines[i]] = i
            lines[i] = ""

    # Remove empty lines after removing labels
    empty_lines = lines.count("")
    for i in range(0, empty_lines):
        lines.remove("")

    return lines, labels


def interpret(proc: W65C02S, lines: list, labels: dict) -> None:
    for line in lines:
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

        is_opcode = False
        try:
            opcode = int(instruction, 16)
            if opcode <= 0xFF:
                instruction = opcode

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

            if "_" in instruction:
                instruction = instruction[:len(instruction) - 2]

            adm, operand = handle_adm(is_indirect, instruction, *args)
            getattr(instr, instruction.lower()).execute_adm(
                adm=adm, proc=proc, operand=operand
            )

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="W65C02S Emulator")
    
    parser.add_argument(
        "-s",
        dest="file_path",
        type=str,
        required=True
    )

    _args = parser.parse_args()

    _proc = W65C02S()

    # TODO: add reading from binary file

    with open(_args.file_path, "r") as file:
        _lines, _labels = preprocess(file.readlines())
        interpret(_proc, _lines, _labels)

    # TODO: how to display memory changes?
