"""End-to-end: assemble with the CLI, run the binary with the ROM runner, inspect in the shell."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROGRAM = """\
; exercises every entry point
LDA #$00
LDX #$05
INX
TXA
BRA $02
LDA #$FF    ; skipped by BRA
PHA
SEC
STA $0234
"""


def test_assemble_run_and_inspect(tmp_path):
    src, rom = tmp_path / "prog.s", tmp_path / "prog.bin"
    src.write_text(PROGRAM)

    asm = subprocess.run([sys.executable, "asm_to_bin.py", "-s", str(src), "-r", str(rom)],
                         cwd=ROOT, capture_output=True, text=True)
    assert asm.returncode == 0, asm.stderr
    assert rom.read_bytes().hex(" ") == "a9 00 a2 05 e8 8a 80 02 a9 ff 48 38 8d 34 02"

    run = subprocess.run([sys.executable, "w65c02s.py", "--rom", str(rom)],
                         input="!reg\n!mem 0234\n!stk /FD\n!exit\n",
                         cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert "| 06 | 06 | 00 |" in run.stdout  # A X Y
    assert "0234: 06" in run.stdout
    assert "01FD: 06" in run.stdout
