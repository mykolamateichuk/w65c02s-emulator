INSTRUCTION = "STA"

ADM_ZP      = 0x85
ADM_ZPIX    = 0x95
ADM_A       = 0x8D
ADM_AIX     = 0x9D
ADM_AIY     = 0x99
ADM_ZPII    = 0x81
ADM_ZPIIY   = 0x91


def zp(proc, zp_addr: int) -> None:
    proc.mem_write(zp_addr, proc.A)

def zpix(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.X) & 0xFF
    proc.mem_write(eff_addr, proc.A)

def a(proc, addr: int) -> None:
    proc.mem_write(addr, proc.A)

def aix(proc, addr: int) -> None:
    eff_addr = (addr + proc.X) & 0xFFFF
    proc.mem_write(eff_addr, proc.A)

def aiy(proc, addr: int) -> None:
    eff_addr = (addr + proc.Y) & 0xFFFF
    proc.mem_write(eff_addr, proc.A)

def zpii(proc, zp_addr: int) -> None:
    ind_addr = (zp_addr + proc.X) & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])

    proc.mem_write(eff_addr, proc.A)

def zpiiy(proc, zp_addr: int) -> None:
    ind_addr = zp_addr & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])

    proc.mem_write((eff_addr + proc.Y) & 0xFFFF, proc.A)

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
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

def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_ZP:
        zp(proc, args[0])
    if opcode == ADM_ZPIX:
        zpix(proc, args[0])
    if opcode == ADM_A:
        a(proc, (args[1] << 8) + args[0])
    if opcode == ADM_AIX:
        aix(proc, (args[1] << 8) + args[0])
    if opcode == ADM_AIY:
        aiy(proc, (args[1] << 8) + args[0])
    if opcode == ADM_ZPII:
        zpii(proc, args[0])
    if opcode == ADM_ZPIIY:
        zpiiy(proc, args[0])

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_ZP:     2,
        ADM_ZPIX:   2,
        ADM_A:      3,
        ADM_AIX:    3,
        ADM_AIY:    3,
        ADM_ZPII:   2,
        ADM_ZPIIY:  2,
    }

    return opcodes.get(opcode)
