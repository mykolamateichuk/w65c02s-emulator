# W65C02S Microprocessor
class W65C02S:
    def __init__(self) -> None:
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
            
        }

        self.OPCODES = {}
        for instruction, opcodes in self.INSTRUCTION_SET.items():
            if isinstance(opcodes, tuple):
                for opcode in opcodes:
                    self.OPCODES[opcode] = instruction
            else:
                self.OPCODES[opcodes] = instruction

    def mem_read(self, addr: hex) -> hex:
        return self.MEMORY[addr]
    
    def mem_write(self, addr: hex, val: hex) -> None:
        self.MEMORY[addr] = val & 0xFF  # Only the first 8 bits are stored
    
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
