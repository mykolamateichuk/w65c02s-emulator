INSTRUCTION = "SED"

ADM_I = 0xF8

def i(proc) -> None:
    proc.set_flags("D")

def execute_adm(adm: str, proc) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
