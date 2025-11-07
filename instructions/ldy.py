INSTRUCTION = "LDY"

ADM_IA      = 0xA0
ADM_ZP      = 0xA4
ADM_ZPIX    = 0xB4
ADM_A       = 0xAC
ADM_AIX     = 0xBC


def ia(proc, value: int) -> None:
    proc.Y = value & 0xFF

    proc.set_flags(
        "Z" if not bool(proc.Y) else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )

def zp(proc, zp_addr: int) -> None:
    proc.Y = proc.MEMORY[zp_addr & 0xFF]

    proc.set_flags(
        "Z" if not bool(proc.Y) else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )

def zpix(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.X) & 0xFF
    proc.Y = proc.MEMORY[eff_addr]

    proc.set_flags(
        "Z" if not bool(proc.Y) else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )

def a(proc, addr: int) -> None:
    proc.Y = proc.MEMORY[addr & 0xFFFF]

    proc.set_flags(
        "Z" if not bool(proc.Y) else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )

def aix(proc, addr: int) -> None:
    eff_addr = (addr + proc.X) & 0xFFFF
    proc.Y = proc.MEMORY[eff_addr]

    proc.set_flags(
        "Z" if not bool(proc.Y) else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )


def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "IA":
        ia(proc, operand)
    if adm == "ZP":
        zp(proc, operand)
    if adm == "ZPIX":
        zpix(proc, operand)
    if adm == "A":
        a(proc, operand)
    if adm == "AIX":
        aix(proc, operand)

def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_IA:
        ia(proc, args[0])
    if opcode == ADM_ZP:
        zp(proc, args[0])
    if opcode == ADM_ZPIX:
        zpix(proc, args[0])
    if opcode == ADM_A:
        a(proc, (args[1] << 8) + args[0])
    if opcode == ADM_AIX:
        aix(proc, (args[1] << 8) + args[0])

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_IA:     2,
        ADM_ZP:     2,
        ADM_ZPIX:   2,
        ADM_A:      3,
        ADM_AIX:    3,
    }

    return opcodes.get(opcode)
