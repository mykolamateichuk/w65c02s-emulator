INSTRUCTION = "TAY"

ADM_I = 0xA8

def i(proc) -> None:
    proc.Y = proc.A

    proc.set_flags(
        "Z" if not bool(proc.Y) else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode() -> None:
    pass
