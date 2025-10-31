ABBR = "S"
INDIRECT = False
PATTERN = None


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | None]:
    stk_instructions = (
        "TXS", "TSX", "PHA", "PLA", "PHP", "PLP"
    )

    if instruction.upper() in stk_instructions and len(operands) == 0:
        return True, None
    return False, None