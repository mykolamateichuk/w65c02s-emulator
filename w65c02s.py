import argparse

import instructions as instr
from cli import w65c02s_interface

# W65C02S Microprocessor
class W65C02S:
    def __init__(self, rom: bytes = None) -> None:
        self.A = 0x00  # Accumulator A
        self.Y = 0x00  # Index register Y
        self.X = 0x00  # Index register X

        self.PC = 0x0000  # Program counter PC
        self.S = 0xFD  # Stack Pointer S
        self.P = 0b00100100  # Processor status register P

        self.P_FLAGS = {
            "CARRY":        0b00000001,  # Carry 1 = True
            "ZERO":         0b00000010,  # Zero 1 = True
            "IRQB_DISABLE": 0b00000100,  # IRQB disable 1 = disable
            "DECIMAL":      0b00001000,  # Decimal mode 1 = True
            "BRK_COMMAND":  0b00010000,  # BRK command 1 = BRK, 0 = IRQB
            "OVERFLOW":     0b01000000,  # Overflow 1 = True
            "NEGATIVE":     0b10000000,  # Negative 1 = True
        }

        self.MEMORY = [0x00] * 0x10000  # 64 KB
        self.STACK_START = 0x0100  # Stack start memory address
        self.STACK_END = 0x01FF  # Stack end memory address

        self.INSTRUCTION_SET = {
            # All unused opcodes are NOPs in 65C02
            "NOP": (0x02, 0x03, 0x0B, 0x13, 0x1B,
                    0x22, 0x23, 0x2B, 0x33, 0x3B,
                    0x42, 0x43, 0x44, 0x4B, 0x53,
                    0x5B, 0x5C, 0x62, 0x63, 0x6B,
                    0x73, 0x7B, 0x82, 0x83, 0x8B,
                    0x93, 0x9B, 0xA3, 0xAB, 0xB3,
                    0xBB, 0xC2, 0xC3, 0xCB, 0xD3,
                    0xD4, 0xDB, 0xDC, 0xE2, 0xE3,
                    0xEB, 0xF3, 0xF4, 0xFB, 0xFC),

            # Flag instructions
            "CLC": 0x18,  # Clear Carry
            "SEC": 0x38,  # Set Carry
            "CLI": 0x58,  # Clear Interrupt
            "SEI": 0x78,  # Set Interrupt
            "CLV": 0xB8,  # Clear Overflow
            "CLD": 0xD8,  # Clear Decimal
            "SED": 0xF8,  # Set Decimal

            # Register instructions
            "TAX": 0xAA,  # Transfer A to X
            "TXA": 0x8A,  # Transfer X to A
            "DEX": 0xCA,  # Decrement X
            "INX": 0xE8,  # Increment X
            "TAY": 0xA8,  # Transfer A to Y
            "TYA": 0x98,  # Transfer Y to A
            "DEY": 0x88,  # Decrement Y
            "INY": 0xC8,  # Increment Y

            # Stack instructions
            "TXS": 0x9A,  # Transfer X to Stack ptr
            "TSX": 0xBA,  # Transfer Stack ptr to X
            "PHA": 0x48,  # Push Accumulator
            "PLA": 0x68,  # Pull Accumulator
            "PHP": 0x08,  # Push Processor status
            "PLP": 0x28,  # Pull Processor status

            # LOAD and STORE instructions
            "LDA": (0xA9, 0xA5, 0xB5, 0xAD, 0xBD, 0xB9, 0xA1, 0xB1),
            "LDX": (0xA2, 0xA6, 0xB6, 0xAE, 0xBE),
            "LDY": (0xA0, 0xA4, 0xB4, 0xAC, 0xBC),
            "STA": (0x85, 0x95, 0x8D, 0x9D, 0x99, 0x81, 0x91),
            "STX": (0x86, 0x96, 0x8E),
            "STY": (0x84, 0x94, 0x8C),

            # Arithmetic and logic instructions
            "INC": (0xE6, 0xF6, 0xEE, 0xFE),
            "DEC": (0xC6, 0xD6, 0xCE, 0xDE),
            "ADC": (0x69, 0x65, 0x75, 0x6D, 0x7D, 0x79, 0x61, 0x71),
            "SBC": (0xE9, 0xE5, 0xF5, 0xED, 0xFD, 0xF9, 0xE1, 0xF1),
            "AND": (0x29, 0x25, 0x35, 0x2D, 0x3D, 0x39, 0x21, 0x31),
            "ORA": (0x09, 0x05, 0x15, 0x0D, 0x1D, 0x19, 0x01, 0x11),
            "EOR": (0x49, 0x45, 0x55, 0x4D, 0x5D, 0x59, 0x41, 0x51),
            "CMP": (0xC9, 0xC5, 0xD5, 0xCD, 0xDD, 0xD9, 0xC1, 0xD1),
            "CPX": (0xE0, 0xE4, 0xEC),
            "CPY": (0xC0, 0xC4, 0xCC),

            # Shift and rotate instructions
            "ASL": (0x0A, 0x06, 0x16, 0x0E, 0x1E),
            "LSR": (0x4A, 0x46, 0x56, 0x4E, 0x5E),
            "ROL": (0x2A, 0x26, 0x36, 0x2E, 0x3E),
            "ROR": (0x6A, 0x66, 0x76, 0x6E, 0x7E),

        }

        self.OPCODES = {}
        for instruction, opcodes in self.INSTRUCTION_SET.items():
            if isinstance(opcodes, tuple):
                for opcode in opcodes:
                    self.OPCODES[opcode] = instruction
            else:
                self.OPCODES[opcodes] = instruction

        self.ROM = rom

    @staticmethod
    def unsigned_byte(val: hex) -> hex:
        return val & ((1 << 8) - 1)  # Convert to 2's complement and wrap-around if needed

    @staticmethod
    def signed_byte(val: hex) -> hex:
        if val & (1 << 7):  # Check if wrapped unsigned
            return val - (1 << 8)
        return val

    def mem_read(self, addr: hex) -> hex:
        return self.MEMORY[addr]
    
    def mem_write(self, addr: hex, val: hex) -> None:
        self.MEMORY[addr] = self.unsigned_byte(val)
    
    def stk_pull(self) -> hex:
        self.S = (self.S + 0x01) & 0xFF  # Increment S (if >255 wrap around to 0)
        return self.mem_read(self.STACK_START + self.S)
    
    def stk_push(self, val: hex) -> None:
        self.mem_write(self.STACK_START + self.S, val)
        self.S = (self.S - 0x01) & 0xFF  # Decrement S (if <0 wrap around to 255)

    def set_flags(self, *flags) -> None:
        for flag in flags:
            # SET FLAGS
            if flag == "C":
                self.P |= self.P_FLAGS["CARRY"]
            elif flag == "Z":
                self.P |= self.P_FLAGS["ZERO"]
            elif flag == "I":
                self.P |= self.P_FLAGS["IRQB_DISABLE"]
            elif flag == "D":
                self.P |= self.P_FLAGS["DECIMAL"]
            elif flag == "B":
                self.P |= self.P_FLAGS["BRK_COMMAND"]
            elif flag == "V":
                self.P |= self.P_FLAGS["OVERFLOW"]
            elif flag == "N":
                self.P |= self.P_FLAGS["NEGATIVE"]

            # DISABLE FLAGS
            elif flag == "!C":
                self.P &= ~self.P_FLAGS["CARRY"]
            elif flag == "!Z":
                self.P &= ~self.P_FLAGS["ZERO"]
            elif flag == "!I":
                self.P &= ~self.P_FLAGS["IRQB_DISABLE"]
            elif flag == "!D":
                self.P &= ~self.P_FLAGS["DECIMAL"]
            elif flag == "!B":
                self.P &= ~self.P_FLAGS["BRK_COMMAND"]
            elif flag == "!V":
                self.P &= ~self.P_FLAGS["OVERFLOW"]
            elif flag == "!N":
                self.P &= ~self.P_FLAGS["NEGATIVE"]

    def execute_from_rom(self) -> None:
        while True:
            if self.PC == len(self.ROM) - 1:
                return

            opcode = self.ROM[self.PC]
            if opcode == 0x00:
                return
            print(f"{self.OPCODES.get(opcode)}", end=" ")

            num_bytes = getattr(instr, self.OPCODES[opcode].lower()).get_opcode_bytes(opcode)

            args = []
            for i in range(num_bytes - 1):
                args.append(self.ROM[self.PC + i + 1])
                print(f"{self.ROM[self.PC + i + 1]:02X}", end=" ")
            print()

            getattr(instr, self.OPCODES[opcode].lower()).execute_opcode(self, opcode, *args)

            self.PC += num_bytes

if __name__ == "__main__":
    parser = argparse.ArgumentParser("W65C02S Emulator")
    parser.add_argument("--rom", dest="rom", type=str)
    _args = parser.parse_args()

    with open(_args.rom, "rb") as _rom_file:
        _rom = _rom_file.read()

    _proc = W65C02S(_rom)
    _proc.execute_from_rom()

    w65c02s_interface(_proc)
