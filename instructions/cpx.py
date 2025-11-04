INSTRUCTION = "CPX"

ADM_IA      = 0xE0
ADM_ZP      = 0xE4
ADM_A       = 0xEC


def ia(proc, value: int) -> None:
    x_s = proc.signed_byte(proc.X)
    v_s = proc.signed_byte(value & 0xFF)

    carry = x_s >= v_s
    zero = x_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )


def zp(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read(zp_addr & 0xFF)

    x_s = proc.signed_byte(proc.X)
    v_s = proc.signed_byte(mem_val)

    carry = x_s >= v_s
    zero = x_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )


def a(proc, addr: int) -> None:
    val = proc.mem_read(addr & 0xFFFF)

    x_s = proc.signed_byte(proc.X)
    v_s = proc.signed_byte(val)

    carry = x_s >= v_s
    zero = x_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )


def execute_adm(adm: str, proc=None, operand: int = None) -> None:
    if adm == "IA":
        ia(proc, operand)
    if adm == "ZP":
        zp(proc, operand)
    if adm == "A":
        a(proc, operand)


def execute_opcode() -> None:
    pass
