INSTRUCTION = "CLC"

ADM_I = 0x18

def i(proc) -> None:
    proc.set_flags("!C")

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "I":
        i(proc)

def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_I:
        i(proc)

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_I: 1,
    }

    return opcodes.get(opcode)
