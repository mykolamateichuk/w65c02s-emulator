# W65C02S Microprocessor
import re

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

            # LDA instruction addressing modes
            "LDA": {
                "IA":       0xA9,
                "ZP":       0xA5,
                "ZPIX":     0xB5,
                "A":        0xAD,
                "AIX":      0xBD,
                "AIY":      0xB9,
                "ZPII":     0xA1,
                "ZPIIY":    0xB1,
            },
        }

        self.ADM_A_PATTERN = re.compile(r"(\$[0-9a-fA-F]{4}|%[01]{16}|[0-9]{5})")
        self.ADM_AII_PATTERN = re.compile(r"(\(\$[0-9a-fA-F]{4}\), X|\(%[01]{16}\), X|\([0-9]{5}\), X)")
        self.ADM_AIX_PATTERN = re.compile(r"(\$[0-9a-fA-F]{4}, [xX]|%[01]{16}, [xX]|[0-9]{5}, [xX])")
        self.ADM_AIY_PATTERN = re.compile(r"(\$[0-9a-fA-F]{4}, [yY]|%[01]{16}, [yY]|[0-9]{5}, [yY])")
        self.ADM_AI_PATTERN = re.compile(r"(\(\$[0-9a-fA-F]{4}\)|\(%[01]{16}\)|\([0-9]{5}\))")
        # self.ADM_AA_PATTERN = re.compile(r"")
        self.ADM_IA_PATTERN = re.compile(r"#(\$[0-9a-fA-F]{4}|%[01]{16}|[0-9]{5})")
        # self.ADM_I_PATTERN = re.compile(r"")
        # self.ADM_PCR_PATTERN = re.compile(r"")
        # self.ADM_S_PATTERN = re.compile(r"")
        self.ADM_ZP_PATTERN = re.compile(r"(\$[0-9a-fA-F]{2}|%[01]{8}|[0-9]{3})")
        self.ADM_ZPII_PATTERN = re.compile(r"(\(\$[0-9a-fA-F]{2}, X\)|\(%[01]{8}, X\)|\([0-9]{3}, X\))")
        self.ADM_ZPIX_PATTERN = re.compile(r"(\$[0-9a-fA-F]{2}, [xX]|%[01]{8}, [xX]|[0-9]{3}, [xX])")
        self.ADM_ZPIY_PATTERN = re.compile(r"(\$[0-9a-fA-F]{2}, Y|%[01]{8}, Y|[0-9]{3}, Y)")
        self.ADM_ZPI_PATTERN = re.compile(r"(\(\$[0-9a-fA-F]{2}\)|\(%[01]{8}\)|\([0-9]{3}\))")
        self.ADM_ZPIIY_PATTERN = re.compile(r"(\(\$[0-9a-fA-F]{2}\), Y|\(%[01]{8}\), Y|\([0-9]{3}\), Y)")


    def _mem_read(self, addr: hex) -> hex:
        return self.MEMORY[addr]
    
    def _mem_write(self, addr: hex, val: hex) -> None:
        self.MEMORY[addr] = val & 0xFF  # Only the first 8 bits are stored
    
    def _stk_pull(self) -> hex:
        self.S = (self.S + 0x01) & 0xFF  # Increment S (if >255 wrap around to 0)
        return self._mem_read(self.STACK_START + self.S)
    
    def _stk_push(self, val: hex) -> None:
        self._mem_write(self.STACK_START + self.S, val)
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

    @staticmethod
    def _parse_const(const: str) -> int | None:
        if const.startswith("$"):
            try:
                return int(const[1:], 16)
            except ValueError:
                return None
        elif const.startswith("%"):
            try:
                return int(const[1:], 2)
            except ValueError:
                return None
        else:
            try:
                return int(const)
            except ValueError:
                return None

    def _adm_a(self, operand: str) -> int | None:
        return self._parse_const(operand)

    def _adm_aii(self, low: int, high: int) -> int:
        ...

    def _adm_aix(self, operand: str, x: str) -> int | None:
        if x in ["x", "X"]:
            return self._parse_const(operand.split(",")[0])
        return None

    def _adm_aiy(self, operand: str, y: str) -> int| None:
        if y in ["y", "Y"]:
            return self._parse_const(operand.split(",")[0])
        return None

    def _adm_ai(self, low: int, high: int) -> int:
        ...

    def _adm_aa(self) -> int:
        ...

    def _adm_ia(self, operand: str) -> int | None:
        if operand.startswith("#"):
            return self._parse_const(operand[1:])
        return None

    def _adm_i(self) -> None:
        ...

    def _adm_pcr(self, offset: int) -> int:
        ...

    def _adm_s(self) -> int:
        ...

    def _adm_zp(self, operand: str) -> int | None:
        return self._parse_const(operand)

    def _adm_zpii(self, zp: int) -> int:
        ...

    def _adm_zpix(self, operand: str, x: str) -> int | None:
        if x in ["x", "X"]:
            return self._parse_const(operand.split(",")[0])
        return None

    def _adm_zpiy(self, zp: int) -> int:
        ...

    def _adm_zpi(self, zp: int) -> int:
        ...

    def _adm_zpiiy(self, zp: int) -> int:
        ...

    def _run_instruction(self, opcode: int, *args) -> None:
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

        # LDA
        elif opcode in self.INSTRUCTION_SET["LDA"].values():
            if opcode == 0xA9:
                self.lda_ia(args[0])
            if opcode == 0xA5:
                self.lda_zp(args[0])
            if opcode == 0xB5:
                self.lda_zpix(args[0], args[1])
            if opcode == 0xAD:
                self.lda_a(args[0])
            if opcode == 0xBD:
                self.lda_aix(args[0], args[1])
            if opcode == 0xB9:
                self.lda_aiy(args[0], args[1])
            if opcode == 0xA1:
                self.lda_zpii(args[0])
            if opcode == 0xB1:
                self.lda_zpiiy(args[0], args[1])

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
            "N" if bool(self.X & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def txa(self) -> None:
        self.A = self.X
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def dex(self) -> None:
        self.X = (self.X - 0x01) & 0xFF
        self._set_flags(
            "Z" if not bool(self.X) else "!Z",
            "N" if bool(self.X & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def inx(self) -> None:
        self.X = (self.X + 0x01) & 0xFF
        self._set_flags(
            "Z" if not bool(self.X) else "!Z",
            "N" if bool(self.X & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def tay(self) -> None:
        self.Y = self.A
        self._set_flags(
            "Z" if not bool(self.Y) else "!Z",
            "N" if bool(self.Y & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def tya(self) -> None:
        self.A = self.Y
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def dey(self) -> None:
        self.Y = (self.Y - 0x01) & 0xFF
        self._set_flags(
            "Z" if not bool(self.Y) else "!Z",
            "N" if bool(self.Y & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def iny(self) -> None:
        self.Y = (self.Y + 0x01) & 0xFF
        self._set_flags(
            "Z" if not bool(self.Y) else "!Z",
            "N" if bool(self.Y & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def txs(self) -> None:
        self.S = self.X

    def tsx(self) -> None:
        self.X = self.S
        self._set_flags(
            "Z" if not bool(self.X) else "!Z",
            "N" if bool(self.X & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def pha(self) -> None:
        self._stk_push(self.A)

    def pla(self) -> None:
        self.A = self._stk_pull()
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def php(self) -> None:
        self._stk_push(self.P)

    def plp(self) -> None:
        self.P = self._stk_pull()

    def lda_ia(self, operand: str) -> None:
        operand_hex = self._adm_ia(operand)

        self.A = operand_hex & 0xFF
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def lda_zp(self, operand: str) -> None:
        zp_addr = self._adm_zp(operand)

        self.A = self.MEMORY[zp_addr & 0xFF]
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def lda_zpix(self, operand: str, x: str) -> None:
        zp_addr = self._adm_zpix(operand, x)
        zp_addr += self.X

        self.A = self.MEMORY[zp_addr & 0xFF]
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def lda_a(self, operand: str) -> None:
        addr = self._adm_a(operand)

        self.A = self.MEMORY[addr & 0xFFFF]
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def lda_aix(self, operand: str, x: str) -> None:
        addr = self._adm_aix(operand, x)
        addr += self.X

        self.A = self.MEMORY[addr & 0xFFFF]
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def lda_aiy(self, operand: str, y: str) -> None:
        addr = self._adm_aiy(operand, y)
        addr += self.Y

        self.A = self.MEMORY[addr & 0xFFFF]
        self._set_flags(
            "Z" if not bool(self.A) else "!Z",
            "N" if bool(self.A & 0x80) else "!N"  # 0x80 = 0b10000000
        )

    def lda_zpii(self, operand: str) -> None:
        ...

    def lda_zpiiy(self, operand: str) -> None:
        ...


def _draw_flags(flags: int) -> None:
    C = int(bool(flags & 0b00000001))
    Z = int(bool(flags & 0b00000010))
    I = int(bool(flags & 0b00000100))
    D = int(bool(flags & 0b00001000))
    B = int(bool(flags & 0b00010000))
    V = int(bool(flags & 0b01000000))
    N = int(bool(flags & 0b10000000))

    print("=============================")
    print("| N | V | B | D | I | Z | C |")
    print("=============================")
    print(f"| {N} | {V} | {B} | {D} | {I} | {Z} | {C} |")
    print("=============================")


def _draw_registers(a: int, x: int, y: int) -> None:
    A = f"{a:02X}"
    X = f"{x:02X}"
    Y = f"{y:02X}"

    print("================")
    print("| A  | X  | Y  |")
    print("================")
    print(f"| {A} | {X} | {Y} |")
    print("================")


def w65c02s_interface(proc: W65C02S) -> None:
    running = True
    while running:
        tokens = input("> ").split()

        instruction = tokens[0]
        args = tokens[1:] if len(tokens) > 1 else []

        is_opcode = False
        try:
            instruction = int(instruction, 16)
            is_opcode = True
        except ValueError:
            if instruction.upper() in proc.INSTRUCTION_SET.keys():
                is_opcode = True

        if is_opcode:
            if "," in args[0]:
                args[0] = args[0].split(",")[0]
            if "(" in args[0]:
                args[0] = args[0].split("(")[1]
            if ")" in args[1]:
                args[1] = args[1].split(")")[0]

            if isinstance(instruction, int):
                proc._run_instruction(instruction, *args)
                continue

            if len(args) == 1:
                if re.match(proc.ADM_A_PATTERN, args[0]):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("A")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_AI_PATTERN, args[0]):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("AI")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_IA_PATTERN, args[0]):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("IA")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_ZP_PATTERN, args[0]):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("ZP")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_ZPI_PATTERN, args[0]):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("ZPI")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue

            if len(args) == 2:
                if re.match(proc.ADM_AII_PATTERN, ", ".join(args)):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("AII")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_AIX_PATTERN, ", ".join(args)):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("AIX")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_AIY_PATTERN, ", ".join(args)):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("AIY")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_ZPII_PATTERN, ", ".join(args)):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("ZPII")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_ZPIX_PATTERN, ", ".join(args)):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("ZPIX")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_ZPIY_PATTERN, ", ".join(args)):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("ZPIY")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue
                if re.match(proc.ADM_ZPIIY_PATTERN, ", ".join(args)):
                    opcode = proc.INSTRUCTION_SET[instruction.upper()].get("ZPIIY")
                    if not opcode:
                        continue

                    proc._run_instruction(opcode, *args)
                    continue

        if instruction == "!exit":
            running = False

        elif instruction == "!flag":
            if len(args) == 0:
                _draw_flags(proc.P)
                continue
            
            flags = {
                "C": None, 
                "Z": None,
                "I": None,
                "D": None,
                "B": None,
                "V": None,
                "N": None
            }

            for arg in args:
                if "C" in arg or "c" in arg:
                    if "!" in arg:
                        flags["C"] = False
                    else:
                        flags["C"] = True
                if "Z" in arg or "z" in arg:
                    if "!" in arg:
                        flags["Z"] = False
                    else:
                        flags["Z"] = True
                if "I" in arg or "i" in arg:
                    if "!" in arg:
                        flags["I"] = False
                    else:
                        flags["I"] = True
                if "D" in arg or "d" in arg:
                    if "!" in arg:
                        flags["D"] = False
                    else:
                        flags["D"] = True
                if "B" in arg or "b" in arg:
                    if "!" in arg:
                        flags["B"] = False
                    else:
                        flags["B"] = True
                if "V" in arg or "v" in arg:
                    if "!" in arg:
                        flags["V"] = False
                    else:
                        flags["V"] = True
                if "N" in arg or "n" in arg:
                    if "!" in arg:
                        flags["N"] = False
                    else:
                        flags["N"] = True
            
            proc._set_flags(
                "C" if flags["C"] else "!C" if flags["C"] is False else None,
                "Z" if flags["Z"] else "!Z" if flags["Z"] is False else None,
                "I" if flags["I"] else "!I" if flags["I"] is False else None,
                "D" if flags["D"] else "!D" if flags["D"] is False else None,
                "B" if flags["B"] else "!B" if flags["B"] is False else None,
                "V" if flags["V"] else "!V" if flags["V"] is False else None,
                "N" if flags["N"] else "!N" if flags["N"] is False else None,
            )
                    
        elif instruction == "!reg":
            if len(args) == 0:
                _draw_registers(a=proc.A, x=proc.X, y=proc.Y)
                continue
            
            for arg in args:
                if "=" not in arg:
                    continue

                reg, val = arg.split("=")
                if reg in ["A", "a"]:
                    proc.A = int(val, 16)
                if reg in ["X", "x"]:
                    proc.X = int(val, 16)
                if reg in ["Y", "y"]:
                    proc.Y = int(val, 16)
        
        elif instruction == "!mem":
            if len(args) == 1:
                try:
                    addr = int(args[0], 16)
                    print(f"{addr:04X}: {proc.MEMORY[addr]:02X}")
                    continue
                except ValueError:
                    if "=" not in args[0]:
                        continue

                    addr, val = args[0].split("=")

                    try:
                        addr = int(addr, 16)
                        val = int(val, 16)
                    except ValueError:
                        continue

                    proc._mem_write(addr, val)
                    continue

            if len(args) == 2:
                try:
                    addr1 = int(args[0], 16)
                    addr2 = int(args[1], 16)
                except ValueError:
                    continue

                num_rows = (addr2 - addr1) // 16

                if num_rows == 0:
                    values = " ".join([f"{val:02X}" for val in proc.MEMORY[addr1:addr2 + 1]])
                    print(f"{addr1:04X}-{addr2:04X}: {values}")
                    continue

                if num_rows >= 1:
                    row_end_addr = addr1 - 1

                    addr1_offset = addr1 & 0x000F
                    if addr1_offset != 0:
                        row_end_addr = addr1 + (0x000F - addr1_offset)

                        spaces = " ".join(["  " for _ in range(addr1_offset)])
                        values = " ".join([f"{val:02X}" for val in proc.MEMORY[addr1:row_end_addr + 1]])

                        print(f"{addr1:04X}-{row_end_addr:04X}: {spaces} {values}")                

                    row_start_addr = row_end_addr + 0x0001
                    for _ in range(num_rows + 1):
                        row_end_addr = row_start_addr + 0x000F

                        values = " ".join([f"{val:02X}" for val in proc.MEMORY[row_start_addr:row_end_addr + 1]])
                        print(f"{row_start_addr:04X}-{row_end_addr:04X}: {values}")

                        row_start_addr = row_end_addr + 0x0001
                    
                    addr2_offset = addr2 & 0x000F
                    if addr2_offset != 0x000F:
                        row_start_addr = addr2 - addr2_offset

                        spaces = " ".join(["  " for _ in range(0x000F - addr2_offset)])
                        values = " ".join([f"{val:02X}" for val in proc.MEMORY[row_start_addr:addr2 + 1]])

                        print(f"{row_start_addr:04X}-{addr2:04X}: {values} {spaces}")

        elif instruction == "!stk":
            STACK = proc.MEMORY[proc.STACK_START:proc.STACK_END + 1]

            if len(args) == 1:
                if args[0] == "pull":
                    val = proc._stk_pull()
                    print(f"{val:02X}")
                    continue
                if args[0] == "ptr":
                    print(f"{proc.S:02X}")
                    continue

                try:
                    addr = int(args[0], 16)
                    print(f"{addr:02X}: {STACK[addr]:02X}")
                    continue
                except ValueError:
                    if args[0][0] == "/":
                        addr = int(args[0][1:], 16)
                        print(f"{(0x0100 + addr):04X}: {proc.MEMORY[0x0100 + addr]:02X}")
                        continue

            if len(args) == 2:
                if args[0] == "push":
                    try:
                        val = int(args[1], 16)
                    except ValueError:
                        continue

                    proc._stk_push(val)
        
        elif instruction == "!flush":
            allowed_fields = {
                "A":        0x00,
                "X":        0x00,
                "Y":        0x00,
                "PC":       0x0000,
                "S":        0xFD,
                "P":        0b00100100,
                "MEMORY":   [0x00] * 0x10000
            }

            if len(args) == 0:
                proc.A = 0x00
                proc.Y = 0x00
                proc.X = 0x00

                proc.PC = 0x0000
                proc.S = 0xFD
                proc.P = 0b00100100

                proc.MEMORY = [0x00] * 0x10000
                continue
            
            for arg in args:
                if arg.upper() in allowed_fields.keys():
                    proc.__setattr__(arg.upper(), allowed_fields[arg.upper()])
            

if __name__ == "__main__":
    _proc = W65C02S()

    w65c02s_interface(_proc)
