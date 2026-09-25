def asl(cpu, loc) -> None:
    v = cpu.load(loc)
    cpu.C = bool(v & 0x80)
    cpu.store(loc, cpu.set_nz((v << 1) & 0xFF))


def lsr(cpu, loc) -> None:
    v = cpu.load(loc)
    cpu.C = bool(v & 0x01)
    cpu.store(loc, cpu.set_nz(v >> 1))


def rol(cpu, loc) -> None:
    v = cpu.load(loc)
    r = (v << 1 | cpu.C) & 0xFF
    cpu.C = bool(v & 0x80)
    cpu.store(loc, cpu.set_nz(r))


def ror(cpu, loc) -> None:
    v = cpu.load(loc)
    r = v >> 1 | cpu.C << 7
    cpu.C = bool(v & 0x01)
    cpu.store(loc, cpu.set_nz(r))
