ABBR = "I"
PATTERN = None


def handle_instruction(instruction: str, *operands) -> tuple[bool, tuple | None]:
    impl_instructions = (
        "NOP",
    )

    if instruction.upper() in impl_instructions and len(operands) == 0:
        return True, None

    return False, None
