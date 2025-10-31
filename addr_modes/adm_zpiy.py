import re

from addr_modes.utils import parse_number

ABBR = "ZPIY"
INDIRECT = False
PATTERN = re.compile(
    r"(\$[0-9a-fA-F]{2}|%[01]{8}|[0-9]{3})"
)


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | None]:
    if len(operands) == 2 and re.match(PATTERN, operands[0]) and operands[1].upper() == "Y":
        try:
            addr = parse_number(operands[0])
        except ValueError:
            return False, None
        return True, addr
    return False, None
