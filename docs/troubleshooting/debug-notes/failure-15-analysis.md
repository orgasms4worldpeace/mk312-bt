# Failure 15 — divide-by-zero (firmware sanity)

_Generated 2026-05-04 from `3-build-and-flash/firmware/backup_flash.bin`._

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
`{r26:r27}` pair just before the actual divide. F15 indicates a
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
13c0:  brne 0x13c6           ; if {r26:r27} != 0, OK
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
