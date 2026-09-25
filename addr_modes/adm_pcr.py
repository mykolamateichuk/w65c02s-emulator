import re

from addr_modes.utils import parse_number

ABBR = "PCR"
INDIRECT = False
PATTERN = re.compile(
    r"(\$[0-9a-fA-F]{2}|%[01]{8}|[0-9]{3})"
)


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | None]:
    if len(operands) == 1 and re.match(PATTERN, operands[0]):
        try:
            offset = parse_number(operands[0])
        except ValueError:
            return False, None
        return True, offset
    return False, None
