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

def execute_opcode() -> None:
    pass
