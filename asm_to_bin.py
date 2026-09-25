import re
import argparse

from addr_modes.handler import handle_adm
from opcodes import lookup


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


def encode(line: str) -> bytes:
    """Assemble one instruction into machine code."""
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

    adm = handle_adm(is_indirect, instruction, *args)
    if adm is None:
        raise ValueError(f"can't assemble {line.strip()!r}: unknown instruction or operand")
    op = lookup(instruction, adm[0])

    operand = adm[1] or 0
    width = op.size - 1
    if operand >= 1 << (8 * width):
        raise ValueError(f"can't assemble {line.strip()!r}: operand doesn't fit in {width} byte(s)")

    return bytes([op.opcode]) + operand.to_bytes(width, "little")


def asm_to_binary(lines: list, bin_file: str) -> None:
    with open(bin_file, "wb") as file:
        file.write(b"".join(encode(line) for line in lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="W65C02S Emulator")
    parser.add_argument("-s", dest="asm_file", type=str)
    parser.add_argument("-r", dest="rom_file", type=str)

    _args = parser.parse_args()

    with open(_args.asm_file, "r") as file:
        _lines, _labels = preprocess(file.readlines())
        asm_to_binary(_lines, _args.rom_file)
