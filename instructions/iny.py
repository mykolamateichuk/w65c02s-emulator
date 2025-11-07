INSTRUCTION = "INY"

ADM_I = 0xC8

def i(proc) -> None:
    proc.Y = (proc.Y + 0x01) & 0xFF

    proc.set_flags(
        "Z" if not bool(proc.Y) else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )

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
