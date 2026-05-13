# Failure 16 — output-level mapping won't converge

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
