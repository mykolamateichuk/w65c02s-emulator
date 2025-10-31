INSTRUCTION = "CLD"

ADM_I = 0xD8

def i(proc) -> None:
    proc.set_flags("!D")

def execute_adm(adm: str, proc, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
