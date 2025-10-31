ABBR = "I"
INDIRECT = False
PATTERN = None


def handle_instruction(instruction: str, *operands) -> tuple[bool, int | None]:
    impl_instructions = (
        "NOP",
        "CLC", "SEC", "CLI", "SEI", "CLV", "CLD", "SED",
        "TXA", "TAX", "TYA", "TAY", "INX", "INY", "DEX", "DEY",
        "TXS", "TSX", "PHA", "PLA", "PHP", "PLP"
    )

    if instruction.upper() in impl_instructions and len(operands) == 0:
        return True, None
    return False, None
