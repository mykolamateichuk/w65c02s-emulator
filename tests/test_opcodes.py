"""The opcode table against the W65C02S datasheet, and the assembler against the table."""
import pytest

from asm_to_bin import encode
from opcodes import OPCODES

# Reserved opcodes execute as NOPs of these lengths (WDC W65C02S datasheet, table 6-4)
RESERVED_2_BYTES = {0x02, 0x22, 0x42, 0x62, 0x82, 0xC2, 0xE2, 0x44, 0x54, 0xD4, 0xF4}
RESERVED_3_BYTES = {0x5C, 0xDC, 0xFC}

# An operand of the right shape for each mode, in datasheet notation
SAMPLE_OPERAND = {
    "a": "$1234", "(a,x)": "($1234,X)", "a,x": "$1234,X", "a,y": "$1234,Y", "(a)": "($1234)",
    "A": "A", "#": "#$12", "i": "", "r": "$12", "s": "",
    "zp": "$12", "(zp,x)": "($12,X)", "zp,x": "$12,X", "zp,y": "$12,Y", "(zp)": "($12)", "(zp),y": "($12),Y",
}
SAMPLE_BYTES = {1: b"", 2: b"\x12", 3: b"\x34\x12"}

DOCUMENTED = [op for op in OPCODES if not op.reserved]


def test_table_covers_every_opcode_once():
    assert [op.opcode for op in OPCODES] == list(range(0x100))
    assert len(DOCUMENTED) == 212


def test_reserved_opcodes_are_nops_of_datasheet_length():
    for op in OPCODES:
        if op.reserved:
            want = 3 if op.opcode in RESERVED_3_BYTES else 2 if op.opcode in RESERVED_2_BYTES else 1
            assert (op.size, op.fn.__name__) == (want, "nop"), f"${op.opcode:02X}"


def test_wai_and_stp_are_instructions():
    assert (str(OPCODES[0xCB]), str(OPCODES[0xDB])) == ("WAI i", "STP i")
    assert str(OPCODES[0xEA]) == "NOP i"


@pytest.mark.parametrize("op", [op for op in DOCUMENTED if op.mnemonic[:3] not in ("BBR", "BBS")],
                         ids=lambda op: f"{op.opcode:02X} {op}")
def test_assembler_round_trips_every_documented_opcode(op):
    line = f"{op.mnemonic} {SAMPLE_OPERAND[op.mode.syntax]}".strip()
    assert encode(line) == bytes([op.opcode]) + SAMPLE_BYTES[op.size]
