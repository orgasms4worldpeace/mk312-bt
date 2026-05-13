# MK-312BT firmware failure codes — complete index

_Generated 2026-05-04 from `3-build-and-flash/firmware/backup_flash.bin`. Every
`(rjmp|jmp) 0x1676` in the firmware was traced to its preceding
`ldi r26, 0xNN`. The error_handler at `0x1676` prints `"Failure NN /
Shut Off Power"` and halts; `r26` at jmp time is the displayed code._

| Code | Branch | Meaning | Class | Most likely cause |
| ---: | --- | --- | --- | --- |
| **10** | `0x0bba` | DAC write value ≥ 224 | Firmware/state | EEPROM corruption or pot/ribbon glitch |
| **15** | `0x1396`, `0x13c4` | Divide-by-zero | Firmware bug | Custom patch or RAM glitch (rare) |
| **16** | `0x15fa` | Output-level mapping won't converge | Hardware (pots) | Front-panel ribbon, noisy pot, AVCC ripple |
| **20** | `0x1494` | Output stage current sense fails (A or B) | Hardware | MOSFET Vt mismatch, transformer rev'd, R35/R46 wrong |
| **21** | `0x16e4` | Wall adapter ≥ ~17.1 V | Power | 18 V / 19 V supply over-spec, or ADC reference / ribbon |
| **72** | `0x1a1e` | State counter RAM[0x01F1] ≥ 56 | Firmware/state | Custom patch bug or EEPROM corruption |
| **80** | `0x0796` | EEPROM config byte ≥ 40 | EEPROM | First boot of fresh chip; reflash EEPROM |

## Where to start

Each code has its own `failure-NN-analysis.md` in this directory with
disassembly evidence, likely causes, and a diagnostic procedure.

**Order of frequency on a fresh build**: F20 (output stage), F21 (supply
voltage), F80 (EEPROM init). F10/F15/F16/F72 are rare in the wild and
usually point at firmware patches or worn-out hardware on long-running units.

## Caveat: dynamic dispatcher at 0x3ea

There's also one branch at `0x3ea` that does `jmp 0x1676` with a _dynamic_
code — it loads `r26` from `Y+34` and jumps if that value ≥ 4. So in
principle the firmware can display Failure codes 4, 5, 6, 7, … if some
other code path stores those values into `Y+34`. None of the literal
`ldi r26` sites elsewhere in the firmware load values in the 4–9 range, so
the practical list of codes a stock f005 build will ever actually display is
the seven above.

## Method

Disassembly: `avr-objdump -m avr5 -D --target=binary backup_flash.bin`. The
error_handler entry was identified by tracing the string `"Failure "` in
flash and finding the routine that consumes `r26` as a number to print.
Every `(rjmp|jmp) 0x1676` reference was followed back to the
immediately-preceding `ldi r26, 0xNN` instruction. Cross-checked against
`f005.bin` (the canonical firmware file) — identical bytes at all 9 sites.
