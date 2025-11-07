INSTRUCTION = "LDX"

ADM_IA      = 0xA2
ADM_ZP      = 0xA6
ADM_ZPIY    = 0xB6
ADM_A       = 0xAE
ADM_AIY     = 0xBE


def ia(proc, value: int) -> None:
    proc.X = value & 0xFF

    proc.set_flags(
        "Z" if not bool(proc.X) else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )

def zp(proc, zp_addr: int) -> None:
    proc.X = proc.MEMORY[zp_addr & 0xFF]

    proc.set_flags(
        "Z" if not bool(proc.X) else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )

def zpiy(proc, zp_addr: int) -> None:
    eff_addr = (zp_addr + proc.Y) & 0xFF
    proc.X = proc.MEMORY[eff_addr]

    proc.set_flags(
        "Z" if not bool(proc.X) else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )

def a(proc, addr: int) -> None:
    proc.X = proc.MEMORY[addr & 0xFFFF]

    proc.set_flags(
        "Z" if not bool(proc.X) else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )

def aiy(proc, addr: int) -> None:
    eff_addr = (addr + proc.Y) & 0xFFFF
    proc.X = proc.MEMORY[eff_addr]

    proc.set_flags(
        "Z" if not bool(proc.X) else "!Z",
        "N" if bool(proc.X & 0b10000000) else "!N"
    )


def execute_adm(adm: str, proc = None, operand: int = None) -> None:
    if adm == "IA":
        ia(proc, operand)
    if adm == "ZP":
        zp(proc, operand)
    if adm == "ZPIY":
        zpiy(proc, operand)
    if adm == "A":
        a(proc, operand)
    if adm == "AIY":
        aiy(proc, operand)

def execute_opcode(proc, opcode: int, *args) -> None:
    if opcode == ADM_IA:
        ia(proc, args[0])
    if opcode == ADM_ZP:
        zp(proc, args[0])
    if opcode == ADM_ZPIY:
        zpiy(proc, args[0])
    if opcode == ADM_A:
        a(proc, (args[1] << 8) + args[0])
    if opcode == ADM_AIY:
        aiy(proc, (args[1] << 8) + args[0])

def get_opcode_bytes(opcode: int) -> int | None:
    opcodes = {
        ADM_IA:     2,
        ADM_ZP:     2,
        ADM_ZPIY:   2,
        ADM_A:      3,
        ADM_AIY:    3,
    }

    return opcodes.get(opcode)
