INSTRUCTION = "INC"

ADM_ZP      = 0xE6
ADM_ZPIX    = 0xF6
ADM_A       = 0xEE
ADM_AIX     = 0xFE


def zp(proc, zp_addr: int) -> None:
    zp_addr = zp_addr & 0xFF
    proc.mem_write(zp_addr, proc.mem_read(zp_addr) + 1)

    proc.set_flags(
        "Z" if not bool(proc.mem_read(zp_addr)) else "!Z",
        "N" if bool(proc.mem_read(zp_addr) & 0b10000000) else "!N"
    )

def zpix(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.X) & 0xFF
    proc.mem_write(eff_addr, proc.mem_read(eff_addr) + 1)

    proc.set_flags(
        "Z" if not bool(proc.mem_read(eff_addr)) else "!Z",
        "N" if bool(proc.mem_read(eff_addr) & 0b10000000) else "!N"
    )

def a(proc, addr: int) -> None:
    addr = addr & 0xFFFF
    proc.mem_write(addr, proc.mem_read(addr) + 1)

    proc.set_flags(
        "Z" if not bool(proc.mem_read(addr)) else "!Z",
        "N" if bool(proc.mem_read(addr) & 0b10000000) else "!N"
    )

def aix(proc, addr: int) -> None:
    eff_addr = (addr + proc.X) & 0xFFFF
    proc.mem_write(eff_addr, proc.mem_read(eff_addr) + 1)

    proc.set_flags(
        "Z" if not bool(proc.mem_read(eff_addr)) else "!Z",
        "N" if bool(proc.mem_read(eff_addr) & 0b10000000) else "!N"
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
