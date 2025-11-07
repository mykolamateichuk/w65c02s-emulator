INSTRUCTION = "PLP"

ADM_I = 0x28

def i(proc) -> None:
    proc.P = proc.stk_pull()

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_I: 1,
    }

    return opcodes.get(opcode)
