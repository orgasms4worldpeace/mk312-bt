# Failure 21 — firmware, circuit, and intermittent-boot analysis

This is an evidence-based engineering report for the v1.4 board running patched
buttshock-et312-frankenbutt **f005** firmware. Every non-trivial claim cites
its source. Where I could not confirm something through the disassembly,
schematic, datasheet, or an authored third-party source, I say so explicitly.

The most important finding up front: **Failure 21 in this firmware is NOT a
"channel B mirror of Failure 20". F21 is a power-supply / wall-adapter
voltage check that runs once at boot. The forum lore that pairs F20/F21 as
A-vs-B output tests is wrong.** F20 already tests both channels in a single
routine (it loops twice, once with `r16=0` for channel A drive, once with
`r16=1` for channel B drive — see §1.2).

---

## 1. What "Failure 21" means in firmware

### 1.1 String location and the error_handler

`Failure ` is stored as an 8-byte field at flash offset `0x1DF0` (verified by
`xxd backup_flash.bin`):

```
00001df0: 4661 696c 7572 6520 5077 7220 4c65 763a  Failure Pwr Lev:
```

The string is loaded by the **error_handler** at `0x1676`. From
`avr-objdump -m avr5 -b binary -D backup_flash.bin`:

```
1676:  2a 2f       mov   r18, r26       ; r26 = failure code from caller
1678:  a4 e6       ldi   r26, 0x64      ; 100 -- string index "Failure"
167a:  38 de       rcall .-912    ;  0x12ec  ; show_Text_on_Display
167c:  ab ec       ldi   r26, 0xCB      ; 203 -- string index "Shut Off Power"
167e:  36 de       rcall .-916    ;  0x12ec
1680:  f8 e0       ldi   r31, 0x08      ; LCD position
1682:  e2 2f       mov   r30, r18       ; failure number
1684:  19 de       rcall .-974    ;  0x12b8  ; display_number_on_display
1686:  a0 e0       ldi   r26, 0x00
1688:  29 de       rcall .-942    ;  0x12dc
168a:  f8 94       cli
168c-16b6:                                  ; force outputs safe + idle loop
```

This routine is annotated `error_handler` in the buttshock annotated
disassembly file
`/tmp/buttshock-fw/annotation/312-16-decrypted-combined.tags`:

> `0x1676  L  error_handler  CallTable_23_37_38_39`
> `0x167a  T  display "Failure", spaces, failure num`
> `0x1688  T  display "Shut off power"`

### 1.2 All four call sites that load a failure code

I searched the disassembly for every `ldi r26, 0x14` (=20) and `ldi r26, 0x15`
(=21):

```
0x072e:  ldi r26, 0x14   ; rcall 0xb98          ← runtime, NOT error_handler
0x0736:  ldi r26, 0x15   ; rcall 0xb98          ← runtime, NOT error_handler
0x1492:  ldi r26, 0x14   ; rjmp  0x1676 (F20)   ← BOOT self-test
0x16e2:  ldi r26, 0x15   ; rjmp  0x1676 (F21)   ← BOOT self-test
```

The `0xb98` callee is the SPI-DAC write path; `0x14`/`0x15` there are DAC
levels, not failure codes. Only `0x1492` and `0x16e2` actually trigger the
error handler. So the firmware emits exactly **two** boot failure codes:
F20 from `0x1492` and F21 from `0x16e2`.

#### Failure 20 (`0x1492`) — both channels through R30

The F20 test is the loop at `0x1406-0x1494`. Pseudocode (from the buttshock
annotated dump, identical bytes to our `backup_flash.bin`):

```
Function_0x1406:
1406:  ldi r26, 0xff
1408:  mov r6, r26
140a:  mov r11, r26
140c:  ldi r16, 0       ; channel-select flag: 0=A, 1=B
140e:  ldi r27, 0       ; pulse counter
1410:  ldi r26, 100
1412:  std Y+4, r26     ; DAC initial = 100  (this is the OUTA=4.38V seed)
1414:  std Y+5, r26     ; DAC initial = 100

Label_0x1416:
1416:  rcall 0x15b8     ; setup_0x205_x206_based_on_pot_and_ramp_and_levels
1418:  rcall 0x1456     ; send_data_to_spdr  (DAC update)
141a-1430: ADMUX/ADCSR setup, three sleeps (for ADC settle)

Label_0x1432:
1432:  rcall 0x15b8     ; refresh DAC value
1434:  rcall 0x1456
1438:  sleep 3
143a:  cmp r16, 0
143c:  brne Label_0x1444
143e:  ldi r26, 0x0c    ; PORTB = 0b00001100 ; q5=PB2=1, q6=PB3=1, q7=PB0=0, q8=PB1=0
1440:  out PORTB, r26                          ; ← drives channel A only (Q1+Q2 open)
1442:  rjmp Label_0x1448

Label_0x1444:
1444:  ldi r26, 0x03    ; PORTB = 0b00000011 ; q5=PB2=0, q6=PB3=0, q7=PB0=1, q8=PB1=1
1446:  out PORTB, r26                          ; ← drives channel B only (Q4+Q5 open)

Label_0x1448:
1448:  ldi r26, 2 ; sleep 2          ; pulse width
144c:  out ADCSR, 0xC6                ; start single ADC conversion
1452:  short delay loop
1456:  out PORTB, 0                   ; gates OFF
1458:  loop until ADIF set
145c:  in r26, ADCL
145e:  in r31, ADCH
1460:  cpi r26, 0x10                  ; ADCL < 16 ? (i.e. ADC < ~313 mV ref-AVCC, ≈61 mV unscaled)
1462:  brcc Label_0x1476              ; PASS -> exit & advance to next channel or finish
1464:  inc r27                        ; pulse counter
1466:  cpi r27, 0x40                  ; 64 attempts?
1468:  brcc 0x1492                    ; → F20  ("never settled in 64 attempts")
146a-1474:                            ; decrement DAC, save, loop back to 0x1432
1476:  cmp r27, 0
1478:  breq 0x1492                    ; first pulse already too LOW = open circuit → F20
... continues into channel-B half ...

0x1492:  ldi r26, 0x14 ; rjmp 0x1676  ; ← FAILURE 20
```

**Conclusion on F20:** A single routine drives PB2+PB3 for channel A, then
PB0+PB1 for channel B (the `r16` flag), and on each pass it reads ADC0
(PA0 = R30 sense). The pass criterion: starting from a low-power DAC value,
each successive pulse must produce a measurable but bounded current through
R30, settling within 64 iterations.

### 1.3 Failure 21 (`0x16e2`) — boot voltage check

The F21 test is **completely separate** from the F20 channel test. It is
a small routine at `0x16b8` called once from RESET at `0x151a`:

```
0x151a:  rcall 0x16b8   ; (boot self-test -- voltage sense)
```

Disassembly of `0x16b8` (raw bytes match our `backup_flash.bin`):

```
Function_0x16b8:                ; Y points at 0x4060
16b8:  ldi r26, 0x56            ; seed
16ba:  std Y+2, r26             ; pre-seed mem[0x4062]  (ADC2 storage slot)
16bc:  ldi r26, 0x85            ; seed
16be:  std Y+3, r26             ; pre-seed mem[0x4063]  (ADC3 storage slot)
16c0:  rcall 0x0b1e             ; enable_ADC_and_set_r17[3]
16c2:  sbrc r17,3 / rjmp .-4    ; wait for ISR to clear "ADC running"
16c6:  rcall 0x0b1e             ; (auto-cycled ADMUX, see §1.4)
16c8:  sbrc r17,3 / rjmp .-4
16cc:  rcall 0x0b1e
16ce:  sbrc r17,3 / rjmp .-4
16d2:  ldd r26, Y+3             ; read averaged ADC3 result (battery rail sense)
16d4:  cpi r26, 0x8E            ; 142
16d6:  brcc Label_0x16dc        ; if ADC3 ≥ 142 → continue
16d8:  jmp 0x590                ; otherwise: display_battery_low
16dc:  ldd r27, Y+2             ; read averaged ADC2 result (wall-adapter sense)
16de:  cpi r27, 0x92            ; 146
16e0:  brcs Label_0x16e6        ; if ADC2 < 146 → continue
16e2:  ldi r26, 0x15            ; ← FAILURE 21
16e4:  rjmp 0x1676              ; → error_handler
```

After the F21 check passes, `0x16e6-0x16fc` derives a `power_status_bits`
bitmap into mem[0x0215]:

- bit 0 set if ADC3 < `0xB2` (178) → "we have a battery"
- bit 1 set if ADC2 ≥ `0x40` (64)  → "PSU/charger is connected"
- if ADC2 ≥ `0x63` (99) but the check at `0x16de` passed (< 146) the firmware
  also computes a battery-level percentage at `0x171a` from the ADC2/ADC3
  pair, then proceeds to `Function_0x1406` (the F20 channel test).

**So at boot the firmware runs F21 first (voltage sanity), then F20 (output
stage sanity). F21 trips ONLY if the wall-adapter sense reads too high.**

### 1.4 Why two ADC results from the same `enable_ADC_and_set_r17[3]` call

`0x0b1e` always writes `ADMUX = 0x01` (REFS=00 AVCC, MUX=00001 → ADC1):

```
0b1e:  ldi r26, 0x01 ; out ADMUX, r26
0b22:  ldi r26, 0xCB ; out ADCSR, r26   ; ADEN|ADSC|ADIE, /8
0b26:  ori r17, 0x08                    ; flag "ADC running"
```

The ADC ISR (`ADC_Conversion_Complete`, `0x106e`) however does an
**ADMUX increment after each conversion**:

```
106e:  ...
1072:  in r28, ADMUX                   ; r28 = current MUX
1074:  subi r28, 0xA0                  ; r28 = MUX + 0x60 = SRAM ptr low byte
1076:  in r24, ADCL ; r25 = ADCH ; right-shift 4 → 8-bit result in r24
1082-108e: read prior value at SRAM[Y], average with r24, store
10ca:  in r23, ADMUX
10cc:  inc r23
10ce:  sbrs r23, 3                     ; if MUX would advance to 8 → done
10d0:  rjmp Label_0x10de
10d2:  out ADMUX, r23                  ; otherwise: advance to next channel
10d4:  ldi r23, 0xCC ; out ADCSR, r23  ; and start new conversion
```

So a single call to `0x0b1e` **starts** one conversion on ADC1, and the ISR
**auto-chains** ADC2, ADC3, ... through ADC7 by rewriting ADMUX between
conversions. Results land at SRAM `0x4060 + channel_index`. Y in
`Function_0x16b8` is set up so that `Y+2 = 0x4062` (ADC2 result) and
`Y+3 = 0x4063` (ADC3 result), matching the buttshock annotation:

> `0x1766  T  display 0x4063 (Battery Voltage ADC3)`

The three explicit `rcall 0x0b1e` in `0x16b8` give the ISR enough chained
conversions for the auto-cycled values at offsets 2 and 3 to settle
(seeded with 0x56 and 0x85 to give the ISR's averager a defined starting
point).

### 1.5 Numeric thresholds vs. the v1.4 schematic

Page 2 of the v1.4 schematic shows two voltage dividers feeding PA2 (ADC2)
and PA3 (ADC3). Both are tied to the AREF/AVCC reference (5.0 V).

The annotation file calls **ADC3 = "Battery Voltage"** and the F21 thresholds
make sense ONLY with the schematic-actual divider ratios. Working backwards:

| ADC | Pin | Divider (page 2)         | Net at top of divider | 8-bit ADC reading at threshold |
|-----|-----|--------------------------|-----------------------|--------------------------------|
| 2   | PA2 | R3 100kΩ / R4 20kΩ to GND | "U+" (wall-adapter, pre-LM2941T) | F21 trips at ADC2 ≥ **0x92 (146)** → 2.85 V at PA2 → **U+ ≥ ~17.1 V** |
| 3   | PA3 | R5 10kΩ / R6 3.3kΩ to GND | "+12V" rail (battery side, post-D1) | "battery low" at ADC3 < **0x8E (142)** → 2.77 V at PA3 → **+12V rail < ~11.2 V** |

(D5 1N4148 sits cathode-to-PA2 to clamp surges from U+; this does not affect
the divider ratio in normal operation.)

These thresholds match the third-party debug write-up from `hvprvbo`
(see §5).

### 1.6 The pre-test PORTB/PORTD setup at 0x14e0-0x14ee

Before either failure routine runs the firmware sets up I/O. From
`0x14d4-0x14ee` of `backup_flash.bin`:

```
14d8:  ldi r26, 0xBF ; out 0x17, r26    ; DDRB  = 1011 1111  (PB6 = MISO input)
14dc:  ldi r26, 0xFF ; out 0x14, r26    ; DDRC  = 1111 1111  (LCD bus, all out)
14e0:  ldi r26, 0xF2 ; out 0x11, r26    ; DDRD  = 1111 0010  (PD7..4,PD1 out; PD3,PD2,PD0 in)
14e4:  ldi r26, 0x70 ; out 0x12, r26    ; PORTD = 0111 0000  (PD6,5,4 high)
14e8:  ldi r26, 0x10 ; out 0x18, r26    ; PORTB = 0001 0000  (PB4 = DAC CS high; gates OFF)
14ec:  ldi r26, 0x80 ; out 0x08, r26    ; TCCR0 setup
```

So the F20 channel test fires from a known-clean state with all FET-driver
gates OFF (PORTB = 0x10 → only PB4 high, used as DAC chip-select).

There is **no explicit pre-test stim pulse before the ADC reads in F21**.
The "pulse loop" at `0x16a2-0x16b6` is the *post-failure* watchdog-keepalive
loop reached only via `error_handler`'s rjmp at `0x16b6 → 0x16a2`, not the
pre-test pulse generator. F21 reads ADC2/ADC3 with the outputs OFF.

---

## 2. Channel B circuit reference (v1.4 schematic page 5)

Page 4 of the schematic is **audio I/O + serial/radio interface**, NOT the
output stages. The output power section is on **page 5**. Below is the full
channel B inventory together with channel A as a reference.

### 2.1 Output drive — channel A (page 5, top half, transformer TR3)

| Designator | Value / Part | Function |
|---|---|---|
| Q1 | IRL520N N-MOSFET | Low-side gate, driven by **PB2** via R38 |
| Q2 | IRL520N N-MOSFET | Low-side gate, driven by **PB3** via R41 |
| Q3 | IRF9224 P-MOSFET | High-side, gate driven by U10A op-amp output via R39 |
| U10A | LM358N op-amp | Linear regulator for Q3 gate (sets channel A power level) |
| TR3 | 42TU200 transformer | Pulse step-up to OUTPUT A jack J6 |
| R30 | 0.27 Ω (build) / 0.5 Ω (BOM) | **Channel A current sense** to GND. Top of R30 → PA0/ADC0 |
| R31 | 100 kΩ | DAC OUT-A → U10A (+) input |
| R32 | 100 kΩ | U10A (+) input → +5V (sets DAC offset) |
| R33 | 100 kΩ | U10A (+) input → GND |
| R34 | 100 kΩ | U10A (-) input → +9V1 |
| R35 | 200 kΩ | U10A (-) input → GND |
| R36 | 100 kΩ | U10A feedback |
| R37 | 100 kΩ | Q1 gate pull-down |
| R38 | 10 kΩ | PB2 → Q1 gate series |
| R39 | 10 kΩ | U10A output → Q3 gate |
| R40 | 100 kΩ | Q2 gate pull-down |
| R41 | 10 kΩ | PB3 → Q2 gate series |
| C38 | 0.1 µF | U10A bypass |
| C39 | 0.1 µF | Q3 gate decoupling |

### 2.2 Output drive — channel B (page 5, bottom half, transformer TR4)

| Designator | Value / Part | Function |
|---|---|---|
| Q4 | IRL520N N-MOSFET | Low-side gate, driven by **PB0** via R49 |
| Q5 | IRL520N N-MOSFET | Low-side gate, driven by **PB1** via R52 |
| Q6 | IRF9224 P-MOSFET | High-side, gate driven by U10B op-amp output via R50 |
| U10B | LM358N op-amp | Mirror of U10A — sets channel B power level |
| TR4 | 42TU200 transformer | Pulse step-up to OUTPUT B jack J7 |
| R42 | 100 kΩ | DAC OUT-B → U10B (+) input |
| R43 | 100 kΩ | U10B (+) input → +5V (mirror of R32) |
| R44 | 100 kΩ | U10B (+) input → GND (mirror of R33) |
| R45 | 100 kΩ | U10B (-) input → +9V2 (mirror of R34) |
| R46 | 200 kΩ | U10B (-) input → GND (mirror of R35) |
| R47 | 100 kΩ | U10B feedback (mirror of R36) |
| R48 | 100 kΩ | Q4 gate pull-down (mirror of R37) |
| R49 | 10 kΩ | PB0 → Q4 gate series (mirror of R38) |
| R50 | 10 kΩ | U10B output → Q6 gate (mirror of R39) |
| R51 | 100 kΩ | Q5 gate pull-down (mirror of R40) |
| R52 | 10 kΩ | PB1 → Q5 gate series (mirror of R41) |
| C40 | 0.1 µF | Q6 gate decoupling (mirror of C39) |

### 2.3 DAC for both channels

| Designator | Value / Part | Function |
|---|---|---|
| U8 | LTC1661 dual 10-bit DAC | One DAC drives U10A, the other drives U10B. SPI on PB5 (MOSI), PB7 (SCK), CS via PD4 (per the LCD-init code's `cbi 0x12,4` and tag "pin D4 is DAC CS") |
| C41 | 0.1 µF | LTC1661 bypass |

### 2.4 Asymmetries and answer to "what is the channel B sense path?"

**There is no channel B current-sense resistor that is its own component.**
Channel B does not have its own equivalent of R30. Channel A's R30 (0.27 Ω
between PA0 and GND) is the only AVR-pin-connected current sense in the
output stages.

The wire that runs from R30 to GND also routes back to **both transformer
primary returns** on page 5 (the "common low side" between Q1/Q2 of channel A
and Q4/Q5 of channel B — both pairs of N-FET sources go to this same node).
That is what allows F20 to test channel B by gating PB0/PB1 and still
reading the resulting current via PA0/R30. F20's two-phase loop (`r16=0`
then `r16=1`) selects which channel's low-side FETs to open. Only one
channel's high-side P-FET (Q3 or Q6) is enabled at a time by setting the
DAC output for that channel; the other channel's DAC is at idle and
contributes essentially zero current to R30.

**Practical consequence for debug probing:** Channel B does NOT have an
independent ADC feedback. Probing PA0 during boot self-test will show
both channel A pulses (when r16=0) and channel B pulses (when r16=1) on
the same node.

---

## 3. ADC sense paths (page 2 of schematic)

The relevant analog-input nets visible on page 2:

| ADC | AVR pin | Path to AVR pin | Reads what |
|---|---|---|---|
| ADC0 | PA0 (pin 40) | Top of R30 (0.27Ω) → straight to PA0; also connected via the shared low-side return rail to Q1/Q2/Q4/Q5 sources | Current through whichever channel's low-side FETs are open |
| ADC1 | PA1 (pin 39) | Front-panel ribbon J11-5; on page 4 → C26 0.1µF + C25 1nF + R20 100kΩ to GND, into U2B (LM324) (+) input. U2B is fed from JP2 AUX LINE IN audio chain. | Audio multi-adjust input level (annotation: "Multi Adjust Offset ADC1") |
| **ADC2** | **PA2 (pin 38)** | **R3 100kΩ from "U+" (raw VDC INPUT, J8) → PA2 → R4 20kΩ to GND.** D5 1N4148 cathode at PA2 to GND (clamp). | **Wall-adapter input voltage. F21 threshold: ADC2 ≥ 146 → ~17.1V at U+ → F21** |
| **ADC3** | **PA3 (pin 37)** | **R5 10kΩ from "+12V" rail → PA3 → R6 3.3kΩ to GND.** | **+12V battery-side rail. Battery-low if ADC3 < 142 → ~11.2V → halt at 0x590** |
| ADC4 | PA4 (pin 36) | Front-panel ribbon J11-9 → VR1 LEVEL A pot wiper | Channel-A power knob |
| ADC5 | PA5 (pin 35) | Front-panel ribbon J11-11 → VR2 LEVEL B pot wiper | Channel-B power knob |
| ADC6 | PA6 (pin 34) | Front-panel ribbon → page 4 → D2 1N4148 + R29 100kΩ + C31 1µF (peak-hold) | Audio B half-wave |
| ADC7 | PA7 (pin 33) | Front-panel ribbon → page 4 → D3 1N4148 + R28 100kΩ + C30 1µF (peak-hold) | Audio A half-wave |

There is no ADC sense path dedicated to channel B output. The only feedback
the firmware has from the high-voltage side is via R30 + PA0.

---

## 4. Per-pin probe table for the boot voltage and stage tests

Voltages are measured with respect to board GND; "boot" means within ~50 ms
of releasing the POWER switch and before the LCD lights, on a v1.4 board
running f005.

| AVR pin | Function | Expected at boot (battery only, no charger) | Expected with 15V charger | If wrong, do this |
|---|---|---|---|---|
| **PA0 / ADC0 (pin 40)** | Channel A & B current sense (top of R30) | ~0 mV resting; brief pulses up to ~150 mV during F20 self-test | same | If stuck high (>200 mV with no pulse): Q1/Q2/Q4/Q5 stuck on, or R30 open. Read R30 with DMM (should be 0.27 Ω). |
| **PA1 / ADC1 (pin 39)** | Audio multi-adjust input | ~0 V (no audio); follows multi-adj knob through audio chain | same | If pinned high: ribbon flip / short to +5V on J11. |
| **PA2 / ADC2 (pin 38)** | Wall-adapter sense, divider R3/R4 from U+ | **~0 V** (U+ = 0V on battery only) | **U+ × 20/120 = 0.167 × U+** → 2.50 V at 15V, 2.83 V at 17V (≈F21 threshold) | F21 trip: measure U+ at J8 input. If U+ > 17V → reduce supply. If U+ ≈ 0V on battery and F21 still trips → AVR is reading garbage; suspect ADC reference (AVCC, AREF) or ribbon-induced fault. |
| **PA3 / ADC3 (pin 37)** | Battery rail sense, divider R5/R6 from +12V | **+12V × 3.3/13.3 = 0.248 × Vbat** → 2.97 V at 12.0V, 3.22 V at 13.0V | same (battery + charger float) | If reading < 2.77 V (= ADC < 142) box halts at 0x590 ("battery low"). Measure the +12V rail directly at the cathode of D1 — if rail is OK but PA3 is low: R5 open or R6 short. |
| PA4 / ADC4 (pin 36) | Channel-A LEVEL knob | follows VR1 wiper, 0..5V | same | knob wiring or J11-9 |
| PA5 / ADC5 (pin 35) | Channel-B LEVEL knob | follows VR2 wiper, 0..5V | same | knob wiring or J11-11 |
| PA6 / ADC6 (pin 34) | Audio B peak | 0V (no audio) | same | C31 leaky |
| PA7 / ADC7 (pin 33) | Audio A peak | 0V (no audio) | same | C30 leaky |
| AREF (pin 32) | ADC reference | tied to AVCC = +5V via the AREF cap C16 (18pF) on schematic? Actually AREF and AVCC both feed +5V externally via L1/ferrite. Check both pins read +5.00V ±0.05V. | same | Off by >0.1V → ADC results scaled wrong. Could mimic F21 if AVCC droops. |
| AVCC (pin 30) | ADC supply | +5.00 V | same | If sagging during boot inrush, ADC2/3 reads will be biased. **Check with scope, not DMM.** |
| PB0 / PB1 (pins 1 / 2) | Channel B low-side FET drives | quiet, then 4–6 µs pulses during F20 (r16=1 phase) | same | Stuck high: F20 trip on first pulse |
| PB2 / PB3 (pins 3 / 4) | Channel A low-side FET drives | quiet, then pulses during F20 (r16=0 phase) | same | Stuck high: F20 trip on first pulse |
| PB4 (pin 5) | LTC1661 DAC chip-select | high (idle), goes low only during DAC transfer | same | If stuck low → DAC permanently selected → spurious SPI transfers |
| PB5 / PB7 (pins 6 / 8) | DAC SPI MOSI / SCK | quiet bursts during SPI updates | same | Cross-talk from ribbon → SPI corruption |
| PC0..PC7 (pins 22-29) | LCD bus (4-bit data on PC7:4, RS=PC3, E=PC2, RW=PC1) | 4-bit nibbles + E strobes during init | same | See §6 — this is the LCD path |
| PD0 (pin 14) | RXD (link/serial RX) | high (idle) | same | |
| PD1 (pin 15) | TXD | high (idle) | same | |
| PD2 (pin 16) | INT0 (page 4 ref) | high or low depending on input | same | |
| PD3 (pin 17) | INT1 | similar | same | |
| PD4 (pin 18) | DAC CS via cbi 0x12,4 (annotation: "pin D4 is DAC CS") | high (idle) | same | conflict with PB4? See §6 — this is suspicious. |
| PD5 (pin 19) | OC1A / front-panel | mode-dependent | same | |
| PD6 (pin 20) | ICP / front-panel | mode-dependent | same | |
| PD7 (pin 21) | OC2 / front-panel | mode-dependent | same | |
| RESET (pin 9) | reset (10kΩ pull-up to +5V) | +5V | same | If pulled low at boot → infinite reset; LCD power cycles → can produce a "blocks on top row" stuck-init |
| XTAL1 / XTAL2 (pins 13 / 12) | 8 MHz crystal | sine ~3-5 V p-p | same | If crystal slow to start, boot watchdog may fire before LCD init completes |

---

## 5. Forum & blog quotes — what the community says about F21

The metafetish.club forum is offline (since ~2020-12). The Wayback Machine
returned no usable snapshots within the WebFetch timeout for the specific
F20/F21 thread URLs. However, **one third-party reverse-engineering write-up
remains live and is direct:**

### 5.1 hvprvbo (CrazyEstim) blog, 2021-03-29 — definitive third-party source

URL: https://hvprvbo.blogspot.com/2021/03/mk312-btfailure20-failure21-debug-for.html
PDF mirror: https://drive.google.com/file/d/1gr-n5ldNQqSA_JH1kqPSWMPF73wiGk7i/view?usp=sharing

Verbatim Chinese, with translation. The author built an MK-312-BT v1.2 and
hit F21 followed by F20:

> 1.Failure 21故障
>     故障原因是面板插口处的电源电压不对。MK312-BT的BOM中推荐电源电压15~19V。
>     MK312-BT有一个电源电压检测机制，如图 1所示。图中"V+"结点为前面板电源插
>     口正极。单片机启动时读取AD引脚PA2上的分压，数值不对就会报Failure 21故
>     障。调整电源电压即可解决。

Translation:

> **1. Failure 21**
>     The cause is that the power-supply voltage at the front-panel jack is
>     wrong. The MK-312-BT BOM recommends a 15–19 V supply. The MK-312-BT has
>     a power-supply voltage detection mechanism (figure 1). "V+" in the
>     figure is the front-panel power-jack positive terminal. At MCU
>     startup, the firmware reads the divided voltage on AD pin **PA2**,
>     and if the value is wrong it raises the Failure 21 fault. Adjusting
>     the supply voltage solves it.

For F20 the same article cites a forum user "Sirius" on metafetish.club:

> 根据(Sirius, https://metafetish.club )提供的信息(图 2)，单片机启动时需要分别
> 对A, B两个通道进行测试，每个通道必须满足两个条件：
>     设置OUTA=4.38V， 输出第1个脉冲，要求R30电位低于78.2mV(条件1)。
>     然后每次减小OUTA电位0.016V依次输出脉冲并测量R30电位，要求 在64次以内
>     R30电位高于78.2mV(条件2) 。对于B通道，重复上述过程。

Translation:

> Per Sirius (forum.metafetish.club, fig. 2), at MCU startup the firmware
> must test channels A and B separately, and each channel must satisfy two
> conditions:
>     Set OUTA = 4.38 V, output the first pulse, R30 voltage must be **below
>     78.2 mV (condition 1)**.
>     Then decrease OUTA by 0.016 V each pulse, output pulses and measure
>     R30, requiring R30 voltage to **rise above 78.2 mV within 64 pulses
>     (condition 2)**. Repeat for channel B.

The blog's F20 fix was to **add a 270 kΩ resistor in parallel with R32 and
with R43** (raising the U10A and U10B `+` input bias so Q3/Q6 are not
over-driven on the first pulse), which made `condition 1` pass on the first
attempt for both channels.

This blog post is the most authoritative public reference outside the dead
forum and lines up exactly with the disassembly above.

### 5.2 Wayback Machine search — what is and isn't there

I exhausted the WebFetch tool's timeout against
`https://web.archive.org/web/.../metafetish.club/t/...` for the threads at
`/t/another-failure-20-with-measurements-and-some-test-mode/629`,
`/t/mk-312bt-failure-20/419`,
`/t/mk312bt-firmware-and-function-issues-failure-20-debug-suggestions/1327`,
and `/t/mk312bt-failure-modes-20-and-21/357`. The pre-fetch hook killed every
attempt before content was returned.

Google search returns the metafetish thread titles (so they were indexed
once), but the live forum is offline and the Wayback snapshots either don't
render or aren't fetch-able from this environment. **I could not retrieve
any verbatim forum quotes about F21 from the Wayback Machine** — only the
hvprvbo blog above and the AI-summarised search-snippet wording:

> "**Failure 21** appears with mains power supply connected" and "Mode 21
> with mains power supply connected"

That summary fits the disassembly: F21 trips on a too-high adapter voltage,
which is only ever non-zero when the adapter is connected.

There is no public documentation of a "test mode" / diagnostic-mode bypass
for the F21 self-test in the firmware. The boot path runs unconditionally
from RESET → `0x151a: rcall 0x16b8`. A factory-reset hold-on-power
sequence does exist (annotation `0x1726: T look for key push 1100 (factory
reset up+down)` and `0x174e: loop display debug values until we get a
keypress 1010`), but that's reached **after** the F21 / F20 self-tests
finish, not before — so it cannot be used to bypass either failure.

---

## 6. ST7066U init-timing relevant to the NHD-0216K1Z-NSW-FBW-L

I read the official Newhaven datasheet (revision 6, 2019-03-01) at
https://newhavendisplay.com/content/specs/NHD-0216K1Z-NSW-FBW-L.pdf
(downloaded copy preserved at the WebFetch tool result PDF).

Key facts relevant to "blocks on top row" symptoms:

### 6.1 Module facts

- **Driver IC: ST7066U, 8/4-bit MPU interface.** HD44780 instruction-compatible.
- **Supply voltage: VDD = 5.0 V typ (4.8 V min, 5.2 V max).**
- **VLCD (contrast) = 4.4 V typ (4.3 min, 4.7 max) — note: this is +5V minus
  contrast pot wiper voltage, so V0 ≈ 0.5–0.7 V from GND.**
- 1/16 duty, 1/5 bias.
- Backlight: White LED, +5V via on-board resistor on LED+ pin (no series
  resistor needed externally — but the schematic adds R55 as additional
  current limit; user changed R55 from 47Ω to 100Ω, which is fine).

### 6.2 Bus timing (write) — far from anything the AVR could violate

| Parameter | Symbol | Min |
|---|---|---|
| Enable cycle | T_C | 1200 ns |
| Enable pulse width (E high) | T_PW | 140 ns |
| Address setup (RS, RW before E↑) | T_AS | 0 ns |
| Address hold (RS, RW after E↓) | T_AH | 10 ns |
| Data setup (DB before E↓) | T_DSW | 40 ns |
| Data hold (DB after E↓) | T_H | 10 ns |
| Enable rise/fall | T_R, T_F | 25 ns max |

At 8 MHz, one AVR cycle = 125 ns. The firmware E-pulse is `IO_BIT[PORTC,2]=true; nop; IO_BIT[PORTC,2]=false` → ~250-375 ns high. **All write-bus timings have wide margin.**

### 6.3 Power-on initialization (Newhaven's own example, datasheet page 11)

This is the **4-bit init sequence Newhaven recommends**:

```c
void init() {
    P1 = 0;
    P3 = 0;
    Delay(100);                  // Wait >40 msec after power is applied
    P1 = 0x30;                   // put 0x30 on the output port
    Delay(30);                   // must wait 5ms, busy flag not available
    Nybble();                    // command 0x30 = Wake up
    Delay(10);                   // must wait 160us, busy flag not available
    Nybble();                    // command 0x30 = Wake up #2
    Delay(10);
    Nybble();                    // command 0x30 = Wake up #3
    Delay(10);                   // can check busy flag now instead of delay
    P1 = 0x20;
    Nybble();                    // Function set: 4-bit interface
    command(0x28);               // Function set: 4-bit/2-line
    command(0x10);               // Set cursor
    command(0x0F);               // Display ON; Blinking cursor
    command(0x06);               // Entry Mode set
}
```

**Critical line: `Delay(100); // Wait >40 msec after power is applied`.**
This is what the firmware does NOT do.

### 6.4 What the f005 firmware actually does (LCD init at 0x11c8)

```
RESET (0x14a6) → SRAM clear (~30 µs) → register init (~100 µs)
              → 0x150e jmp to unifyboxes patch (~5 µs) → 0x1512 sei
              → 0x1514 rcall 0x11c8 (initialize_lcd)

initialize_lcd (0x11c8):
   r27 = 4
   loop 4 times:
       PORTC = 0x30        ; "function set 8-bit"
       PORTC[2] = 1 ; nop ; PORTC[2] = 0     ; ~250 ns E pulse
       sleep(0x22)         ; ≈ 359 ms (see §6.5)
       r27--
   PORTC = 0x20            ; "function set 4-bit"
   PORTC[2] = 1 ; nop ; PORTC[2] = 0
   sleep(0x22)             ; ≈ 359 ms
   set_lcd_position(0x28)  ; 4-bit, 2 line, 5x8 — full byte via 2 nibble writes
   set_lcd_position(0x0C)  ; display on, no cursor
   set_lcd_position(0x01)  ; clear
```

**The pre-init delay between Vcc rising and the FIRST `PORTC = 0x30` write
is approximately 130–200 microseconds**, not 40 ms. The 359 ms gaps come
*after* each E-strobe, so the SECOND attempt onward has plenty of margin —
but if the first nibble strobe lands while the ST7066U's internal POR is
still asserted, the LCD enters undefined state. Subsequent "function set"
nibbles can't always rescue it.

### 6.5 sleep parameter math

`delay_0x183e(r26)`:

```
push r27, r28
loop r26 times:
    r28 = 110
    loop r28 times:
        r27 = 0xFF
        loop r27 times:    ; 3 cycles per inner iteration
            r27--
            brne
        r28--
        brne
    r26--
    brne
```

Inner: 3 × 256 = 768 cycles. Middle: 768 × 110 ≈ 84,480 cycles. Outer:
84,480 × r26 cycles.

At 8 MHz, **84,480 cycles = 10.56 ms per outer-loop iteration**. So
`sleep(0x22)` = 34 × 10.56 ms ≈ **359 ms**.

### 6.6 ST7066U internal POR window — the marginal-Vcc-rise issue

The ST7066U datasheet (Sitronix) states that the internal power-on reset
circuit is reliable only for **Vcc rise time between 0.1 ms and 10 ms**. If
the rise is slower than 10 ms — common when feeding the LCD off a 5V rail
filtered through a 7805 + bulk caps + ferrite — the internal reset *can*
fail to assert correctly, and the LCD comes up with random instruction
register state. The firmware's "function set 0x30 × 4" pattern is the
HD44780 standard recovery for this case **if it's started after Vcc has
fully settled**.

This is exactly the failure mode that produces "solid blocks on the top
row" — DDRAM is in 8-bit mode with auto-increment on the wrong line and
without a clear, so the cursor address rolls into CGRAM and prints the
all-pixels-on character.

---

## 7. Most likely root cause for the intermittent symptom

The board exhibits two reproducible behaviours at the same hardware state:

1. **Most boots: solid blocks on top row, no text** — LCD never accepted
   the function-set sequence; remained in undefined post-POR state.
2. **Occasional boots: clean text "Failure 21 / Shut Off Power"** — LCD
   accepted the init **and** F21 self-test fired.

Two AVRs and two front panels reproduce identically; power rails are stable
to a DMM; symptom changes with ribbon orientation.

### 7.1 Best hypothesis: ST7066U internal POR is borderline, AND the F21 trip is real

Two independent things are happening, not one:

**A. The "blocks vs. text" outcome is governed by the LCD's internal POR.**
The f005 firmware lacks the >40 ms post-Vcc-rise delay that Newhaven's own
example code calls out. The ST7066U's POR is reliable only for Vcc rise
times between 0.1 ms and 10 ms; the v1.4 5V rail is fed through a 7805
behind LM2941T, D1, 1000µF + 0.1µF + the 12V rail's 470µF, and the ferrite
on AVCC. Cold inrush from the SLA battery into all those caps will
overshoot 10 ms easily. When the rise is slow, the LCD's internal reset
mis-asserts, the firmware's blind 4× function-set fails to recover it, and
you see solid blocks. Sometimes the rise is fast enough (depends on
battery state, capacitor temperature, contact bounce in S5) and the LCD
comes up clean.

**B. When the LCD does come up clean, F21 trips because PA2 reads
non-zero.** On battery only, U+ should be 0 V and PA2 → 0 V → ADC2 = 0,
well below the 146 (=0x92) threshold. If the box is reporting Failure 21,
**something is driving PA2 above 2.85 V at boot**. Three plausible causes:

  - U+ is not actually 0 V. Check J8 with a DMM at battery-only boot — is
    there >5 V at the centre pin? D1 leakage, board contamination, or a
    floating wall-adapter cable can do this.
  - The AVCC reference is brown-out-low (e.g., 3 V instead of 5 V) at the
    moment the firmware reads ADC2/ADC3, scaling the 0V at PA2 into a
    relative reading > 146/256. This is a clock-startup or LDO-transient
    issue on AVCC. Inspect the AVCC pin (30) of the ATmega16 with a scope
    during the first 50 ms of boot.
  - The ADMUX auto-cycling in the ADC ISR isn't running cleanly because
    interrupt-priority / clock startup is glitching, leaving Y+2 still at
    its seed value `0x56` (= 86) **but** Y+3 also stuck at seed `0x85`
    (= 133, < 142). That actually fails the *battery-low* check first
    (jumps to 0x590, "battery low" message), not F21. So if you see
    Failure 21 specifically (not a battery-low halt), the ISR auto-cycle
    *is* running and ADC2 actually read high.

The ribbon-orientation effect is consistent with hypothesis A modulating
how cleanly the LCD's VDD rail rises (the ribbon carries +5V on multiple
pins — orientation flip changes which J11 conductors carry +5V vs which
carry signal, changing the inrush profile into the LCD's local C42 0.1µF
bypass).

### 7.2 The single test that confirms or rules it out

**Scope-probe both AVCC (pin 30) and the LCD's VDD pin (LCD pin 2, top of
C42) simultaneously while toggling power.** Trigger on the rising edge of
either. You are looking for two things:

1. **Vcc rise time on both rails.** If either rail takes longer than ~10 ms
   to cross from 0.5 V to 4.5 V, the ST7066U POR is being defeated — that
   confirms hypothesis A. Mitigation: add an explicit `delay 0x4` (≈42 ms)
   call as the first instruction in `initialize_lcd` (a 2-byte patch at
   `0x11c8`: insert `ldi r26, 0x04 ; rcall 0x183e` before the loop). Or,
   externally, hardware-reset the LCD (briefly pull VDD low after AVR boot)
   before the firmware tries to talk to it.

2. **PA2 voltage at the same trigger.** If PA2 ≥ 2.85 V at any time during
   the first 50 ms of boot **and you are on battery only**, that explains
   F21. Trace why — measure U+ at J8, measure D1 leakage, measure resistance
   from PA2 to +5V (should be infinite minus the divider chain).

If both AVCC and VDD_LCD rise cleanly within <5 ms AND PA2 stays below
1 V on battery-only boot, then hypothesis A and B are both wrong and the
problem lies elsewhere (most likely: AVR clock-startup oscillator damage,
brown-out detection mis-set, or contamination on the AVR socket pins). The
fact that two AVRs and two panels reproduce identically rules out a single
defective IC, leaving the board's passive components (caps, ribbon, regulator)
or a routing/inrush issue as the prime suspects.

---

## Source references used

- Annotated upstream firmware (binary identical to our `backup_flash.bin` for
  all addresses outside the f005 patch territory ≥ 0x3000):
  https://github.com/teledildonics/buttshock-et312-firmware
  Cloned to `/tmp/buttshock-fw`.
  Tag file: `/tmp/buttshock-fw/annotation/312-16-decrypted-combined.tags`
  Failure-codes table: `/tmp/buttshock-fw/annotation/312-16-failcodes.txt`
- Frankenbutt patch source (already in `/tmp/frankenbutt`):
  https://github.com/CrashOverride85/buttshock-et312-frankenbutt
- Disassembly of our flash (raw `avr-objdump -m avr5 -b binary -D`):
  `/tmp/backup_flash.dis` (7,945 lines)
- v1.4 schematic: `/Users/jas/Documents/git/o4wp/mk312-bt/1-order-boards/schematics/pages/v1.4 Schematic Page 1.png` … `Page 5.png`
- Newhaven NHD-0216K1Z-NSW-FBW-L datasheet rev 6 (2019-03-01):
  https://newhavendisplay.com/content/specs/NHD-0216K1Z-NSW-FBW-L.pdf
- ST7066U controller note (linked from above):
  https://newhavendisplay.com/content/app_notes/ST7066U.pdf
- Third-party F20/F21 debug write-up (CrazyEstim / hvprvbo, 2021-03-29):
  https://hvprvbo.blogspot.com/2021/03/mk312-btfailure20-failure21-debug-for.html
  PDF: https://drive.google.com/file/d/1gr-n5ldNQqSA_JH1kqPSWMPF73wiGk7i/view
- ATmega16 datasheet (Microchip): I/O register addresses (ADMUX = 0x07,
  ADCSRA = 0x06, PORTC = 0x15, DDRC = 0x14, PORTB = 0x18, DDRB = 0x17,
  PORTD = 0x12, DDRD = 0x11) — used to decode every `out`/`in` instruction
  in §1.

## Sources I could NOT retrieve

- Wayback Machine snapshots of metafetish.club threads /357, /419, /629,
  /1327. The fetch tool's pre-check hook timed out on every URL form I
  tried; only Google search index titles came back. The hvprvbo blog above
  is the closest substitute. **No verbatim quote from the metafetish forum
  about Failure 21 was obtainable in this session.**
- The original ST7066U Sitronix datasheet PDF — searches returned mirrors
  but the WebFetch tool could not parse the PDFs; the Newhaven app-note
  copy was the substitute used.
