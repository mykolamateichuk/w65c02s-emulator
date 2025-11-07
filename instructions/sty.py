INSTRUCTION = "STY"

ADM_ZP      = 0x84
ADM_ZPIX    = 0x94
ADM_A       = 0x8C


def zp(proc, zp_addr: int) -> None:
    proc.mem_write(zp_addr, proc.Y)

def zpix(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.X) & 0xFF
    proc.mem_write(eff_addr, proc.Y)

def a(proc, addr: int) -> None:
    proc.mem_write(addr, proc.Y)

def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "ZP":
        zp(proc, operand)
    if adm == "ZPIX":
        zpix(proc, operand)
    if adm == "A":
        a(proc, operand)

def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_ZP:
        zp(proc, args[0])
    if opcode == ADM_ZPIX:
        zpix(proc, args[0])
    if opcode == ADM_A:
        a(proc, (args[1] << 8) + args[0])

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_ZP:     2,
        ADM_ZPIX:   2,
        ADM_A:      3,
    }

    return opcodes.get(opcode)

