INSTRUCTION = "STX"

ADM_ZP      = 0x86
ADM_ZPIY    = 0x96
ADM_A       = 0x8E


def zp(proc, zp_addr: int) -> None:
    proc.mem_write(zp_addr, proc.X)

def zpiy(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.Y) & 0xFF
    proc.mem_write(eff_addr, proc.X)

def a(proc, addr: int) -> None:
    proc.mem_write(addr, proc.X)

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "ZP":
        zp(proc, operand)
    if adm == "ZPIY":
        zpiy(proc, operand)
    if adm == "A":
        a(proc, operand)

def execute_opcode() -> None:
    pass
