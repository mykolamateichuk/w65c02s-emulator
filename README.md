## W65C02S Emulator

### Tests
```
pip install -r requirements-dev.txt
python -m pytest
```
`tests/test_instructions.py` runs every case through the ROM runner, the shell and the assembler.
`tests/test_regressions.py` has one test per known bug (B01–B22); open bugs are strict `xfail`,
so fixing one turns its test red until the marker is updated to `fixed_in=<step>`.

### Architecture and instruction set

#### Registers
[![registers](_imgs/registers.png)]()

#### Addressing modes
![addr_modes](_imgs/addr_modes.png)

#### Instruction set
![instr_set](_imgs/instr_set.png)
