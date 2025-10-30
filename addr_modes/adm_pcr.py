import re

ABBR = "PCR"
PATTERN = re.compile(
    r"(\$[0-9a-fA-F]{2}|%[01]{8}|[0-9]{3})"
)


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | tuple | None]:
    if len(operands) == 1 and re.match(PATTERN, operands[0]):
        try:
            offset = int(operands[0], 16)
        except ValueError:
            return False, None
        return True, offset
    return False, None
