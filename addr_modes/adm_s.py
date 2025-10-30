ABBR = "S"
PATTERN = None


def handle_instruction(instruction: str, *operands) -> tuple[bool, tuple | None]:
    stk_instructions = (
        ...
    )

    if instruction.upper() in stk_instructions and len(operands) == 0:
        return True, None
    return False, None