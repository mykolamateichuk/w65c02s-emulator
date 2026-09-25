ABBR = "I"
INDIRECT = False
PATTERN = None


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | None]:
    if len(operands) == 0:
        return True, None
    return False, None
