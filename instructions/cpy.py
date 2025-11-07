INSTRUCTION = "CPY"

ADM_IA      = 0xC0
ADM_ZP      = 0xC4
ADM_A       = 0xCC


def ia(proc, value: int) -> None:
    y_s = proc.signed_byte(proc.Y)
    v_s = proc.signed_byte(value & 0xFF)

    carry = y_s >= v_s
    zero = y_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )


def zp(proc, zp_addr: int) -> None:
    mem_val = proc.mem_read(zp_addr & 0xFF)

    y_s = proc.signed_byte(proc.Y)
    v_s = proc.signed_byte(mem_val)

    carry = y_s >= v_s
    zero = y_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )


def a(proc, addr: int) -> None:
    val = proc.mem_read(addr & 0xFFFF)

    y_s = proc.signed_byte(proc.Y)
    v_s = proc.signed_byte(val)

    carry = y_s >= v_s
    zero = y_s == v_s

    proc.set_flags(
        "C" if carry else "!C",
        "Z" if zero else "!Z",
        "N" if bool(proc.Y & 0b10000000) else "!N"
    )


def execute_adm(adm: str, proc=None, operand: int = None) -> None:
    if adm == "IA":
        ia(proc, operand)
    if adm == "ZP":
        zp(proc, operand)
    if adm == "A":
        a(proc, operand)


def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_IA:
        ia(proc, args[0])
    if opcode == ADM_ZP:
        zp(proc, args[0])
    if opcode == ADM_A:
        a(proc, (args[1] << 8) + args[0])

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_IA:     2,
        ADM_ZP:     2,
        ADM_A:      3,
    }

    return opcodes.get(opcode)
