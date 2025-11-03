INSTRUCTION = "SBC"

ADM_IA      = 0xE9
ADM_ZP      = 0xE5
ADM_ZPIX    = 0xF5
ADM_A       = 0xED
ADM_AIX     = 0xFD
ADM_AIY     = 0xF9
ADM_ZPII    = 0xE1
ADM_ZPIIY   = 0xF1


def _check_overflow(proc, a: int, b: int, result: int) -> bool:
    a_s = proc.signed_byte(a)
    b_s = proc.signed_byte(b)
    res = proc.signed_byte(result)

    return (a_s > 0 and b_s > 0 and res < 0) or (a_s < 0 and b_s < 0 and res > 0)


def ia(proc, value: int) -> None:
    carry = proc.P & 0x00000001

    result = proc.A - value - (1 - carry)

    overflow = _check_overflow(proc, proc.A, value, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zp(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read(zp_addr & 0xFF)
    carry = proc.P & 0x00000001

    result = proc.A - mem_val - (1 - carry)

    overflow = _check_overflow(proc, proc.A, mem_val, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpix(proc, zp_addr: int) -> None:
    val = proc.mem_read((zp_addr + proc.X) & 0xFF)
    carry = proc.P & 0x00000001

    result = proc.A - val - (1 - carry)

    overflow = _check_overflow(proc, proc.A, val, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def a(proc, addr: int) -> None:
    val = proc.mem_read(addr & 0xFFFF)
    carry = proc.P & 0x00000001

    result = proc.A - val - (1 - carry)

    overflow = _check_overflow(proc, proc.A, val, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def aix(proc, addr: int) -> None:
    val = proc.mem_read((addr + proc.X) & 0xFFFF)
    carry = proc.P & 0x00000001

    result = proc.A - val - (1 - carry)

    overflow = _check_overflow(proc, proc.A, val, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def aiy(proc, addr: int) -> None:
    val = proc.mem_read((addr + proc.Y) & 0xFFFF)
    carry = proc.P & 0x00000001

    result = proc.A - val - (1 - carry)

    overflow = _check_overflow(proc, proc.A, val, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpii(proc, zp_addr: int) -> None:
    ind_addr = (zp_addr + proc.X) & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])

    val = proc.mem_read(eff_addr & 0xFFFF)
    carry = proc.P & 0x00000001

    result = proc.A - val - (1 - carry)

    overflow = _check_overflow(proc, proc.A, val, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpiiy(proc, zp_addr: int) -> None:
    ind_addr = zp_addr & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])
    val = proc.mem_read((eff_addr + proc.Y) & 0xFFFF)
    carry = proc.P & 0x00000001

    result = proc.A - val - (1 - carry)

    overflow = _check_overflow(proc, proc.A, val, result)
    carry_out = result >= 0

    proc.A = proc.unsigned_byte(result)

    proc.set_flags(
        "C" if carry_out else "!C",
        "Z" if not bool(proc.A) else "!Z",
        "V" if overflow else "!V",
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
