INSTRUCTION = "PHA"

ADM_I = 0x48

def i(proc) -> None:
    proc.stk_push(proc.A)

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
