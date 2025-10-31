import addr_modes as adm

def handle_adm(is_indirect: bool, instruction: str, *args) -> tuple[str, tuple | None] | None:
    for _adm in adm.__all__:
        if len(args) > 0:
            handle, operands = getattr(adm, _adm).handle_instruction(instruction, *args)
        else:
            handle, operands = getattr(adm, _adm).handle_instruction(instruction)

        if handle and getattr(adm, _adm).INDIRECT == is_indirect:
            return getattr(adm, _adm).ABBR, operands if operands else None
    return None
