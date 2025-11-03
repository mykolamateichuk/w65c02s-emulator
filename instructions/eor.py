INSTRUCTION = "EOR"

ADM_IA      = 0x49
ADM_ZP      = 0x45
ADM_ZPIX    = 0x55
ADM_A       = 0x4D
ADM_AIX     = 0x5D
ADM_AIY     = 0x59
ADM_ZPII    = 0x41
ADM_ZPIIY   = 0x51


def ia(proc, value: int) -> None:
    proc.A ^= value & 0xFF

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zp(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read(zp_addr & 0xFF)

    proc.A ^= mem_val

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpix(proc, zp_addr: int) -> None:
    val = proc.mem_read((zp_addr + proc.X) & 0xFF)

    proc.A ^= val

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def a(proc, addr: int) -> None:
    val = proc.mem_read(addr & 0xFFFF)

    proc.A ^= val

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def aix(proc, addr: int) -> None:
    val = proc.mem_read((addr + proc.X) & 0xFFFF)

    proc.A ^= val

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def aiy(proc, addr: int) -> None:
    val = proc.mem_read((addr + proc.Y) & 0xFFFF)

    proc.A ^= val

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpii(proc, zp_addr: int) -> None:
    ind_addr = (zp_addr + proc.X) & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])
    val = proc.mem_read(eff_addr & 0xFFFF)

    proc.A ^= val

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpiiy(proc, zp_addr: int) -> None:
    ind_addr = zp_addr & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])
    val = proc.mem_read((eff_addr + proc.Y) & 0xFFFF)

    proc.A ^= val

    proc.set_flags(
        "Z" if not bool(proc.A) else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def execute_adm(adm: str, proc=None, operand: int = None) -> None:
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
