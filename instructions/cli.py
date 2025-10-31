INSTRUCTION = "CLI"

ADM_I = 0x58

def i(proc) -> None:
    proc.set_flags("!I")

def execute_adm(adm: str, proc, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
