"""One function per mnemonic, grouped by family.

Every handler has the signature `fn(cpu, loc)`, where `loc` is what the
addressing mode resolved to (see modes.py). Mnemonics missing from HANDLERS
are in the opcode table but not implemented yet.
"""
from instructions import alu, branch, flags, load_store, shift, stack, system, transfer

HANDLERS = {
    "NOP": system.nop,

    "CLC": flags.clc, "SEC": flags.sec, "CLI": flags.cli, "SEI": flags.sei,
    "CLV": flags.clv, "CLD": flags.cld, "SED": flags.sed,

    "TAX": transfer.tax, "TXA": transfer.txa, "TAY": transfer.tay, "TYA": transfer.tya,
    "TSX": transfer.tsx, "TXS": transfer.txs,

    "PHA": stack.pha, "PLA": stack.pla, "PHP": stack.php, "PLP": stack.plp,

    "LDA": load_store.lda, "LDX": load_store.ldx, "LDY": load_store.ldy,
    "STA": load_store.sta, "STX": load_store.stx, "STY": load_store.sty,

    "ADC": alu.adc, "SBC": alu.sbc, "AND": alu.and_, "ORA": alu.ora, "EOR": alu.eor,
    "CMP": alu.cmp, "CPX": alu.cpx, "CPY": alu.cpy,
    "INC": alu.inc, "DEC": alu.dec, "INX": alu.inx, "INY": alu.iny, "DEX": alu.dex, "DEY": alu.dey,

    "ASL": shift.asl, "LSR": shift.lsr, "ROL": shift.rol, "ROR": shift.ror,

    "BRA": branch.bra,
}
