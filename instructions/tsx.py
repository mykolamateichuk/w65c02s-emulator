INSTRUCTION = "TSX"

ADM_I = 0xBA

def i(proc) -> None:
    proc.X = proc.S
    proc.set_flags(
        "Z" if not bool(proc.X) else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
