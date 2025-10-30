import re

ABBR = "AI"
PATTERN = re.compile(
    r"(\(\$[0-9a-fA-F]{4}\)|\(%[01]{16}\)|\([0-9]{5}\))"
)


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | tuple | None]:
    if len(operands) == 1 and re.match(PATTERN, operands[0]):
        try:
            addr = int(operands[0], 16)
        except ValueError:
            return False, None
        return True, addr
    return False, None
