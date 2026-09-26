## W65C02S Emulator

### Running
```
python asm_to_bin.py -s prog.s -r prog.bin      # assemble
python w65c02s.py --rom prog.bin                # boot the ROM, trace it, then open the shell
python w65c02s.py --rom prog.bin --org 0200 --trap 020A
python w65c02s.py                               # just the shell
```
The CPU sits on a 64 KB bus. A ROM image is mapped read-only at `$8000` (or at `--org`);
an image that ends at `$FFFF` boots from its own reset vector at `$FFFC`, and a smaller one
gets a vector pointing at its first byte. A run stops on `STP`, on a `--trap` address, on a
jump or branch to itself, or on `BRK` (which ends a program until BRK is implemented).

### Tests
```
pip install -r requirements-dev.txt
python -m pytest
```
`tests/test_instructions.py` runs every case through the ROM runner, the shell and the assembler.
`tests/test_opcodes.py` checks the opcode table against the datasheet and round-trips every documented opcode through the assembler.
`tests/test_bus.py` covers the memory map, the reset sequence and the stop conditions.
`tests/test_regressions.py` has one test per known bug (B01–B23); open bugs are strict `xfail`,
so fixing one turns its test red until the marker is updated to `fixed_in=<step>`.

### Layout
```
opcodes.py      the opcode table: all 256 opcodes as (mnemonic, mode, size, handler)
modes.py        the 16 addressing modes: operand -> effective address
instructions/   one function per mnemonic, grouped by family
bus.py          the 64 KB address space: RAM, plus read-only ROM regions
w65c02s.py      the CPU: reset, step, run; and the ROM runner CLI
asm_to_bin.py   the assembler (python asm_to_bin.py -s prog.s -r prog.bin)
cli.py          the shell; each line is assembled and its bytes executed
addr_modes/     operand syntax parsers used by the assembler
```

### Architecture and instruction set

#### Registers
[![registers](_imgs/registers.png)]()

#### Addressing modes
![addr_modes](_imgs/addr_modes.png)

#### Instruction set
![instr_set](_imgs/instr_set.png)
