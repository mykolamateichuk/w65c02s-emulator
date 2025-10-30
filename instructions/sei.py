INSTRUCTION = "SEI"

ADM_I = 0x78

def i(proc) -> None:
    proc.set_flags("I")

def execute_adm(adm: str, proc) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
