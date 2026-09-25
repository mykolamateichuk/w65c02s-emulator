def _add(cpu, m: int) -> None:
    r = cpu.A + m + cpu.C
    cpu.V = bool(~(cpu.A ^ m) & (cpu.A ^ r) & 0x80)  # both inputs share a sign the result doesn't
    cpu.C = r > 0xFF
    cpu.A = cpu.set_nz(r & 0xFF)


def adc(cpu, loc) -> None:
    _add(cpu, cpu.load(loc))


def sbc(cpu, loc) -> None:
    # A - M - !C is A + ~M + C, so subtraction shares the addition flags
    _add(cpu, cpu.load(loc) ^ 0xFF)


def and_(cpu, loc) -> None:
    cpu.A = cpu.set_nz(cpu.A & cpu.load(loc))


def ora(cpu, loc) -> None:
    cpu.A = cpu.set_nz(cpu.A | cpu.load(loc))


def eor(cpu, loc) -> None:
    cpu.A = cpu.set_nz(cpu.A ^ cpu.load(loc))


def _compare(cpu, reg: int, loc) -> None:
    m = cpu.load(loc)
    cpu.C = reg >= m
    cpu.set_nz((reg - m) & 0xFF)


def cmp(cpu, loc) -> None:
    _compare(cpu, cpu.A, loc)


def cpx(cpu, loc) -> None:
    _compare(cpu, cpu.X, loc)


def cpy(cpu, loc) -> None:
    _compare(cpu, cpu.Y, loc)


def inc(cpu, loc) -> None:
    cpu.store(loc, cpu.set_nz((cpu.load(loc) + 1) & 0xFF))


def dec(cpu, loc) -> None:
    cpu.store(loc, cpu.set_nz((cpu.load(loc) - 1) & 0xFF))


def inx(cpu, loc) -> None:
    cpu.X = cpu.set_nz((cpu.X + 1) & 0xFF)


def iny(cpu, loc) -> None:
    cpu.Y = cpu.set_nz((cpu.Y + 1) & 0xFF)


def dex(cpu, loc) -> None:
    cpu.X = cpu.set_nz((cpu.X - 1) & 0xFF)


def dey(cpu, loc) -> None:
    cpu.Y = cpu.set_nz((cpu.Y - 1) & 0xFF)
