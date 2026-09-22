"""Drive the emulator through its three public entry points.

Tests talk to the emulator only through these helpers, so a restructure of the
core needs to update this file, not every test.
"""
import builtins
import os
import tempfile

from w65c02s import W65C02S
from cli import w65c02s_interface
from asm_to_bin import preprocess, asm_to_binary

FLAG_BITS = {"C": 0, "Z": 1, "I": 2, "D": 3, "B": 4, "V": 6, "N": 7}


def make_cpu(rom=None, *, A=None, X=None, Y=None, S=None, P=None, flags=None, mem=None) -> W65C02S:
    cpu = W65C02S(bytes(rom) if rom is not None else None)
    for reg, val in (("A", A), ("X", X), ("Y", Y), ("S", S), ("P", P)):
        if val is not None:
            setattr(cpu, reg, val)
    for name, on in (flags or {}).items():
        if on:
            cpu.P |= 1 << FLAG_BITS[name]
        else:
            cpu.P &= ~(1 << FLAG_BITS[name])
    for addr, val in (mem or {}).items():
        cpu.MEMORY[addr] = val
    return cpu


def flag(cpu: W65C02S, name: str) -> int:
    return (cpu.P >> FLAG_BITS[name]) & 1


def run_rom(program, **state) -> W65C02S:
    """Run machine code in the ROM runner, terminated by a BRK."""
    cpu = make_cpu(list(program) + [0x00], **state)
    cpu.execute_from_rom()
    return cpu


def run_shell(lines, cpu: W65C02S = None, **state) -> W65C02S:
    """Feed lines to the interactive shell, then `!exit`."""
    cpu = cpu or make_cpu(**state)
    feed = iter(list(lines) + ["!exit"])
    original = builtins.input
    builtins.input = lambda prompt="": next(feed)
    try:
        w65c02s_interface(cpu)
    finally:
        builtins.input = original
    return cpu


def assemble(lines) -> bytes:
    """Assemble source lines and return the emitted bytes."""
    processed, _ = preprocess(list(lines))
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "out.bin")
        asm_to_binary(processed, out)
        with open(out, "rb") as f:
            return f.read()
