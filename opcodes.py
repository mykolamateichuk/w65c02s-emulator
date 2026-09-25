"""The W65C02S opcode table: the only place opcode facts live.

MATRIX is the opcode matrix from the WDC W65C02S datasheet, written as
"MNEMONIC mode" in datasheet notation (row = high nibble, column = low nibble).
"---" marks a reserved opcode. Those execute as NOPs of the length given by
their mode and can't be assembled.

The ROM runner decodes through OPCODES, and the assembler encodes through
lookup(), so the two can't disagree.
"""
from dataclasses import dataclass
from typing import Callable

from instructions import HANDLERS
from modes import BY_SYNTAX, Mode

RESERVED = "---"

MATRIX = [
    # x0      x1            x2          x3       x4           x5          x6          x7         x8       x9          xA        xB       xC            xD          xE          xF
    ["BRK s", "ORA (zp,x)", "--- #",    "--- i", "TSB zp",    "ORA zp",   "ASL zp",   "RMB0 zp", "PHP s", "ORA #",    "ASL A",  "--- i", "TSB a",      "ORA a",    "ASL a",    "BBR0 r"],  # 0x
    ["BPL r", "ORA (zp),y", "ORA (zp)", "--- i", "TRB zp",    "ORA zp,x", "ASL zp,x", "RMB1 zp", "CLC i", "ORA a,y",  "INC A",  "--- i", "TRB a",      "ORA a,x",  "ASL a,x",  "BBR1 r"],  # 1x
    ["JSR a", "AND (zp,x)", "--- #",    "--- i", "BIT zp",    "AND zp",   "ROL zp",   "RMB2 zp", "PLP s", "AND #",    "ROL A",  "--- i", "BIT a",      "AND a",    "ROL a",    "BBR2 r"],  # 2x
    ["BMI r", "AND (zp),y", "AND (zp)", "--- i", "BIT zp,x",  "AND zp,x", "ROL zp,x", "RMB3 zp", "SEC i", "AND a,y",  "DEC A",  "--- i", "BIT a,x",    "AND a,x",  "ROL a,x",  "BBR3 r"],  # 3x
    ["RTI s", "EOR (zp,x)", "--- #",    "--- i", "--- zp",    "EOR zp",   "LSR zp",   "RMB4 zp", "PHA s", "EOR #",    "LSR A",  "--- i", "JMP a",      "EOR a",    "LSR a",    "BBR4 r"],  # 4x
    ["BVC r", "EOR (zp),y", "EOR (zp)", "--- i", "--- zp,x",  "EOR zp,x", "LSR zp,x", "RMB5 zp", "CLI i", "EOR a,y",  "PHY s",  "--- i", "--- a",      "EOR a,x",  "LSR a,x",  "BBR5 r"],  # 5x
    ["RTS s", "ADC (zp,x)", "--- #",    "--- i", "STZ zp",    "ADC zp",   "ROR zp",   "RMB6 zp", "PLA s", "ADC #",    "ROR A",  "--- i", "JMP (a)",    "ADC a",    "ROR a",    "BBR6 r"],  # 6x
    ["BVS r", "ADC (zp),y", "ADC (zp)", "--- i", "STZ zp,x",  "ADC zp,x", "ROR zp,x", "RMB7 zp", "SEI i", "ADC a,y",  "PLY s",  "--- i", "JMP (a,x)",  "ADC a,x",  "ROR a,x",  "BBR7 r"],  # 7x
    ["BRA r", "STA (zp,x)", "--- #",    "--- i", "STY zp",    "STA zp",   "STX zp",   "SMB0 zp", "DEY i", "BIT #",    "TXA i",  "--- i", "STY a",      "STA a",    "STX a",    "BBS0 r"],  # 8x
    ["BCC r", "STA (zp),y", "STA (zp)", "--- i", "STY zp,x",  "STA zp,x", "STX zp,y", "SMB1 zp", "TYA i", "STA a,y",  "TXS i",  "--- i", "STZ a",      "STA a,x",  "STZ a,x",  "BBS1 r"],  # 9x
    ["LDY #", "LDA (zp,x)", "LDX #",    "--- i", "LDY zp",    "LDA zp",   "LDX zp",   "SMB2 zp", "TAY i", "LDA #",    "TAX i",  "--- i", "LDY a",      "LDA a",    "LDX a",    "BBS2 r"],  # Ax
    ["BCS r", "LDA (zp),y", "LDA (zp)", "--- i", "LDY zp,x",  "LDA zp,x", "LDX zp,y", "SMB3 zp", "CLV i", "LDA a,y",  "TSX i",  "--- i", "LDY a,x",    "LDA a,x",  "LDX a,y",  "BBS3 r"],  # Bx
    ["CPY #", "CMP (zp,x)", "--- #",    "--- i", "CPY zp",    "CMP zp",   "DEC zp",   "SMB4 zp", "INY i", "CMP #",    "DEX i",  "WAI i", "CPY a",      "CMP a",    "DEC a",    "BBS4 r"],  # Cx
    ["BNE r", "CMP (zp),y", "CMP (zp)", "--- i", "--- zp,x",  "CMP zp,x", "DEC zp,x", "SMB5 zp", "CLD i", "CMP a,y",  "PHX s",  "STP i", "--- a",      "CMP a,x",  "DEC a,x",  "BBS5 r"],  # Dx
    ["CPX #", "SBC (zp,x)", "--- #",    "--- i", "CPX zp",    "SBC zp",   "INC zp",   "SMB6 zp", "INX i", "SBC #",    "NOP i",  "--- i", "CPX a",      "SBC a",    "INC a",    "BBS6 r"],  # Ex
    ["BEQ r", "SBC (zp),y", "SBC (zp)", "--- i", "--- zp,x",  "SBC zp,x", "INC zp,x", "SMB7 zp", "SED i", "SBC a,y",  "PLX s",  "--- i", "--- a",      "SBC a,x",  "INC a,x",  "BBS7 r"],  # Fx
]


@dataclass(frozen=True)
class Op:
    opcode: int
    mnemonic: str
    mode: Mode
    size: int                 # bytes, opcode included
    fn: Callable | None       # None: in the datasheet, not implemented yet

    @property
    def reserved(self) -> bool:
        return self.mnemonic == RESERVED

    def __str__(self) -> str:
        return f"{self.mnemonic} {self.mode.syntax}"


def _build() -> list[Op]:
    ops = []
    for opcode in range(0x100):
        mnemonic, syntax = MATRIX[opcode >> 4][opcode & 0xF].split(" ")
        mode = BY_SYNTAX[syntax]
        size = mode.size
        if mnemonic[:3] in ("BBR", "BBS"):
            size = 3  # zero page address + relative offset
        fn = HANDLERS["NOP"] if mnemonic == RESERVED else HANDLERS.get(mnemonic)
        ops.append(Op(opcode, mnemonic, mode, size, fn))
    return ops


OPCODES = _build()

MNEMONICS = {op.mnemonic for op in OPCODES if not op.reserved}

_ENCODE = {(op.mnemonic, op.mode.name): op for op in OPCODES if not op.reserved}


def lookup(mnemonic: str, mode_name: str) -> Op | None:
    """The documented opcode for a mnemonic in an addressing mode, if the chip has one."""
    return _ENCODE.get((mnemonic.upper(), mode_name))


assert set(HANDLERS) <= MNEMONICS, f"handlers for unknown mnemonics: {set(HANDLERS) - MNEMONICS}"
