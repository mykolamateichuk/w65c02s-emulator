"""The address space, the reset sequence and the run loop (roadmap step 3)."""
import pytest

from bus import Bus
from w65c02s import W65C02S


def rom_32k(code: bytes, at: int, reset: int) -> bytes:
    """A full-size ROM for $8000-$FFFF with `code` at `at` and its own reset vector."""
    image = bytearray(0x8000)
    image[at - 0x8000:at - 0x8000 + len(code)] = code
    image[0x7FFC:0x7FFE] = reset.to_bytes(2, "little")
    return bytes(image)


# --- loading and booting ------------------------------------------------------

def test_small_rom_loads_at_8000_and_boots_there():
    cpu = W65C02S(bytes([0xA9, 0x05]))
    assert cpu.MEMORY[0x8000:0x8002] == bytes([0xA9, 0x05])
    assert cpu.MEMORY[0xFFFC:0xFFFE] == bytes([0x00, 0x80])  # vector pointed at the image
    assert cpu.PC == 0x8000


def test_org_moves_the_rom():
    cpu = W65C02S(bytes([0xEA]), org=0x0200)
    assert cpu.MEMORY[0x0200] == 0xEA and cpu.PC == 0x0200


def test_full_rom_boots_from_its_own_reset_vector():
    cpu = W65C02S(rom_32k(bytes([0xA9, 0x42]), at=0x9000, reset=0x9000))
    assert cpu.PC == 0x9000
    assert cpu.run() == "BRK"
    assert cpu.A == 0x42


def test_64k_image_loads_at_0000():
    cpu = W65C02S(bytes(0x10000))
    assert cpu.PC == 0x0000


def test_rom_that_doesnt_fit_is_rejected():
    with pytest.raises(ValueError):
        W65C02S(bytes(0x100), org=0xFFF0)


def test_reset_state():
    cpu = W65C02S()
    cpu.S, cpu.I, cpu.D, cpu.stopped = 0x10, False, True, True
    cpu.reset()
    assert (cpu.S, cpu.I, cpu.D, cpu.stopped) == (0xFD, True, False, False)


# --- the program lives in the address space ------------------------------------

def test_rom_is_read_only():
    cpu = W65C02S(bytes([0x8D, 0x00, 0x80, 0x8D, 0x00, 0x02]), org=0x8000)  # STA $8000 ; STA $0200
    cpu.A = 0x55
    cpu.run()
    assert cpu.MEMORY[0x8000] == 0x8D  # the ROM ignored the write
    assert cpu.MEMORY[0x0200] == 0x55  # RAM took it


def test_code_can_read_its_own_bytes():
    cpu = W65C02S(bytes([0xAD, 0x00, 0x80]))  # LDA $8000 reads its own opcode
    cpu.run()
    assert cpu.A == 0xAD


def test_assigning_memory_replaces_the_address_space_with_ram():
    cpu = W65C02S(bytes([0xEA]))
    cpu.MEMORY = [0x00] * 0x10000
    cpu.mem_write(0x8000, 0x12)
    assert cpu.MEMORY[0x8000] == 0x12


def test_bus_wraps_addresses_and_masks_values():
    bus = Bus()
    bus.write(0x1FFFF, 0x1AB)
    assert bus.read(0xFFFF) == 0xAB


# --- stopping -------------------------------------------------------------------

def test_stp_halts_until_reset():
    cpu = W65C02S(bytes([0xDB, 0xA9, 0x05]))  # STP ; LDA #$05
    assert cpu.run() == "STP"
    assert cpu.A == 0x00 and cpu.PC == 0x8001
    assert cpu.run() == "STP"  # still stopped
    cpu.reset()
    assert cpu.PC == 0x8000 and not cpu.stopped


def test_brk_ends_the_program_until_brk_is_implemented():
    cpu = W65C02S(bytes([0xE8]))  # INX, then the $00 after the image
    assert cpu.run() == "BRK"
    assert (cpu.X, cpu.PC) == (0x01, 0x8001)


def test_trap_address_stops_before_executing_it():
    cpu = W65C02S(bytes([0xE8, 0xE8, 0xE8]))
    assert cpu.run(traps=[0x8002]) == "trap"
    assert (cpu.X, cpu.PC) == (0x02, 0x8002)


def test_branch_to_itself_stops_the_run():
    cpu = W65C02S(bytes([0xE8, 0x80, 0xFE]))  # INX ; BRA *
    assert cpu.run() == "loop"
    assert (cpu.X, cpu.PC) == (0x01, 0x8001)


def test_max_steps():
    cpu = W65C02S(bytes([0xE8] * 10))
    assert cpu.run(max_steps=3) == "max steps"
    assert cpu.X == 0x03
