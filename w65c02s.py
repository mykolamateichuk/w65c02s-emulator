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
        }

        self.RUNNING = True
    
    def _mem_read(self, addr: hex) -> hex:
        return self.MEMORY[addr]
    
    def _mem_write(self, addr: hex, val: hex) -> None:
        self.MEMORY[addr] = val & 0xFF  # Only first 8 bits are stored
    
    def _stk_pull(self) -> hex:
        self.S = (self.S + 0x01) & 0xFF  # Increment S (if >255 wrap around to 0)
        return self._mem_read(self.STACK_ADDR + self.S)
    
    def _stk_push(self, val: hex) -> None:
        self._mem_write(self.STACK_ADDR + self.S, val)
        self.S = (self.S - 0x01) & 0xFF  # Decrement S (if <0 wrap around to 255)

    def _set_flags(self, *flags) -> None:
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

    def _proc_instruction(self, opcode: int, *args) -> None:
        if opcode in self.INSTRUCTION_SET["NOP"]:
            self.nop()

        # Flag instructions
        elif opcode == self.INSTRUCTION_SET["CLC"]:
            self.clc()
        elif opcode == self.INSTRUCTION_SET["SEC"]:
            self.sec()
        elif opcode == self.INSTRUCTION_SET["CLI"]:
            self.cli()
        elif opcode == self.INSTRUCTION_SET["SEI"]:
            self.sei()
        elif opcode == self.INSTRUCTION_SET["CLV"]:
            self.clv()
        elif opcode == self.INSTRUCTION_SET["CLD"]:
            self.cld()
        elif opcode == self.INSTRUCTION_SET["SED"]:
            self.sed()

        # Register instructions
        elif opcode == self.INSTRUCTION_SET["TAX"]:
            self.tax()
        elif opcode == self.INSTRUCTION_SET["TXA"]:
            self.txa()
        elif opcode == self.INSTRUCTION_SET["DEX"]:
            self.dex()
        elif opcode == self.INSTRUCTION_SET["INX"]:
            self.inx()
        elif opcode == self.INSTRUCTION_SET["TAY"]:
            self.tay()
        elif opcode == self.INSTRUCTION_SET["TYA"]:
            self.tya()
        elif opcode == self.INSTRUCTION_SET["DEY"]:
            self.dey()
        elif opcode == self.INSTRUCTION_SET["INY"]:
            self.iny()

        # Stack instructions
        elif opcode == self.INSTRUCTION_SET["TXS"]:
            self.txs()
        elif opcode == self.INSTRUCTION_SET["TSX"]:
            self.tsx()
        elif opcode == self.INSTRUCTION_SET["PHA"]:
            self.pha()
        elif opcode == self.INSTRUCTION_SET["PLA"]:
            self.pla()
        elif opcode == self.INSTRUCTION_SET["PHP"]:
            self.php()
        elif opcode == self.INSTRUCTION_SET["PLP"]:
            self.plp()

    def nop(self) -> None:
        pass

    def clc(self) -> None:
        self._set_flags("!C")

    def sec(self) -> None:
        self._set_flags("C")

    def cli(self) -> None:
        self._set_flags("!I")

    def sei(self) -> None:
        self._set_flags("I")

    def clv(self) -> None:
        self._set_flags("!V")

    def cld(self) -> None:
        self._set_flags("!D")

    def sed(self) -> None:
        self._set_flags("D")

    def tax(self) -> None:
        self.X = self.A
        self._set_flags(
            "Z" if not bool(self.X) else "!Z",
            "N" if bool(self.X) & 0x80 else "!N"  # 0x80 = 0b10000000
        )

    def txa(self) -> None:
        self.A = self.X
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A) & 0x80 else "!N"  # 0x80 = 0b10000000
        )

    # TODO: flags
    def dex(self) -> None:
        self.X -= 0x01

    # TODO: flags
    def inx(self) -> None:
        self.X += 0x01

    def tay(self) -> None:
        self.Y = self.A
        self._set_flags(
            "Z" if not bool(self.Y) else "!Z",
            "N" if bool(self.Y) & 0x80 else "!N"  # 0x80 = 0b10000000
        )

    def tya(self) -> None:
        self.A = self.Y
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A) & 0x80 else "!N"  # 0x80 = 0b10000000
        )

    # TODO: flags
    def dey(self) -> None:
        self.Y -= 0x01

    # TODO: flags
    def iny(self) -> None:
        self.Y += 0x01

    def txs(self) -> None:
        self.S = self.X

    def tsx(self) -> None:
        self.X = self.S
        self._set_flags(
            "Z" if not bool(self.X) else "!Z",
            "N" if bool(self.X) & 0x80 else "!N"  # 0x80 = 0b10000000
        )

    def pha(self) -> None:
        self._stk_push(self.A)

    def pla(self) -> None:
        self.A = self._stk_pull()
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A) & 0x80 else "!N"  # 0x80 = 0b10000000
        )

    def php(self) -> None:
        self._stk_push(self.P)

    def plp(self) -> None:
        self.P = self._stk_pull()
