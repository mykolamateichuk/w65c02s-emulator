INSTRUCTION = "TYA"

ADM_I = 0x98

def i(proc) -> None:
    proc.A = proc.Y

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
