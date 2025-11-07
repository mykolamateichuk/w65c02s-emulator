INSTRUCTION = "SEC"

ADM_I = 0x38

def i(proc) -> None:
    proc.set_flags("C")

def execute_adm(adm: str, proc, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_I: 1,
    }

    return opcodes.get(opcode)
