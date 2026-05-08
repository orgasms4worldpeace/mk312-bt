# Failure 72 — state variable RAM[0x01F1] overflow

_Generated 2026-05-04 from `3-build-and-flash/firmware/backup_flash.bin`._

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
