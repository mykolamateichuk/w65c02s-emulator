def nop(cpu, loc) -> None:
    pass


def stp(cpu, loc) -> None:
    cpu.stopped = True
