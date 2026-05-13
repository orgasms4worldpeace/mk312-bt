# Failure 80 — EEPROM/config readback out of range

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
