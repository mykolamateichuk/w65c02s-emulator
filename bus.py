"""The 64 KB address space the CPU reads and writes through.

Everything is RAM except the regions a ROM image is loaded into: those are
read-only, and writes to them are ignored, as on real hardware.
"""

SIZE = 0x10000


class Bus:
    def __init__(self, image=None) -> None:
        self.mem = bytearray(image) if image is not None else bytearray(SIZE)  # raw contents
        if len(self.mem) != SIZE:
            raise ValueError(f"a memory image must be {SIZE} bytes, got {len(self.mem)}")
        self.readonly = bytearray(SIZE)  # 1 marks a ROM byte

    def read(self, addr: int) -> int:
        return self.mem[addr & 0xFFFF]

    def write(self, addr: int, val: int) -> None:
        addr &= 0xFFFF
        if not self.readonly[addr]:
            self.mem[addr] = val & 0xFF

    def load(self, data: bytes, start: int, *, rom: bool = False) -> None:
        """Copy `data` into memory at `start`; with rom=True the region becomes read-only."""
        end = start + len(data)
        if start < 0 or end > SIZE:
            raise ValueError(f"{len(data)} bytes at ${start:04X} don't fit in the 64 KB address space")
        self.mem[start:end] = data
        if rom:
            self.readonly[start:end] = b"\x01" * len(data)
