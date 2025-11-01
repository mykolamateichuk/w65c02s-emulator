INSTRUCTION = "LDA"

ADM_IA      = 0xA9
ADM_ZP      = 0xA5
ADM_ZPIX    = 0xB5
ADM_A       = 0xAD
ADM_AIX     = 0xBD
ADM_AIY     = 0xB9
ADM_ZPII    = 0xA1
ADM_ZPIIY   = 0xB1


def ia(proc, value: int) -> None:
    proc.A = value & 0xFF

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def zp(proc, zp_addr: int) -> None:
    proc.A = proc.MEMORY[zp_addr & 0xFF]

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def zpix(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.X) & 0xFF
    proc.A = proc.MEMORY[eff_addr]

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def a(proc, addr: int) -> None:
    proc.A = proc.MEMORY[addr & 0xFFFF]

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def aix(proc, addr: int) -> None:
    eff_addr = (addr + proc.X) & 0xFFFF
    proc.A = proc.MEMORY[eff_addr]

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def aiy(proc, addr: int) -> None:
    eff_addr = (addr + proc.Y) & 0xFFFF
    proc.A = proc.MEMORY[eff_addr]

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def zpii(proc, zp_addr: int) -> None:
    ind_addr = (zp_addr + proc.X) & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])
    proc.A = proc.MEMORY[eff_addr & 0xFFFF]

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )

def zpiiy(proc, zp_addr: int) -> None:
    ind_addr = zp_addr & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])
    proc.A = proc.MEMORY[(eff_addr + proc.Y) & 0xFFFF]

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
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
    if adm == "AIY":
        aiy(proc, operand)
    if adm == "ZPII":
        zpii(proc, operand)
    if adm == "ZPIIY":
        zpiiy(proc, operand)

def execute_opcode() -> None:
    pass
