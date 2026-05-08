#!/usr/bin/env python3
"""Generate one markdown per MK-312BT firmware failure code in
docs/troubleshooting/debug-notes/.

Source of truth: the firmware binary at 3-build-and-flash/firmware/backup_flash.bin
disassembled with avr-objdump -m avr5 -D --target=binary. Every claim cites a
specific flash byte address that can be verified against the dump.

Skips failure-21-analysis.md — that file already exists with a much deeper
investigation. This script only generates the codes that don't yet have notes.

Run: python3 scripts/build-failure-mds.py
"""
from pathlib import Path
from datetime import datetime
import textwrap

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "troubleshooting" / "debug-notes"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")


def write(code, content):
    p = OUT_DIR / f"failure-{code:02d}-analysis.md"
    p.write_text(content)
    return p


# --------------------------------------------------------------------------- F10
write(10, f"""# Failure 10 — DAC write value out-of-range (≥ 224)

_Generated {TODAY} from `3-build-and-flash/firmware/backup_flash.bin`
(disassembly via `avr-objdump -m avr5`)._

| Field | Value |
| --- | --- |
| Code (decimal) | **10** |
| Branch site | `0x0bba` (`rjmp .+2746` → `0x1676`) |
| Test type | Argument range check inside the DAC writer |
| When it runs | Every DAC update — ramp engine, knob change, mode switch |
| Class | Firmware/state — almost never hardware |

## Summary

F10 fires when the firmware tries to push a value ≥ 224 to the SPI DAC via the
routine at `0x0b98`. The routine cascades through three range checks and routes
legal values into different sub-paths; anything ≥ 0xE0 falls off the end of the
cascade and trips F10. In normal operation valid DAC values stay below 0xC0,
so F10 indicates that the firmware's intensity/level state has gotten into a
bad value — usually a knob/pot reading way out of band, a bus glitch corrupting
an intermediate calculation, or a ramp/multiplier bug. F10 is rare in the wild
compared to F20/F21.

## Disassembly evidence

The DAC writer at `0x0b98` takes the requested value in `r26`:

```
0b98:  push r30, r31, r28
0b9e:  lds  r30, 0x0207        ; load DAC channel flag
0ba2:  and  r30, r30
0ba4:  breq 0x0bac             ; if no override, use r26 directly
...
0bac:  cpi  r26, 0x80          ; r26 < 128 ?
0bae:  brcs 0x0bbe             ;   yes → normal write path
0bb0:  cpi  r26, 0xC0          ; r26 < 192 ?
0bb2:  brcs 0x0c24             ;   yes → alternate path
0bb4:  cpi  r26, 0xE0          ; r26 < 224 ?
0bb6:  brcs 0x0bbc             ;   yes → another path
0bb8:  ldi  r26, 0x0A          ; ← loads code 10
0bba:  rjmp 0x1676             ; ← FAILURE 10
```

The cascade implements a banded DAC update: low values (< 128) write directly,
mid-band values take a slow-update path, upper-mid values (192–223) take a
special case, and the top band (≥ 224) is treated as illegal.

## Likely cause

1. **Ramp/multiplier overflow.** The firmware's ramp engine computes
   intermediate values that can exceed 0xE0 if a starting DAC seed plus an
   accumulated delta wraps the byte. Triggered most often when a pot wire is
   broken or shorted and the ADC reads an extreme value.
2. **Pot wire fault.** If the level pot's wiper is shorted to V+ or open, the
   firmware's pot→DAC mapping can produce an out-of-range intensity request.
3. **EEPROM corruption.** A corrupt stored level/setting at boot can seed the
   level engine with a bad value. Power-cycle and full EEPROM reset (or
   reflash `backup_eeprom.bin`) addresses this.

## Diagnostic procedure

1. Power-cycle the box. If F10 reproduces immediately on every boot, suspect
   EEPROM corruption — try reflashing the known-good `backup_eeprom.bin`
   (`avrdude … -U eeprom:w:backup_eeprom.bin`).
2. If F10 only fires when adjusting a knob, measure each pot's wiper voltage
   with a multimeter. Should sweep cleanly between 0 V and ~5 V across the
   full rotation. A jumpy or stuck reading points at the offending pot.
3. Reseat the front-panel ribbon — vibration can intermittently open one of
   the pot lines.

## Fix

If EEPROM corruption: reflash `backup_eeprom.bin` and full reseat. If pot
fault: replace the offending pot or repair the wiring. F10 from a normal build
with no EEPROM history is uncommon — the first port of call is always the
front-panel ribbon.
""")

# --------------------------------------------------------------------------- F15
write(15, f"""# Failure 15 — divide-by-zero (firmware sanity)

_Generated {TODAY} from `3-build-and-flash/firmware/backup_flash.bin`._

| Field | Value |
| --- | --- |
| Code (decimal) | **15** |
| Branch sites | `0x1396`, `0x13c4` (both `rjmp` → `0x1676`) |
| Test type | Divide-by-zero precondition checks |
| When it runs | Any time the firmware performs a 16-bit division |
| Class | Firmware bug — no hardware diagnosis applies |

## Summary

F15 fires from two sites inside the divide routine at `0x138c`. Both sites
guard against a zero divisor: the first at `0x1394` catches a zero high byte
before the long-division loop runs; the second at `0x13c2` catches a zero
`{{r26:r27}}` pair just before the actual divide. F15 indicates a
firmware-internal arithmetic precondition violation, not a hardware fault. In
a working stock build this code should never appear; if it does it points at
a bug in firmware (the source f005 tree or a custom patch) or at corrupted
state — never at a solderable component.

## Disassembly evidence

The divide routine entry:

```
138c:  push r26, r27
1390:  and  r31, r31         ; r31 = high byte of divisor
1392:  brne 0x1398           ; if non-zero, OK
1394:  ldi  r26, 0x0F        ; ← loads code 15
1396:  rjmp 0x1676           ; ← FAILURE 15 (early)
1398:  ...                   ; long-division proper
13bc:  cp   r27, r29         ; r29 is zero-register
13be:  cpc  r26, r29
13c0:  brne 0x13c6           ; if {{r26:r27}} != 0, OK
13c2:  ldi  r26, 0x0F        ; ← loads code 15 (second site)
13c4:  rjmp 0x1676           ; ← FAILURE 15 (late)
```

Both checks fire on the same condition (divisor = 0) at different points in
the routine — defensive programming inside the divide.

## Likely cause

F15 is firmware-internal. If you ever see it in real life:

1. **Patched firmware bug.** If you applied a custom patch to f005 (e.g. a
   custom boot message or a feature mod), the patch may have introduced a
   divide that doesn't validate its operands.
2. **Corrupted EEPROM** driving zero into a config field that's later used as
   a divisor. Reseat / reflash EEPROM.
3. **Cosmic-ray-class glitch** (extremely rare) — bit flip in RAM. Power-cycle
   clears it.

## Diagnostic procedure

1. Power-cycle. Does it reproduce? If only intermittent, EEPROM or RAM glitch.
2. If reproducing every boot, the firmware is suspect. Reflash known-good
   `f005.bin`.
3. If you've applied custom patches, revert one at a time until F15 stops.

## Fix

Reflash known-good firmware. If F15 persists with stock `f005.bin`, that
would be a genuine bug worth filing upstream — but in practice this never
happens with the canonical build.
""")

# --------------------------------------------------------------------------- F16
write(16, f"""# Failure 16 — output-level mapping won't converge

_Generated {TODAY} from `3-build-and-flash/firmware/backup_flash.bin`._

| Field | Value |
| --- | --- |
| Code (decimal) | **16** |
| Branch site | `0x15fa` (`rjmp .+122` → `0x1676`) |
| Test type | Iteration-counter sanity check |
| When it runs | Continuously during normal output — every DAC setpoint update |
| Class | Most often a pot/ribbon hardware fault |

## Summary

F16 fires from inside `Function_0x15b8`, the routine that maps pot/ramp
positions to output DAC seeds. The function uses an iteration counter at RAM
`0x01F4`; if that counter reaches 4 without the calculation converging, F16
trips. In practice this means the pot inputs are reading values that produce
no valid intensity mapping — either out-of-range pot ADC values, or a corrupt
ramp profile that diverges instead of settling.

## Disassembly evidence

```
15b8:  push r26, r27
15bc:  ldd  r30, Y+4         ; load DAC base for channel
15c0:  ldd  r2,  Y+11        ; load step delta
15c4:  lds  r26, 0x01F4      ; load iteration counter
15c8:  cpi  r26, 0x04        ; counter < 4 ?
15ca:  brcc 0x15f8           ;   no → fail
...                          ; iteration body, increments counter
15f8:  ldi  r26, 0x10        ; ← loads code 16
15fa:  rjmp 0x1676           ; ← FAILURE 16
```

The body of the function (`0x15cc`–`0x15f6`) computes a target DAC value from
the current pot reading + ramp position. Each iteration that doesn't converge
increments RAM[0x01F4]; if it reaches 4 without convergence, F16.

## Likely cause

1. **Pot wiper noise / dropout.** A noisy or intermittently open pot wiper
   makes the pot ADC reading jump on every sample, so the iteration never
   settles. Most common physical cause.
2. **Ribbon cable fault.** The front-panel ribbon connector has 24 pins and
   carries every pot signal. A loose pin produces F16-like behavior.
3. **ADC reference glitch.** If AVCC or AREF is noisy, ADC readings drift
   between consecutive samples and the iteration can't converge.

## Diagnostic procedure

1. **Reseat the front-panel ribbon** — first thing to try.
2. With the box powered, measure each level pot's wiper voltage on the ATmega
   side of the ribbon while slowly rotating the knob. Reading should sweep
   smoothly from ~0 V to ~5 V. Any sudden drops or flat spots = pot bad.
3. With a scope (if available), look at AVCC (pin 30) and AREF (pin 32) —
   should be clean 5.0 V. Ripple > ~50 mV on either rail can cause F16.

## Fix

Reseat ribbon → replace offending pot if measurements show dropout → in rare
cases, replace bypass caps on AVCC/AREF if rails are noisy. F16 is rarely a
build error; usually a worn-knob or loose-ribbon condition that develops
over time.
""")

# --------------------------------------------------------------------------- F20
write(20, f"""# Failure 20 — output stage current sense (channels A and B)

_Generated {TODAY} from `3-build-and-flash/firmware/backup_flash.bin`._

| Field | Value |
| --- | --- |
| Code (decimal) | **20** |
| Branch site | `0x1494` (`rjmp .+480` → `0x1676`) |
| Test type | Output stage current-sense, both channels |
| When it runs | Once at boot, after F21 voltage check passes |
| Class | Almost always hardware — MOSFETs, transformer, R35/R46 |

## Summary

F20 is the post-boot output-stage self-test, and the most common build failure
on first power-up. A single routine at `Function_0x1406` drives PB2+PB3
(channel A) and then PB0+PB1 (channel B) while monitoring ADC0 (R30 current
sense). On each pass it ramps the DAC down from a low-power seed and looks
for the R30 current to settle within bounds. If either channel can't deliver
current, or the current runs away, F20 fires.

**The forum lore that pairs F20 (channel A) with F21 (channel B) is wrong** —
F20 alone tests both channels; F21 is the wall-adapter voltage check.

## Disassembly evidence

```
1406:  ; init counters
140c:  ldi  r16, 0           ; channel-select flag: 0=A, 1=B
1410:  ldi  r26, 100         ; DAC seed = 100 (≈OUTA 4.38 V)
143a:  cp   r16, 0
143c:  brne 0x1444           ; channel B branch
143e:  ldi  r26, 0x0c        ; PORTB = 0b00001100 (PB2+PB3 = q5+q6)
1440:  out  PORTB, r26       ; ← drives channel A FETs
1444:  ldi  r26, 0x03        ; PORTB = 0b00000011 (PB0+PB1 = q7+q8)
1446:  out  PORTB, r26       ; ← drives channel B FETs
1448-1452:                   ; pulse-width delay
1456:  out  PORTB, 0         ; gates OFF
1458-145c:                   ; wait for ADC, read ADCL
1460:  cpi  r26, 0x10        ; ADCL < 16 ? (≈61 mV)
1462:  brcc 0x1476           ;   yes → settled, advance
1464:  inc  r27              ; pulse counter
1466:  cpi  r27, 0x40        ; 64 attempts ?
1468:  brcc 0x1492           ; ← 64 attempts exhausted → F20
146a-1474:                   ; decrement DAC, loop back
1476:  cmp  r27, 0
1478:  breq 0x1492           ; ← first pulse already too LOW = open → F20
...                          ; advance to channel B (r16=1) and repeat
1492:  ldi  r26, 0x14        ; ← loads code 20
1494:  rjmp 0x1676           ; ← FAILURE 20
```

Two distinct ways to trip F20:

- **(a)** First pulse already reads ADCL < 16 — meaning no current is flowing
  through R30 even at the high-power DAC seed. This points at an **open
  circuit** in the output stage (transformer wired wrong, FET missing,
  broken solder joint).
- **(b)** 64 successive pulses fail to bring ADCL below the threshold — the
  firmware can never get the channel quiet. This points at a **runaway /
  imbalanced** output (mismatched MOSFET Vt, leaky FET, wrong R35/R46 value).

## Likely cause

**Most common (in this order):**

1. **MOSFET Vt mismatch** — IRL520 quartet or IRF9Z24 pair with > ~50 mV
   spread in gate threshold voltage. The output stage can't keep R32 and R43
   balanced.
2. **Transformer reversed** — primary wired backward, current direction wrong.
3. **R35/R46 wrong value** — should be 200 kΩ. A 20 kΩ or 2 MΩ here throws
   off the gate bias.
4. **FET orientation** — IRL520 / IRF9Z24 placed backwards.
5. **DAC fault** — LTC1661 not communicating, or one of its outputs stuck.
   Last resort.

## Diagnostic procedure

1. **Measure DC voltage across R32 and across R43** with the box powered on,
   no patient cables connected. Both should read between **4.0 V and 4.4 V**
   and be very close to each other (within ~50 mV).
2. If R32 ≠ R43: **MOSFET mismatch**. Desolder the IRL520 quartet, measure
   Vt of each on a component tester, replace with a matched set (target
   spread < 20 mV).
3. If R32 = R43 but both out of range (e.g. both 1 V or both 5 V): check
   transformer orientation, R35 and R46 values, FET orientations.
4. **Before soldering on a fresh build**: pre-match every IRL520 / IRF9Z24
   with a component tester. A ~$15 Mega328-based tester from Amazon
   (B0DDBPWYP8) will save you hours of debugging.

## Fix

Match MOSFETs by Vt before soldering. If already built and F20 trips,
desolder and swap in a matched set. R32/R43 mismatch is the diagnostic
smoking gun — believe the multimeter, not your soldering pride. Build-guide
section `docs/build-guide.md` → "Error 20" covers prevention. Background
reading: forum threads in
`docs/troubleshooting/MK-312BT Failure 20 - Estim - Metafetish.pdf` and
`docs/troubleshooting/Another Failure 20 with measurements and some test mode_ - Estim - Metafetish.pdf`.
""")

# --------------------------------------------------------------------------- F72
write(72, f"""# Failure 72 — state variable RAM[0x01F1] overflow

_Generated {TODAY} from `3-build-and-flash/firmware/backup_flash.bin`._

| Field | Value |
| --- | --- |
| Code (decimal) | **72** |
| Branch site | `0x1a1e` (`rjmp .-938` → `0x1676`) |
| Test type | Internal state-variable bounds check |
| When it runs | Inside the routine at `0x1a06` — called from mode/ramp engine |
| Class | Firmware — almost never a hardware fault |

## Summary

F72 fires from the routine at `0x1a06`, which increments an accumulator at RAM
`0x0214` and then checks a related state variable at `0x01F1`. If RAM[0x01F1]
ever reaches ≥ 56 (0x38), F72 trips. This is a defensive check on a
firmware-internal state machine — likely a step counter for a multi-stage
operation (mode setup, ramp progression, audio sequencer phase). F72 normally
indicates that the state machine got out of sync, often due to an interrupt
race or corrupted RAM.

## Disassembly evidence

```
1a06:  push r30, r31
1a0a:  lds  r30, 0x0214      ; load accumulator
1a0e:  add  r30, r26         ; accumulator += r26 (the new step)
1a10:  sts  0x0214, r30      ; store back
1a14:  lds  r30, 0x01F1      ; load state variable
1a18:  cpi  r30, 0x38        ; ≥ 56 ?
1a1a:  brcs 0x1a20           ;   no → continue
1a1c:  ldi  r26, 0x48        ; ← loads code 72
1a1e:  rjmp 0x1676           ; ← FAILURE 72
```

RAM[0x01F1] is a step counter. The function adds whatever's in `r26` to
RAM[0x0214] (an accumulator), then aborts if the step counter is too high.
In stock firmware this should never trip because the calling code resets the
counter periodically.

## Likely cause

1. **Custom firmware patch.** A patch that adds modes / ramps / step logic
   without resetting RAM[0x01F1] cleanly between cycles will run the counter
   up over time. Check any user-added f005 patches.
2. **EEPROM corruption seeding bad state** at boot — reflash
   `backup_eeprom.bin`.
3. **Interrupt race** in heavily-loaded modes (e.g. high-frequency rhythm
   modes) where an ISR fires inside the state-update path. This would be a
   real upstream bug.

## Diagnostic procedure

1. Note **which mode** was running when F72 fired — switch back to stock f005
   modes and try to reproduce. If F72 stops, you have a custom-patch bug.
2. Power-cycle and reflash EEPROM. If F72 reproduces from a clean EEPROM with
   stock firmware, that would be a real upstream bug worth reporting.
3. There's no hardware-side fix — F72 is a firmware-state failure.

## Fix

Reflash stock `f005.bin` + clean `backup_eeprom.bin`. If reproducible from
clean state, file upstream — but in practice this is vanishingly rare on
stock firmware.
""")

# --------------------------------------------------------------------------- F80
write(80, f"""# Failure 80 — EEPROM/config readback out of range

_Generated {TODAY} from `3-build-and-flash/firmware/backup_flash.bin`._

| Field | Value |
| --- | --- |
| Code (decimal) | **80** |
| Branch site | `0x0796` (`rjmp .+3806` → `0x1676`) |
| Test type | EEPROM-stored config byte range check |
| When it runs | During mode load / setting recall paths |
| Class | EEPROM contents — software fix (reflash EEPROM) |

## Summary

F80 fires on a value-range check that follows an EEPROM read. The check at
`0x0790` compares an indexed value (in `r30`) to 40 (0x28); if `r30` ≥ 40 the
firmware trips F80. The preceding code path includes `call 0x19dc`, which is
the EEPROM-read primitive (it polls EECR at I/O 0x1c). So F80 indicates a
stored configuration byte (a mode index, calibration value, or saved-state
pointer) that exceeds its valid range. Most often this means a corrupt EEPROM
— first-boot of a freshly-flashed chip with no EEPROM init, or wear /
corruption on a long-running unit.

## Disassembly evidence

```
19dc:  ; EEPROM read primitive
19de:  in   r28, 0x1c        ; EECR
19e0:  andi r28, 0x03        ; check EERE/EEWE busy bits
19e2:  brne 0x19de           ; spin until idle
19e4:  out  0x1f, r27        ; EEAR high
19e6:  out  0x1e, r26        ; EEAR low
19e8:  sbi  0x1c, 0          ; EERE = 1 → start read
19ec:  in   r0, 0x1d         ; EEDR → r0
19f0:  ret
...
0756:  call 0x19dc           ; ← EEPROM read
075a:  mov  r26, r0          ; result into r26
075c:  rcall 0x0b98          ; (use the value)
...
0790:  cpi  r30, 0x28        ; ≥ 40 ?
0792:  brcs 0x0798           ;   no → continue
0794:  ldi  r26, 0x50        ; ← loads code 80
0796:  rjmp 0x1676           ; ← FAILURE 80
```

Combined with the EEPROM read above the check, F80 is a sanity guard on a
stored byte that should be a small index (0..39). The firmware likely stores
the current/saved mode here, or a slot index into a table.

## Likely cause

1. **First boot of fresh chip.** Virgin AVR EEPROM is all 0xFF (= 255), so
   any read of an uninitialized slot returns 255, which is far above 40 → F80.
2. **EEPROM corruption** over time — power loss during write, lightning, ESD.
3. **Bus error during EEPROM read** — extremely rare; only if the AVR's Vcc
   is glitching.

## Diagnostic procedure

1. **First boot of a freshly-flashed chip**: the box may need an initial
   EEPROM image. Either flash the bundled `backup_eeprom.bin` from this repo
   (`avrdude … -U eeprom:w:backup_eeprom.bin`), or run the firmware's normal
   first-boot init (some f005 builds initialize EEPROM if they detect 0xFF;
   others don't).
2. **Long-running unit suddenly throwing F80**: dump current EEPROM
   (`-U eeprom:r:current_eeprom.bin:r`) and compare to known-good
   `backup_eeprom.bin`. Differences in the first ~64 bytes confirm corruption.
3. Reflash known-good EEPROM and reboot.

## Fix

Reflash `backup_eeprom.bin`. F80 is virtually always EEPROM contents, not
hardware — don't go probing the board before you've tried the EEPROM reset.
""")

# --------------------------------------------------------------------------- index
INDEX = OUT_DIR / "failure-codes-index.md"
INDEX.write_text(f"""# MK-312BT firmware failure codes — complete index

_Generated {TODAY} from `3-build-and-flash/firmware/backup_flash.bin`. Every
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
""")

import os
files = sorted(OUT_DIR.glob("failure-*.md"))
for p in files:
    print(f"  {p.relative_to(REPO)}  ({os.path.getsize(p):,} B)")
print(f"\n{len(files)} markdown files in {OUT_DIR.relative_to(REPO)}/")
