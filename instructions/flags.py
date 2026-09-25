def clc(cpu, loc) -> None:
    cpu.C = False


def sec(cpu, loc) -> None:
    cpu.C = True


def cli(cpu, loc) -> None:
    cpu.I = False


def sei(cpu, loc) -> None:
    cpu.I = True


def clv(cpu, loc) -> None:
    cpu.V = False


def cld(cpu, loc) -> None:
    cpu.D = False


def sed(cpu, loc) -> None:
    cpu.D = True
