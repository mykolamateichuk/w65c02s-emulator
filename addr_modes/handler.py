import addr_modes as adm
from opcodes import lookup

def handle_adm(is_indirect: bool, instruction: str, *args) -> tuple[str, int | None] | None:
    """Return the first mode whose syntax matches the operands and that the opcode table allows for `instruction`."""
    for _adm in adm.__all__:
        module = getattr(adm, _adm)
        handle, operand = module.handle_instruction(instruction, *args)

        if handle and module.INDIRECT == is_indirect and lookup(instruction, module.ABBR):
            return module.ABBR, operand
    return None
