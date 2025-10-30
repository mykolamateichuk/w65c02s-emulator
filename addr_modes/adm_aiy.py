import re

ABBR = "AIY"
PATTERN = re.compile(
    r"(\$[0-9a-fA-F]{4}|%[01]{16}|[0-9]{5})"
)


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | tuple | None]:
    if len(operands) == 2 and re.match(PATTERN, operands[0]) and operands[1].upper() == "Y":
        try:
            addr = int(operands[0], 16)
        except ValueError:
            return False, None
        return True, addr
    return False, None
