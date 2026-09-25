"""One regression test per bug from the project audit (IDs match the dashboard).

Open bugs are marked xfail(strict=True): the suite stays green while they are
open, and turns red the moment one gets fixed, so the marker must be removed
(changing `fixed_in`) in the same commit as the fix.
"""
import builtins
import subprocess
import sys
from pathlib import Path

import pytest

from cli import print_memory
from asm_to_bin import preprocess
from w65c02s import W65C02S
from tests.helpers import run_rom, run_shell, assemble, make_cpu, flag

ROOT = Path(__file__).resolve().parents[1]


def bug(bug_id, *, fixed_in=None, reason=""):
    """Tag a regression test with its bug ID; unfixed bugs are expected to fail."""
    def deco(fn):
        fn = pytest.mark.bug(bug_id)(fn)
        if fixed_in is None:
            fn = pytest.mark.xfail(reason=f"{bug_id} open: {reason}", strict=True)(fn)
        return fn
    return deco


# --- critical ---------------------------------------------------------------

IMPLIED_OPCODES = [
    0x18, 0x38, 0x58, 0x78, 0xB8, 0xD8, 0xF8,  # CLC SEC CLI SEI CLV CLD SED
    0xAA, 0x8A, 0xA8, 0x98, 0xE8, 0xC8, 0xCA, 0x88,  # TAX TXA TAY TYA INX INY DEX DEY
    0x9A, 0xBA, 0x48, 0x68, 0x08, 0x28,  # TXS TSX PHA PLA PHP PLP
    0x03,  # a NOP-list opcode
]


@bug("B01", fixed_in=1)
def test_B01_rom_runner_executes_implied_instructions():
    cpu = run_rom([0xA9, 0x05, 0xE8])  # LDA #$05 ; INX
    assert (cpu.A, cpu.X) == (0x05, 0x01)
    for op in IMPLIED_OPCODES:
        run_rom([op])


@bug("B02", fixed_in=1)
def test_B02_bra_runs_everywhere():
    assert run_rom([0x80, 0x02, 0xA9, 0x01, 0xA9, 0x02]).A == 0x02  # skips LDA #$01
    assert run_shell(["BRA $02"]).PC == 0x04  # relative to the next instruction
    assert assemble(["BRA $02"]) == bytes([0x80, 0x02])
    assert assemble(["BRA $FE"]) == bytes([0x80, 0xFE])


@bug("B03", fixed_in=1)
def test_B03_assembler_cli_writes_binary(tmp_path):
    src, out = tmp_path / "prog.s", tmp_path / "prog.bin"
    src.write_text("; demo\nLDA #$05\nINX\n")
    result = subprocess.run(
        [sys.executable, "asm_to_bin.py", "-s", str(src), "-r", str(out)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out.read_bytes() == bytes([0xA9, 0x05, 0xE8])


@bug("B04", fixed_in=1)
def test_B04_zero_operand_is_kept():
    cpu = run_shell(["LDA #$00"], A=0x55)
    assert cpu.A == 0x00 and flag(cpu, "Z") == 1
    assert assemble(["LDA #$00", "INX"]) == bytes([0xA9, 0x00, 0xE8])


# --- high -------------------------------------------------------------------

@bug("B05", fixed_in=2)
def test_B05_compares_are_unsigned():
    cpu = run_shell(["CMP #$01"], A=0x80)
    assert (flag(cpu, "C"), flag(cpu, "N")) == (1, 0)
    cpu = run_shell(["CMP #$02"], A=0x01)
    assert (flag(cpu, "C"), flag(cpu, "N")) == (0, 1)
    assert flag(run_shell(["CPX #$01"], X=0x80), "C") == 1
    assert flag(run_shell(["CPY #$01"], Y=0x80), "C") == 1


@bug("B06", fixed_in=2)
def test_B06_adc_overflow():
    assert flag(run_shell(["ADC #$FF"], A=0xFF, flags={"C": 0}), "V") == 0
    assert flag(run_shell(["ADC #$7F"], A=0x00, flags={"C": 1}), "V") == 1


@bug("B07", fixed_in=2)
def test_B07_sbc_overflow():
    assert flag(run_shell(["SBC #$01"], A=0x80, flags={"C": 1}), "V") == 1
    assert flag(run_shell(["SBC #$FF"], A=0x7F, flags={"C": 1}), "V") == 1


@bug("B08", fixed_in=2)
def test_B08_absolute_below_0100_is_two_bytes():
    assert assemble(["STA $0012"]) == bytes([0x8D, 0x12, 0x00])


@bug("B09", reason="labels resolve to line indexes; branches get absolute addresses")
def test_B09_labels_are_byte_addresses():
    _, labels = preprocess(["LDA #$01", "LDA #$02", "end:", "INX"])
    assert labels["end"] == "$0004"
    assert assemble(["lp:", "INX", "BRA lp"]) == bytes([0xE8, 0x80, 0xFD])


@bug("B10", reason="labels are substituted as raw substrings")
def test_B10_label_substitution_matches_whole_identifiers():
    lines, _ = preprocess(["IN:", "INX"])
    assert lines == ["INX"]
    lines, labels = preprocess(["lp:", "INX", "lp2:", "DEX", "BRA lp2"])
    assert lines[-1] == f"BRA {labels['lp2']}"


@bug("B11", fixed_in=1)
def test_B11_rom_runner_loop_bounds():
    cpu = W65C02S(bytes([0xA9, 0x05, 0x69, 0x01]))  # no trailing BRK
    cpu.execute_from_rom()
    assert cpu.A == 0x06
    cpu = W65C02S(bytes([0xA9, 0x01, 0x0A]))  # last byte is a 1-byte instruction
    cpu.execute_from_rom()
    assert cpu.A == 0x02


@bug("B12", fixed_in=2)
def test_B12_unknown_opcode_error_is_descriptive():
    with pytest.raises(Exception) as exc:
        W65C02S(bytes([0x4C, 0x00, 0x00, 0x00])).execute_from_rom()  # JMP
    assert not isinstance(exc.value, KeyError)
    assert "4C" in str(exc.value).upper()


@bug("B13", reason="STP doesn't halt yet (NOP decoding was fixed in step 2)")
def test_B13_nop_decoding_matches_datasheet():
    assert run_rom([0xEA, 0xA9, 0x05]).A == 0x05              # real NOP
    assert run_rom([0x5C, 0x34, 0x12, 0xA9, 0x05]).A == 0x05  # 3-byte undefined NOP
    assert run_rom([0x02, 0x34, 0xA9, 0x05]).A == 0x05        # 2-byte undefined NOP
    assert run_rom([0xDB, 0xA9, 0x05]).A == 0x00              # STP halts


# --- medium -----------------------------------------------------------------

@bug("B14", reason="decimal mode is ignored")
def test_B14_decimal_mode_adc():
    assert run_shell(["ADC #$01"], A=0x09, flags={"D": 1, "C": 0}).A == 0x10


@bug("B15", fixed_in=2)
def test_B15_zero_page_pointer_wraps():
    mem = {0xFF: 0x34, 0x00: 0x12, 0x100: 0x99, 0x1234: 0x42, 0x9934: 0x77}
    assert run_shell(["LDA ($FF),Y"], Y=0, mem=mem).A == 0x42


@bug("B16", fixed_in=2)
def test_B16_zero_page_indirect_mode():
    mem = {0x12: 0x34, 0x13: 0x12, 0x1234: 0x99}
    assert run_shell(["LDA ($12)"], mem=mem).A == 0x99


@bug("B17", reason="PHP doesn't push B set (PLP bit 5 was fixed in step 2)")
def test_B17_php_plp_status_bits():
    cpu = run_rom([0x28], S=0xFC, mem={0x01FD: 0x00})  # PLP
    assert cpu.P & 0x20 and not cpu.P & 0x10
    cpu = run_rom([0x08], P=0x24)  # PHP
    assert cpu.MEMORY[0x01FD] == 0x34


@bug("B18", reason="operand parsing is width-based and unanchored")
def test_B18_operand_parsing_by_value():
    assert run_shell(["LDA $123"], mem={0x0123: 0x42, 0x23: 0x11}).A == 0x42
    assert run_shell(["LDA 10"], mem={0x0A: 0x42}).A == 0x42
    assert run_shell(["LDA #$5"]).A == 0x05


# --- low --------------------------------------------------------------------

@bug("B19", reason="shell crashes on empty line and EOF")
def test_B19_shell_survives_empty_line_and_eof(monkeypatch):
    run_shell([""])

    def eof(prompt=""):
        raise EOFError
    monkeypatch.setattr(builtins, "input", eof)
    from cli import w65c02s_interface
    w65c02s_interface(make_cpu())


@bug("B20", fixed_in=2)
def test_B20_shell_accepts_raw_opcodes():
    assert run_shell(["A9 05"]).A == 0x05


@bug("B21", reason="range dump overshoots and repeats a row")
def test_B21_memory_dump_stops_at_range_end(capsys):
    cpu = make_cpu(mem={a: a for a in range(0x40)})
    print_memory(cpu, 0x03, 0x25)
    starts = [line.split("-")[0] for line in capsys.readouterr().out.splitlines()]
    assert starts == ["0003", "0010", "0020"]


@bug("B22", reason="!reg values aren't masked")
def test_B22_loose_ends():
    # The instructions.__all__ and "_" suffix items went away with the step 2 opcode table
    assert run_shell(["!reg A=1FF"]).A == 0xFF
