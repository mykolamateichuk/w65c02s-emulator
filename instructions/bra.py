INSTRUCTION = "BRA"

ADM_PCR = 0x80


def pcr(proc, offset: int) -> None:
    if offset & 0b10000000:
        offset -= 0b100000000

    proc.PC += offset


def execute_adm(adm: str, proc=None, operand: int = None) -> None:
    if adm == "PCR":
        pcr(proc, operand)


def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_PCR:
        pcr(proc, args[0])


def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_PCR: 2,
    }

    return opcodes.get(opcode)
