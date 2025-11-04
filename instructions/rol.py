INSTRUCTION = "ROL"

ADM_AA      = 0x2A
ADM_ZP      = 0x26
ADM_ZPIX    = 0x36
ADM_A       = 0x2E
ADM_AIX     = 0x3E


def aa(proc) -> None:
    carry = (proc.A >> 7) & 1
    proc.A = (proc.A << 1) & 0xFF
    proc.A |= proc.P & 0b00000001

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zp(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read(zp_addr & 0xFF)

    carry = (mem_val >> 7) & 1
    mem_val = (mem_val << 1) & 0xFF
    mem_val |= proc.P & 0b00000001

    proc.mem_write(zp_addr & 0xFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(mem_val) else "!Z",
        "N" if bool(mem_val & 0b10000000) else "!N"
    )


def zpix(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read((zp_addr + proc.X) & 0xFF)

    carry = (mem_val >> 7) & 1
    mem_val = (mem_val << 1) & 0xFF
    mem_val |= proc.P & 0b00000001

    proc.mem_write((zp_addr + proc.X) & 0xFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(mem_val) else "!Z",
        "N" if bool(mem_val & 0b10000000) else "!N"
    )


def a(proc, addr: int) -> None:
    mem_val = proc.mem_read(addr & 0xFFFF)

    carry = (mem_val >> 7) & 1
    mem_val = (mem_val << 1) & 0xFF
    mem_val |= proc.P & 0b00000001

    proc.mem_write(addr & 0xFFFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(mem_val) else "!Z",
        "N" if bool(mem_val & 0b10000000) else "!N"
    )


def aix(proc, addr: int) -> None:
    mem_val = proc.mem_read((addr + proc.X) & 0xFFFF)

    carry = (mem_val >> 7) & 1
    mem_val = (mem_val << 1) & 0xFF
    mem_val |= proc.P & 0b00000001

    proc.mem_write((addr + proc.X) & 0xFFFF, mem_val)

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if not bool(mem_val) else "!Z",
        "N" if bool(mem_val & 0b10000000) else "!N"
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


def execute_opcode() -> None:
    pass
