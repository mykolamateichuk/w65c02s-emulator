INSTRUCTION = "INC"

ADM_ZP      = 0xE6
ADM_ZPIX    = 0xF6
ADM_A       = 0xEE
ADM_AIX     = 0xFE


def zp(proc, zp_addr: int) -> None:
    proc.MEMORY[zp_addr & 0xFF] += 1

    proc.set_flags(
        "Z" if not bool(proc.MEMORY[zp_addr & 0xFF]) else "!Z",
        "N" if bool(proc.MEMORY[zp_addr & 0xFF] & 0b10000000) else "!N"
    )

def zpix(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.X) & 0xFF
    proc.MEMORY[eff_addr] += 1

    proc.set_flags(
        "Z" if not bool(proc.MEMORY[eff_addr]) else "!Z",
        "N" if bool(proc.MEMORY[eff_addr] & 0b10000000) else "!N"
    )

def a(proc, addr: int) -> None:
    proc.MEMORY[addr & 0xFFFF] += 1

    proc.set_flags(
        "Z" if not bool(proc.MEMORY[addr & 0xFFFF]) else "!Z",
        "N" if bool(proc.MEMORY[addr & 0xFFFF] & 0b10000000) else "!N"
    )

def aix(proc, addr: int) -> None:
    eff_addr = (addr + proc.X) & 0xFFFF
    proc.MEMORY[eff_addr] += 1

    proc.set_flags(
        "Z" if not bool(proc.MEMORY[eff_addr]) else "!Z",
        "N" if bool(proc.MEMORY[eff_addr] & 0b10000000) else "!N"
    )


def execute_adm(adm: str, proc = None, operand: int = None) -> None:
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
