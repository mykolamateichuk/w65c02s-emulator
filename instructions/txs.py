INSTRUCTION = "TXS"

ADM_I = 0x9A

def i(proc) -> None:
    proc.S = proc.X

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
