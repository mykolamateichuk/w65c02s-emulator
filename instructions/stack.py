def pha(cpu, loc) -> None:
    cpu.stk_push(cpu.A)


def pla(cpu, loc) -> None:
    cpu.A = cpu.set_nz(cpu.stk_pull())


def php(cpu, loc) -> None:
    cpu.stk_push(cpu.P)


def plp(cpu, loc) -> None:
    cpu.P = cpu.stk_pull()
