INSTRUCTION = "CMP"

ADM_IA      = 0xC9
ADM_ZP      = 0xC5
ADM_ZPIX    = 0xD5
ADM_A       = 0xCD
ADM_AIX     = 0xDD
ADM_AIY     = 0xD9
ADM_ZPII    = 0xC1
ADM_ZPIIY   = 0xD1


def ia(proc, value: int) -> None:
    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(value & 0xFF)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zp(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read(zp_addr & 0xFF)

    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(mem_val)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpix(proc, zp_addr: int) -> None:
    val = proc.mem_read((zp_addr + proc.X) & 0xFF)

    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(val)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def a(proc, addr: int) -> None:
    val = proc.mem_read(addr & 0xFFFF)

    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(val)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def aix(proc, addr: int) -> None:
    val = proc.mem_read((addr + proc.X) & 0xFFFF)

    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(val)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def aiy(proc, addr: int) -> None:
    val = proc.mem_read((addr + proc.Y) & 0xFFFF)

    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(val)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpii(proc, zp_addr: int) -> None:
    ind_addr = (zp_addr + proc.X) & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])
    val = proc.mem_read(eff_addr & 0xFFFF)

    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(val)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.A & 0b10000000) else "!N"
    )


def zpiiy(proc, zp_addr: int) -> None:
    ind_addr = zp_addr & 0xFF
    eff_addr = ((proc.MEMORY[ind_addr + 1] << 8) + proc.MEMORY[ind_addr])
    val = proc.mem_read((eff_addr + proc.Y) & 0xFFFF)

    a_s = proc.signed_byte(proc.A)
    v_s = proc.signed_byte(val)

    carry = a_s >= v_s
    zero = a_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
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


def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_IA:
        ia(proc, args[0])
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
        ADM_IA:     2,
        ADM_ZP:     2,
        ADM_ZPIX:   2,
        ADM_A:      3,
        ADM_AIX:    3,
        ADM_AIY:    3,
        ADM_ZPII:   2,
        ADM_ZPIIY:  2,
    }

    return opcodes.get(opcode)
