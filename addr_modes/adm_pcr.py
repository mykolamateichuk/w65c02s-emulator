import re

from addr_modes.utils import parse_number

ABBR = "PCR"
INDIRECT = False
PATTERN = re.compile(
    r"(\$[0-9a-fA-F]{2}|%[01]{8}|[0-9]{3})"
)


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | None]:
    branch_instructions = (
        "BPL", "BMI", "BVC", "BVS", "BCC", "BCS", "BNE", "BEQ"
    )

    if len(operands) == 1 and re.match(PATTERN, operands[0]) and instruction.upper() in branch_instructions:
        try:
            offset = parse_number(operands[0])
        except ValueError:
            return False, None
        return True, offset
    return False, None
