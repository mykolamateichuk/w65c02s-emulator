def tax(cpu, loc) -> None:
    cpu.X = cpu.set_nz(cpu.A)


def txa(cpu, loc) -> None:
    cpu.A = cpu.set_nz(cpu.X)


def tay(cpu, loc) -> None:
    cpu.Y = cpu.set_nz(cpu.A)


def tya(cpu, loc) -> None:
    cpu.A = cpu.set_nz(cpu.Y)


def tsx(cpu, loc) -> None:
    cpu.X = cpu.set_nz(cpu.S)


def txs(cpu, loc) -> None:
    cpu.S = cpu.X
