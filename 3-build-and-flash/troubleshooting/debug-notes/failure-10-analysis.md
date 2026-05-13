# Failure 10 — DAC write value out-of-range (≥ 224)

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
