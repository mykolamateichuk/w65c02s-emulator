"""The 16 W65C02S addressing modes.

A resolver takes the CPU and the instruction's operand (the bytes after the
opcode, read as a little-endian number) and returns the location the
instruction works on:
  * an int, a 16-bit memory address
  * ACC, the accumulator
  * an Immediate, the operand value itself
  * None, when the instruction has no operand

Resolvers run after PC has been advanced past the instruction, so relative
branches are computed from the address of the next instruction.
"""
from dataclasses import dataclass
from typing import Callable

ACC = "A"


class Immediate:
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value


def _word(cpu, addr: int) -> int:
    return cpu.MEMORY[addr] | cpu.MEMORY[(addr + 1) & 0xFFFF] << 8


def _zp_word(cpu, zp_addr: int) -> int:
    # A pointer in zero page wraps within zero page: ($FF) reads $FF and $00
    return cpu.MEMORY[zp_addr & 0xFF] | cpu.MEMORY[(zp_addr + 1) & 0xFF] << 8


def a(cpu, operand: int) -> int:        # a
    return operand


def aii(cpu, operand: int) -> int:      # (a,x)
    return _word(cpu, (operand + cpu.X) & 0xFFFF)


def aix(cpu, operand: int) -> int:      # a,x
    return (operand + cpu.X) & 0xFFFF


def aiy(cpu, operand: int) -> int:      # a,y
    return (operand + cpu.Y) & 0xFFFF


def ai(cpu, operand: int) -> int:       # (a)
    return _word(cpu, operand)


def aa(cpu, operand: int) -> str:       # A
    return ACC


def ia(cpu, operand: int) -> Immediate:  # #
    return Immediate(operand)


def i(cpu, operand: int) -> None:       # i
    return None


def pcr(cpu, operand: int) -> int:      # r
    offset = operand - 0x100 if operand & 0x80 else operand
    return (cpu.PC + offset) & 0xFFFF


def s(cpu, operand: int) -> None:       # s
    return None


def zp(cpu, operand: int) -> int:       # zp
    return operand & 0xFF


def zpii(cpu, operand: int) -> int:     # (zp,x)
    return _zp_word(cpu, operand + cpu.X)


def zpix(cpu, operand: int) -> int:     # zp,x
    return (operand + cpu.X) & 0xFF


def zpiy(cpu, operand: int) -> int:     # zp,y
    return (operand + cpu.Y) & 0xFF


def zpi(cpu, operand: int) -> int:      # (zp)
    return _zp_word(cpu, operand)


def zpiiy(cpu, operand: int) -> int:    # (zp),y
    return (_zp_word(cpu, operand) + cpu.Y) & 0xFFFF


@dataclass(frozen=True)
class Mode:
    name: str        # project abbreviation, as used by the addr_modes parsers
    syntax: str      # datasheet notation
    size: int        # instruction length in bytes, opcode included
    resolve: Callable


MODES = [
    Mode("A",     "a",      3, a),
    Mode("AII",   "(a,x)",  3, aii),
    Mode("AIX",   "a,x",    3, aix),
    Mode("AIY",   "a,y",    3, aiy),
    Mode("AI",    "(a)",    3, ai),
    Mode("AA",    "A",      1, aa),
    Mode("IA",    "#",      2, ia),
    Mode("I",     "i",      1, i),
    Mode("PCR",   "r",      2, pcr),
    Mode("S",     "s",      1, s),
    Mode("ZP",    "zp",     2, zp),
    Mode("ZPII",  "(zp,x)", 2, zpii),
    Mode("ZPIX",  "zp,x",   2, zpix),
    Mode("ZPIY",  "zp,y",   2, zpiy),
    Mode("ZPI",   "(zp)",   2, zpi),
    Mode("ZPIIY", "(zp),y", 2, zpiiy),
]

BY_NAME = {mode.name: mode for mode in MODES}
BY_SYNTAX = {mode.syntax: mode for mode in MODES}
