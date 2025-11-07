INSTRUCTION = "ROR"

ADM_AA      = 0x6A
ADM_ZP      = 0x66
ADM_ZPIX    = 0x76
ADM_A       = 0x6E
ADM_AIX     = 0x7E


def aa(proc) -> None:
    carry = proc.A & 0b00000001
    proc.A = (proc.A >> 1) & 0xFF
    proc.A |= (proc.P & 0b00000001) << 7

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zp(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read(zp_addr & 0xFF)

    carry = mem_val & 0b00000001
    mem_val = (mem_val >> 1) & 0xFF
    mem_val |= (proc.P & 0b00000001) << 7

    proc.mem_write(zp_addr & 0xFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpix(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read((zp_addr + proc.X) & 0xFF)

    carry = mem_val & 0b00000001
    mem_val = (mem_val >> 1) & 0xFF
    mem_val |= (proc.P & 0b00000001) << 7

    proc.mem_write((zp_addr + proc.X) & 0xFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def a(proc, addr: int) -> None:
    mem_val = proc.mem_read(addr & 0xFFFF)

    carry = mem_val & 0b00000001
    mem_val = (mem_val >> 1) & 0xFF
    mem_val |= (proc.P & 0b00000001) << 7

    proc.mem_write(addr & 0xFFFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def aix(proc, addr: int) -> None:
    mem_val = proc.mem_read((addr + proc.X) & 0xFFFF)

    carry = mem_val & 0b00000001
    mem_val = (mem_val >> 1) & 0xFF
    mem_val |= (proc.P & 0b00000001) << 7

    proc.mem_write((addr + proc.X) & 0xFFFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def execute_adm(adm: str, proc=None, operand: int = None) -> None:
    if adm == "AA":
        aa(proc)
    if adm == "ZP":
        zp(proc, operand)
    if adm == "ZPIX":
        zpix(proc, operand)
    if adm == "A":
        a(proc, operand)
    if adm == "AIX":
        aix(proc, operand)


def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_AA:
        aa(proc)
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
        ADM_AA:     1,
        ADM_ZP:     2,
        ADM_ZPIX:   2,
        ADM_A:      3,
        ADM_AIX:    3,
    }

    return opcodes.get(opcode)
