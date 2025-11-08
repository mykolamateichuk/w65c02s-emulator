import re
import argparse

from w65c02s import W65C02S
from addr_modes.handler import handle_adm
import instructions as instr


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
            labels[lines[i]] = f"${i:04X}"
            lines[i] = ""

    # Remove empty lines after removing labels
    empty_lines = lines.count("")
    for i in range(0, empty_lines):
        lines.remove("")
    
    # Replace labels with addrs
    for i, line in enumerate(lines):
        for label, addr in labels.items():
            if label in line:
                lines[i] = lines[i].replace(label, str(addr))

    return lines, labels


def asm_to_binary(lines: list, bin_file: str) -> None:
    bin_program = []

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

        if "_" in instruction:
            instruction = instruction[:len(instruction) - 2]

        adm, operand = handle_adm(is_indirect, instruction, *args)
        opcode = getattr(getattr(instr, instruction.lower()), f"ADM_{adm}")

        bin_program.append(opcode.to_bytes(1, "big"))
        if operand:
            if operand > 255:
                bin_program.append(operand.to_bytes(2, "little"))
            else:
                bin_program.append(operand.to_bytes(1, "big"))
    
    with open(bin_file, "wb") as file:
        file.write(b"".join(bin_program))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="W65C02S Emulator")
    parser.add_argument("-s", dest="asm_file", type=str)
    parser.add_argument("-r", dest="rom_file", type=str)

    _args = parser.parse_args()

    _proc = W65C02S()

    with open(_args.asm_file, "r") as file:
        _lines, _labels = preprocess(file.readlines())
        asm_to_binary(_proc, _lines, _args.rom_file)
