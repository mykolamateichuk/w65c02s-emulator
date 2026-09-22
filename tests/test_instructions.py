"""Characterization tests: behavior that is correct today and must survive refactors.

Every case is executed three ways, which must agree:
  * the ROM runner executes `code`
  * the shell executes `asm`
  * the assembler turns `asm` into exactly `code`

Only W65C02S-correct behavior belongs here. Known-wrong behavior is covered by
test_regressions.py instead.
"""
from dataclasses import dataclass, field

import pytest

from tests.helpers import run_rom, run_shell, assemble, flag


@dataclass
class Case:
    asm: str
    code: list
    setup: dict = field(default_factory=dict)
    expect: dict = field(default_factory=dict)

    def __str__(self):
        return self.asm


CASES = [
    # Loads, every mode
    Case("LDA #$80", [0xA9, 0x80], {}, {"A": 0x80, "N": 1, "Z": 0}),
    Case("LDA #$00", [0xA9, 0x00], {"A": 0x55}, {"A": 0x00, "Z": 1, "N": 0}),
    Case("LDA $12", [0xA5, 0x12], {"mem": {0x12: 0x42}}, {"A": 0x42}),
    Case("LDA $12,X", [0xB5, 0x12], {"X": 2, "mem": {0x14: 0x42}}, {"A": 0x42}),
    Case("LDA $FF,X", [0xB5, 0xFF], {"X": 2, "mem": {0x01: 0x42}}, {"A": 0x42}),
    Case("LDA $0234", [0xAD, 0x34, 0x02], {"mem": {0x0234: 0x42}}, {"A": 0x42}),
    Case("LDA $0234,X", [0xBD, 0x34, 0x02], {"X": 1, "mem": {0x0235: 0x42}}, {"A": 0x42}),
    Case("LDA $0234,Y", [0xB9, 0x34, 0x02], {"Y": 1, "mem": {0x0235: 0x42}}, {"A": 0x42}),
    Case("LDA ($12,X)", [0xA1, 0x12], {"X": 2, "mem": {0x14: 0x34, 0x15: 0x02, 0x0234: 0x42}}, {"A": 0x42}),
    Case("LDA ($12),Y", [0xB1, 0x12], {"Y": 1, "mem": {0x12: 0x34, 0x13: 0x02, 0x0235: 0x42}}, {"A": 0x42}),
    Case("LDX #$05", [0xA2, 0x05], {}, {"X": 0x05, "Z": 0}),
    Case("LDX $12,Y", [0xB6, 0x12], {"Y": 1, "mem": {0x13: 0x81}}, {"X": 0x81, "N": 1}),
    Case("LDX $0234,Y", [0xBE, 0x34, 0x02], {"Y": 1, "mem": {0x0235: 0x42}}, {"X": 0x42}),
    Case("LDY #$05", [0xA0, 0x05], {}, {"Y": 0x05}),
    Case("LDY $12,X", [0xB4, 0x12], {"X": 1, "mem": {0x13: 0x42}}, {"Y": 0x42}),
    Case("LDY $0234,X", [0xBC, 0x34, 0x02], {"X": 1, "mem": {0x0235: 0x42}}, {"Y": 0x42}),

    # Stores
    Case("STA $12", [0x85, 0x12], {"A": 0x42}, {"mem": {0x12: 0x42}}),
    Case("STA $12,X", [0x95, 0x12], {"A": 0x42, "X": 1}, {"mem": {0x13: 0x42}}),
    Case("STA $0234,Y", [0x99, 0x34, 0x02], {"A": 0x42, "Y": 1}, {"mem": {0x0235: 0x42}}),
    Case("STA ($12,X)", [0x81, 0x12], {"A": 0x42, "X": 2, "mem": {0x14: 0x34, 0x15: 0x02}}, {"mem": {0x0234: 0x42}}),
    Case("STA ($12),Y", [0x91, 0x12], {"A": 0x42, "Y": 1, "mem": {0x12: 0x34, 0x13: 0x02}}, {"mem": {0x0235: 0x42}}),
    Case("STX $12,Y", [0x96, 0x12], {"X": 0x42, "Y": 1}, {"mem": {0x13: 0x42}}),
    Case("STY $0234", [0x8C, 0x34, 0x02], {"Y": 0x42}, {"mem": {0x0234: 0x42}}),

    # Increment / decrement
    Case("INC $12", [0xE6, 0x12], {"mem": {0x12: 0xFF}}, {"mem": {0x12: 0x00}, "Z": 1}),
    Case("DEC $0234,X", [0xDE, 0x34, 0x02], {"X": 1, "mem": {0x0235: 0x00}}, {"mem": {0x0235: 0xFF}, "N": 1}),
    Case("INX", [0xE8], {"X": 0xFF}, {"X": 0x00, "Z": 1}),
    Case("DEX", [0xCA], {"X": 0x00}, {"X": 0xFF, "N": 1}),
    Case("INY", [0xC8], {"Y": 0x7F}, {"Y": 0x80, "N": 1}),
    Case("DEY", [0x88], {"Y": 0x01}, {"Y": 0x00, "Z": 1}),

    # Arithmetic (only cases whose flags are already correct; see B06/B07)
    Case("ADC #$03", [0x69, 0x03], {"A": 0x05, "flags": {"C": 0}}, {"A": 0x08, "C": 0, "V": 0}),
    Case("ADC #$01", [0x69, 0x01], {"A": 0xFF, "flags": {"C": 0}}, {"A": 0x00, "C": 1, "Z": 1, "V": 0}),
    Case("SBC #$03", [0xE9, 0x03], {"A": 0x05, "flags": {"C": 1}}, {"A": 0x02, "C": 1, "V": 0}),

    # Logic
    Case("AND #$0F", [0x29, 0x0F], {"A": 0xF3}, {"A": 0x03}),
    Case("ORA $12", [0x05, 0x12], {"A": 0x01, "mem": {0x12: 0x80}}, {"A": 0x81, "N": 1}),
    Case("EOR #$FF", [0x49, 0xFF], {"A": 0xFF}, {"A": 0x00, "Z": 1}),

    # Shifts and rotates
    Case("ASL A", [0x0A], {"A": 0x81}, {"A": 0x02, "C": 1}),
    Case("LSR A", [0x4A], {"A": 0x01}, {"A": 0x00, "C": 1, "Z": 1}),
    Case("ROL A", [0x2A], {"A": 0x80, "flags": {"C": 1}}, {"A": 0x01, "C": 1}),
    Case("ROR A", [0x6A], {"A": 0x01, "flags": {"C": 1}}, {"A": 0x80, "C": 1, "N": 1}),
    Case("ASL $12", [0x06, 0x12], {"mem": {0x12: 0x40}}, {"mem": {0x12: 0x80}, "N": 1, "C": 0}),
    Case("ROR $0234,X", [0x7E, 0x34, 0x02], {"X": 1, "mem": {0x0235: 0x02}}, {"mem": {0x0235: 0x01}, "C": 0}),

    # Transfers
    Case("TAX", [0xAA], {"A": 0x80}, {"X": 0x80, "N": 1}),
    Case("TXA", [0x8A], {"X": 0x00, "A": 0x12}, {"A": 0x00, "Z": 1}),
    Case("TAY", [0xA8], {"A": 0x42}, {"Y": 0x42}),
    Case("TYA", [0x98], {"Y": 0x42}, {"A": 0x42}),
    Case("TSX", [0xBA], {"S": 0xFD}, {"X": 0xFD, "N": 1}),
    Case("TXS", [0x9A], {"X": 0x10}, {"S": 0x10}),

    # Flags
    Case("SEC", [0x38], {}, {"C": 1}),
    Case("CLC", [0x18], {"flags": {"C": 1}}, {"C": 0}),
    Case("SED", [0xF8], {}, {"D": 1}),
    Case("CLD", [0xD8], {"flags": {"D": 1}}, {"D": 0}),
    Case("SEI", [0x78], {"flags": {"I": 0}}, {"I": 1}),
    Case("CLI", [0x58], {}, {"I": 0}),
    Case("CLV", [0xB8], {"flags": {"V": 1}}, {"V": 0}),

    # Stack (PHP/PLP are covered by B17)
    Case("PHA", [0x48], {"A": 0x42, "S": 0xFD}, {"mem": {0x01FD: 0x42}, "S": 0xFC}),
    Case("PLA", [0x68], {"S": 0xFC, "mem": {0x01FD: 0x80}}, {"A": 0x80, "N": 1, "S": 0xFD}),
]


def check(cpu, expect):
    for key, want in expect.items():
        if key == "mem":
            for addr, val in want.items():
                assert cpu.MEMORY[addr] == val, f"mem[${addr:04X}]"
        elif key in ("A", "X", "Y", "S"):
            assert getattr(cpu, key) == want, key
        else:
            assert flag(cpu, key) == want, f"flag {key}"


@pytest.mark.parametrize("case", CASES, ids=str)
def test_rom_runner(case):
    check(run_rom(case.code, **case.setup), case.expect)


@pytest.mark.parametrize("case", CASES, ids=str)
def test_shell(case):
    check(run_shell([case.asm], **case.setup), case.expect)


@pytest.mark.parametrize("case", CASES, ids=str)
def test_assembler(case):
    assert assemble([case.asm]) == bytes(case.code)
