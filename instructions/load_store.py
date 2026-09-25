def lda(cpu, loc) -> None:
    cpu.A = cpu.set_nz(cpu.load(loc))


def ldx(cpu, loc) -> None:
    cpu.X = cpu.set_nz(cpu.load(loc))


def ldy(cpu, loc) -> None:
    cpu.Y = cpu.set_nz(cpu.load(loc))


def sta(cpu, loc) -> None:
    cpu.store(loc, cpu.A)


def stx(cpu, loc) -> None:
    cpu.store(loc, cpu.X)


def sty(cpu, loc) -> None:
    cpu.store(loc, cpu.Y)
