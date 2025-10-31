ABBR = "AA"
INDIRECT = False
PATTERN = None


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | None]:
    if len(operands) == 1 and operands[0].upper() == "A":
        return True, None
    return False, None
