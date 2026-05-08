#!/usr/bin/env python3
"""Generate one PDF per MK-312BT firmware failure code in docs/troubleshooting/debug-notes/.

Source of truth: the firmware binary at 3-build-and-flash/firmware/backup_flash.bin
(matches the f005 firmware running on the user's chip). Disassembly was performed
with avr-objdump -m avr5 -D --target=binary; every claim in these PDFs cites a
specific flash byte address that can be verified against the dump.

Run: python3 scripts/build-failure-pdfs.py
"""
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak,
)
from reportlab.lib.enums import TA_LEFT
from datetime import datetime

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "troubleshooting" / "debug-notes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=20, spaceAfter=12)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceBefore=14, spaceAfter=6)
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=14, spaceAfter=8)
META = ParagraphStyle("Meta", parent=styles["BodyText"], fontSize=9, textColor=colors.grey, spaceAfter=4)
CODE = ParagraphStyle("Code", parent=styles["Code"], fontSize=8.5, leading=11, leftIndent=8,
                      backColor=colors.HexColor("#f4f4f4"), borderPadding=6,
                      borderColor=colors.HexColor("#dddddd"), borderWidth=0.5)


def metadata_table(rows):
    t = Table(rows, colWidths=[1.6 * inch, 4.4 * inch])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f4f4f4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build(code, title, summary, meta_rows, sections):
    fname = OUT_DIR / f"failure-{code:02d}-analysis.pdf"
    doc = SimpleDocTemplate(
        str(fname), pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=f"MK-312BT Failure {code} — firmware analysis",
        author="MK-312BT firmware disassembly",
    )
    story = []
    story.append(Paragraph(f"MK-312BT Failure {code}", H1))
    story.append(Paragraph(f"<i>{title}</i>", BODY))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%Y-%m-%d')} from "
        f"<font face='Courier'>3-build-and-flash/firmware/backup_flash.bin</font> "
        f"(disassembly via <font face='Courier'>avr-objdump -m avr5</font>). "
        f"Cross-checked against <font face='Courier'>f005.bin</font>.", META))
    story.append(Spacer(1, 6))
    story.append(metadata_table(meta_rows))
    story.append(Spacer(1, 10))
    story.append(Paragraph(summary, BODY))
    for heading, body_blocks in sections:
        story.append(Paragraph(heading, H2))
        for block in body_blocks:
            if isinstance(block, str):
                story.append(Paragraph(block, BODY))
            elif isinstance(block, tuple) and block[0] == "code":
                story.append(Preformatted(block[1], CODE))
                story.append(Spacer(1, 4))
            elif isinstance(block, tuple) and block[0] == "table":
                story.append(metadata_table(block[1]))
                story.append(Spacer(1, 4))
    doc.build(story)
    return fname


# ============================================================================
# F10 — DAC write value out-of-range
# ============================================================================
build(
    code=10,
    title="DAC write value out-of-range (≥ 224 / 0xE0)",
    summary=(
        "Failure 10 fires when the firmware tries to push a value ≥ 224 to the SPI DAC "
        "via the routine at <font face='Courier'>0x0b98</font>. The routine cascades "
        "through three range checks and routes legal values into different sub-paths; "
        "anything ≥ 0xE0 falls off the end of the cascade and trips F10. In normal "
        "operation valid DAC values stay below 0xC0, so F10 indicates the firmware's "
        "intensity/level state has gotten into a bad value — usually a knob/pot reading "
        "way out of band, a bus glitch corrupting an intermediate calculation, or a "
        "ramp/multiplier bug. F10 is rare in the wild compared to F20/F21."
    ),
    meta_rows=[
        ["Code (decimal)", "10"],
        ["Branch site", "0x0bba   (rjmp .+2746 → 0x1676)"],
        ["Test type", "Argument range check inside DAC writer"],
        ["When it runs", "Every DAC update — ramp engine, knob change, mode switch"],
        ["Hardware vs firmware?", "Almost always firmware-state corruption, not hardware"],
    ],
    sections=[
        ("Disassembly evidence", [
            "The DAC writer at <font face='Courier'>0x0b98</font> takes the requested "
            "value in <font face='Courier'>r26</font>:",
            ("code",
             "    0b98:  push r30, r31, r28\n"
             "    0b9e:  lds r30, 0x0207        ; load DAC channel flag\n"
             "    0ba2:  and r30, r30\n"
             "    0ba4:  breq 0x0bac            ; if no override, use r26 directly\n"
             "    ...\n"
             "    0bac:  cpi  r26, 0x80         ; r26 < 128 ?\n"
             "    0bae:  brcs 0x0bbe            ;   yes → normal write path\n"
             "    0bb0:  cpi  r26, 0xC0         ; r26 < 192 ?\n"
             "    0bb2:  brcs 0x0c24            ;   yes → alternate path\n"
             "    0bb4:  cpi  r26, 0xE0         ; r26 < 224 ?\n"
             "    0bb6:  brcs 0x0bbc            ;   yes → another path\n"
             "    0bb8:  ldi  r26, 0x0A         ; ← loads code 10\n"
             "    0bba:  rjmp 0x1676            ; ← FAILURE 10"),
            "The cascade is implementing a banded DAC update: low values write directly, "
            "mid-band values take a slow-update path, upper-mid values take a special "
            "case, and the top band (≥ 0xE0) is treated as illegal."
        ]),
        ("Likely cause", [
            "1. <b>Ramp/multiplier overflow</b> — the firmware's ramp engine (called from "
            "Function_0x1406, the same routine that runs F20) computes intermediate values "
            "that can exceed 0xE0 if a starting DAC seed plus an accumulated delta wraps "
            "the byte. Triggered most often when a pot wire is broken/shorted and the ADC "
            "reads an extreme value.",
            "2. <b>Pot wire fault</b> — if the level pot's wiper is shorted to V+ or open, "
            "the firmware's pot→DAC mapping can produce an out-of-range intensity request.",
            "3. <b>EEPROM corruption</b> — a corrupt stored level/setting at boot can seed "
            "the level engine with a bad value. Power-cycle and full EEPROM reset (or "
            "reflash <font face='Courier'>backup_eeprom.bin</font>) addresses this.",
        ]),
        ("Diagnostic procedure", [
            "1. Power-cycle the box. If F10 reproduces immediately on every boot, suspect "
            "EEPROM corruption — try flashing the known-good <font face='Courier'>"
            "backup_eeprom.bin</font> back via avrdude (<font face='Courier'>-U "
            "eeprom:w:backup_eeprom.bin</font>).",
            "2. If F10 only fires when adjusting a knob, measure each pot's wiper voltage "
            "with a multimeter — should sweep cleanly between 0V and ~5V across the full "
            "rotation. A jumpy or stuck reading points at the offending pot.",
            "3. Check the LEVEL pots (R for level A, level B) for wiper continuity to the "
            "ATmega16's PA pins via the front panel ribbon. Reseat the front panel "
            "ribbon — vibration can intermittently open one of the lines.",
        ]),
        ("Fix", [
            "If EEPROM corruption: reflash <font face='Courier'>backup_eeprom.bin</font> "
            "and full reseat. If pot fault: replace the offending pot or repair the "
            "wiring. F10 from a normal build with no EEPROM history is uncommon — the "
            "first port of call is always the front-panel ribbon."
        ]),
    ],
)


# ============================================================================
# F15 — divide by zero
# ============================================================================
build(
    code=15,
    title="Arithmetic divide-by-zero — firmware sanity check",
    summary=(
        "Failure 15 fires from two sites inside the divide routine at <font face='Courier'>"
        "0x138c</font>. Both sites guard against a zero divisor: the first at 0x1394 catches "
        "a zero high byte before the long-division loop runs, the second at 0x13c2 catches a "
        "zero {r26:r27} pair just before the actual divide. F15 indicates a firmware-internal "
        "arithmetic precondition violation, not a hardware fault. In a working build this "
        "code should never appear; if it does it points at a bug in firmware (the source f005 "
        "tree or its patches) or at corrupted state — not at any solderable component."
    ),
    meta_rows=[
        ["Code (decimal)", "15"],
        ["Branch sites", "0x1396 (rjmp → 0x1676), 0x13c4 (rjmp → 0x1676)"],
        ["Test type", "Divide-by-zero precondition checks"],
        ["When it runs", "Any time the firmware performs a 16-bit division"],
        ["Hardware vs firmware?", "Firmware bug — no hardware diagnosis applies"],
    ],
    sections=[
        ("Disassembly evidence", [
            "The divide routine starts at <font face='Courier'>0x138c</font>:",
            ("code",
             "    138c:  push r26, r27\n"
             "    1390:  and  r31, r31         ; r31 = high byte of divisor\n"
             "    1392:  brne 0x1398           ; if non-zero, OK\n"
             "    1394:  ldi  r26, 0x0F        ; ← loads code 15\n"
             "    1396:  rjmp 0x1676           ; ← FAILURE 15 (early)\n"
             "    1398:  ...                   ; long-division proper\n"
             "    13bc:  cp   r27, r29         ; r29 is zero-register\n"
             "    13be:  cpc  r26, r29\n"
             "    13c0:  brne 0x13c6           ; if {r26:r27} != 0, OK\n"
             "    13c2:  ldi  r26, 0x0F        ; ← loads code 15 (second site)\n"
             "    13c4:  rjmp 0x1676           ; ← FAILURE 15 (late)"),
            "Both checks fire on the same condition (divisor = 0) at different points in "
            "the routine — defensive programming inside the divide."
        ]),
        ("Likely cause", [
            "F15 is firmware-internal. If you ever see it in real life:",
            "1. <b>Patched firmware bug</b> — if you applied a custom patch to the f005 "
            "firmware (e.g. a custom boot message or a feature mod), the patch may have "
            "introduced a divide that doesn't validate its operands. Check the patch site.",
            "2. <b>Corrupted EEPROM</b> driving zero into a config field that's later used "
            "as a divisor. Reseat / reflash EEPROM.",
            "3. <b>Cosmic-ray-class glitch</b> (extremely rare) — bit flip in RAM. "
            "Power-cycle clears it.",
        ]),
        ("Diagnostic procedure", [
            "1. Power-cycle. Does it reproduce? If only intermittent, EEPROM or RAM glitch — "
            "monitor.",
            "2. If reproducing every boot, the firmware itself is suspect. Reflash a "
            "known-good <font face='Courier'>f005.bin</font>.",
            "3. If you've applied custom patches, revert one at a time until F15 stops.",
        ]),
        ("Fix", [
            "Reflash known-good firmware. If F15 persists with stock <font face='Courier'>"
            "f005.bin</font>, that would be a genuine bug worth filing upstream — but in "
            "practice this never happens with the canonical build."
        ]),
    ],
)


# ============================================================================
# F16 — output-level mapping iteration overflow
# ============================================================================
build(
    code=16,
    title="Output-level mapping iteration overflow (RAM[0x01F4] ≥ 4)",
    summary=(
        "Failure 16 fires from inside <font face='Courier'>Function_0x15b8</font>, the "
        "routine that maps pot/ramp positions to output DAC seeds. The function uses an "
        "iteration counter at RAM <font face='Courier'>0x01F4</font>; if that counter "
        "reaches 4 without the calculation converging, F16 trips. In practice this means "
        "the pot inputs are reading values that produce no valid intensity mapping — "
        "either out-of-range pot ADC values, or a corrupt ramp profile that diverges "
        "instead of settling."
    ),
    meta_rows=[
        ["Code (decimal)", "16"],
        ["Branch site", "0x15fa   (rjmp .+122 → 0x1676)"],
        ["Test type", "Iteration-counter sanity check"],
        ["When it runs", "Continuously during normal output — any DAC setpoint update"],
        ["Hardware vs firmware?", "Most often a pot/ribbon hardware fault"],
    ],
    sections=[
        ("Disassembly evidence", [
            "The function entry at <font face='Courier'>0x15b8</font> reads the loop "
            "counter and bails out if it's ever ≥ 4:",
            ("code",
             "    15b8:  push r26, r27\n"
             "    15bc:  ldd  r30, Y+4         ; load DAC base for channel\n"
             "    15c0:  ldd  r2,  Y+11        ; load step delta\n"
             "    15c4:  lds  r26, 0x01F4      ; load iteration counter\n"
             "    15c8:  cpi  r26, 0x04        ; counter < 4 ?\n"
             "    15ca:  brcc 0x15f8           ;   no → fail\n"
             "    ...                          ; iteration body, increments counter\n"
             "    15f8:  ldi  r26, 0x10        ; ← loads code 16\n"
             "    15fa:  rjmp 0x1676           ; ← FAILURE 16"),
            "The body of the function (0x15cc–0x15f6) computes a target DAC value from "
            "the current pot reading + ramp position. Each iteration that doesn't converge "
            "increments RAM[0x01F4]; if it reaches 4 without convergence, F16."
        ]),
        ("Likely cause", [
            "1. <b>Pot wiper noise / dropout</b> — a noisy or intermittently open pot "
            "wiper makes the pot ADC reading jump on every sample, so the iteration never "
            "settles. Most common physical cause.",
            "2. <b>Ribbon cable fault</b> — front-panel ribbon connector has 24 pins and "
            "carries every pot signal. A loose pin produces F16-like behavior.",
            "3. <b>ADC reference glitch</b> — if AVCC or AREF is noisy, ADC readings drift "
            "between consecutive samples and the iteration can't converge.",
        ]),
        ("Diagnostic procedure", [
            "1. <b>Reseat the front-panel ribbon</b> — first thing to try. F16 plus any "
            "pot-related symptoms point here.",
            "2. With the box powered, measure each level pot's wiper voltage on the "
            "ATmega side of the ribbon while slowly rotating the knob. Reading should "
            "sweep smoothly from ~0V to ~5V. Any sudden drops or flat spots = pot bad.",
            "3. With a scope (if available), look at AVCC (pin 30) and AREF (pin 32) — "
            "should be clean 5.0V. Ripple > ~50 mV on either rail can cause F16.",
        ]),
        ("Fix", [
            "Reseat ribbon → replace offending pot if measurements show dropout → in rare "
            "cases, replace bypass caps on AVCC/AREF if rails are noisy. F16 is rarely a "
            "build error; it's usually a worn-knob or loose-ribbon condition that "
            "develops over time."
        ]),
    ],
)


# ============================================================================
# F20 — output stage current-sense check (channels A and B)
# ============================================================================
build(
    code=20,
    title="Output stage can't settle current — both channels (R30 sense)",
    summary=(
        "Failure 20 is the post-boot output-stage self-test, and the most common build "
        "failure on first power-up. A single routine at <font face='Courier'>"
        "Function_0x1406</font> drives PB2+PB3 (channel A) and then PB0+PB1 (channel B) "
        "while monitoring ADC0 (R30 current sense). On each pass it ramps the DAC down "
        "from a low-power seed and looks for the R30 current to settle within bounds. "
        "If either channel can't deliver current, or the current runs away, F20 fires. "
        "Forum lore that pairs F20 (channel A) with F21 (channel B) is wrong — F20 alone "
        "tests both channels; F21 is the wall-adapter voltage check."
    ),
    meta_rows=[
        ["Code (decimal)", "20"],
        ["Branch site", "0x1494   (rjmp .+480 → 0x1676)"],
        ["Test type", "Output stage current-sense, both channels"],
        ["When it runs", "Once at boot, after F21 voltage check passes"],
        ["Hardware vs firmware?", "Almost always hardware — MOSFETs, transformer, R35/R46"],
    ],
    sections=[
        ("Disassembly evidence", [
            "The test routine at <font face='Courier'>Function_0x1406</font>:",
            ("code",
             "    1406:  ; init counters\n"
             "    140c:  ldi  r16, 0           ; channel-select flag: 0=A, 1=B\n"
             "    1410:  ldi  r26, 100         ; DAC seed = 100 (≈OUTA 4.38V)\n"
             "    143a:  cp   r16, 0\n"
             "    143c:  brne 0x1444           ; channel B branch\n"
             "    143e:  ldi  r26, 0x0c        ; PORTB = 0b00001100 (PB2+PB3 = q5+q6)\n"
             "    1440:  out  PORTB, r26       ; ← drives channel A FETs\n"
             "    1444:  ldi  r26, 0x03        ; PORTB = 0b00000011 (PB0+PB1 = q7+q8)\n"
             "    1446:  out  PORTB, r26       ; ← drives channel B FETs\n"
             "    1448-1452:                   ; pulse-width delay\n"
             "    1456:  out  PORTB, 0         ; gates OFF\n"
             "    1458-145c:                   ; wait for ADC, read ADCL\n"
             "    1460:  cpi  r26, 0x10        ; ADCL < 16 ? (≈61mV)\n"
             "    1462:  brcc 0x1476           ;   yes → settled, advance\n"
             "    1464:  inc  r27              ; pulse counter\n"
             "    1466:  cpi  r27, 0x40        ; 64 attempts?\n"
             "    1468:  brcc 0x1492           ; ← 64 attempts exhausted → F20\n"
             "    146a-1474:                   ; decrement DAC, loop back\n"
             "    1476:  cmp  r27, 0\n"
             "    1478:  breq 0x1492           ; ← first pulse already too LOW = open → F20\n"
             "    ...                          ; advance to channel B (r16=1) and repeat\n"
             "    1492:  ldi  r26, 0x14        ; ← loads code 20\n"
             "    1494:  rjmp 0x1676           ; ← FAILURE 20"),
            "There are two distinct ways to trip F20:",
            "<b>(a)</b> The very first pulse already reads ADCL &lt; 16 — meaning no "
            "current is flowing through R30 even at the high-power DAC seed. This points "
            "at an <b>open circuit</b> in the output stage (transformer wired wrong, FET "
            "missing, broken solder joint).",
            "<b>(b)</b> 64 successive pulses fail to bring ADCL below the threshold — "
            "the firmware can never get the channel quiet. This points at a <b>runaway / "
            "imbalanced</b> output (mismatched MOSFET Vt, leaky FET, wrong R35/R46 value)."
        ]),
        ("Likely cause", [
            "<b>Most common (in this order):</b>",
            "1. <b>MOSFET Vt mismatch</b> — IRL520 quartet or IRF9Z24 pair with > ~50 mV "
            "spread in gate threshold voltage. The output stage can't keep R32 and R43 "
            "balanced.",
            "2. <b>Transformer reversed</b> — primary wired backward, current direction "
            "wrong.",
            "3. <b>R35/R46 wrong value</b> — should be 200 kΩ. A 20 kΩ or 2 MΩ here "
            "throws off the gate bias.",
            "4. <b>FET orientation</b> — IRL520 / IRF9Z24 placed backwards.",
            "5. <b>DAC fault</b> — LTC1661 not communicating, or one of its outputs stuck. "
            "Last resort.",
        ]),
        ("Diagnostic procedure", [
            "1. <b>Measure DC voltage across R32 and across R43</b> with the box powered "
            "on, no patient cables connected. Both should read between <b>4.0 V and 4.4 V</b> "
            "and be very close to each other (within ~50 mV).",
            "2. If R32 ≠ R43: <b>MOSFET mismatch</b>. Desolder the IRL520 quartet, measure "
            "Vt of each on a component tester, and replace with a matched set "
            "(target spread &lt; 20 mV).",
            "3. If R32 = R43 but both out of range (e.g. both 1V or both 5V): check "
            "transformer orientation, R35 and R46 values, FET orientations.",
            "4. <b>Before soldering on a fresh build</b>: pre-match every IRL520 / IRF9Z24 "
            "with a component tester. A $15 Mega328-based tester from Amazon (B0DDBPWYP8) "
            "will save you hours of debugging.",
        ]),
        ("Fix", [
            "Match MOSFETs by Vt before soldering. If already built and F20 trips, "
            "desolder and swap in a matched set. R32/R43 mismatch is the diagnostic "
            "smoking gun — believe the multimeter, not your soldering pride. The "
            "build-guide section "
            "<font face='Courier'>docs/build-guide.md → Error 20</font> covers prevention. "
            "Background reading: the metafetish forum threads archived in "
            "<font face='Courier'>docs/troubleshooting/MK-312BT Failure 20 - Estim - "
            "Metafetish.pdf</font> and "
            "<font face='Courier'>Another Failure 20 with measurements and some test "
            "mode_ - Estim - Metafetish.pdf</font>."
        ]),
    ],
)


# ============================================================================
# F21 — wall-adapter voltage too high
# ============================================================================
build(
    code=21,
    title="Wall-adapter voltage too high (ADC2 ≥ 146 → U+ ≥ ~17.1 V)",
    summary=(
        "Failure 21 is a boot-time voltage check that runs <i>before</i> F20. The "
        "firmware reads ADC2 (PA2, fed by the R3 100kΩ / R4 20kΩ divider from raw input "
        "U+) and trips F21 if the reading is ≥ 146. Through that divider, ADC2=146 "
        "corresponds to U+ ≈ 17.1 V at J8. F21 means the wall adapter is over-spec, OR "
        "the ADC reference / divider / ribbon is reading garbage. The forum lore that "
        "pairs F21 with F20 as A/B channel tests is wrong — F21 is purely a power check."
    ),
    meta_rows=[
        ["Code (decimal)", "21"],
        ["Branch site", "0x16e4   (rjmp .-112 → 0x1676)"],
        ["Test type", "Boot voltage check (ADC2 = wall adapter sense)"],
        ["When it runs", "Once at boot, before F20"],
        ["Hardware vs firmware?", "Power supply OR ADC reference / wiring"],
    ],
    sections=[
        ("Disassembly evidence", [
            "The check at <font face='Courier'>Function_0x16b8</font>:",
            ("code",
             "    16b8:  ldi  r26, 0x56        ; pre-seed ADC2 storage slot\n"
             "    16ba:  std  Y+2, r26\n"
             "    16bc:  ldi  r26, 0x85        ; pre-seed ADC3 storage slot\n"
             "    16be:  std  Y+3, r26\n"
             "    16c0:  rcall 0x0b1e          ; trigger ADC, wait, three sample average\n"
             "    16c2-16d0:                   ; (ISR auto-cycles ADMUX)\n"
             "    16d2:  ldd  r26, Y+3         ; ADC3 result (battery sense)\n"
             "    16d4:  cpi  r26, 0x8E        ; 142\n"
             "    16d6:  brcc 0x16dc           ;   ≥142 → continue\n"
             "    16d8:  jmp  0x590            ;   <142 → 'Battery Low' display\n"
             "    16dc:  ldd  r27, Y+2         ; ADC2 result (wall adapter sense)\n"
             "    16de:  cpi  r27, 0x92        ; 146\n"
             "    16e0:  brcs 0x16e6           ;   <146 → continue\n"
             "    16e2:  ldi  r26, 0x15        ; ← loads code 21\n"
             "    16e4:  rjmp 0x1676           ; ← FAILURE 21"),
            "Voltage-divider math: ADC threshold 146/255 × 5.00 V = 2.86 V at PA2. "
            "Divider R3=100kΩ / R4=20kΩ gives PA2 = U+ × 20/(100+20) = U+/6. "
            "Threshold U+ = 2.86 × 6 = <b>~17.1 V</b>."
        ]),
        ("BOM tension", [
            "The MK-312BT BOM recommends a <b>15–19 V</b> supply. The firmware tripwire "
            "is at <b>~17.1 V</b>. So an 18 V or 19 V brick — explicitly recommended in "
            "the BOM — is over the firmware threshold the moment it sags less than ~6%. "
            "<b>If you're seeing F21 with an 18 V or 19 V brick, that's why.</b> A "
            "regulated 15 V brick gives you ~2 V of headroom and is the safe choice."
        ]),
        ("Likely cause", [
            "1. <b>Adapter over-spec</b> — most common. Especially if you're using an "
            "18 V or 19 V brick, or an unregulated 'up to 18V' brick that idles high.",
            "2. <b>ADC reference issue</b> — AVCC (pin 30) or AREF (pin 32) noisy or "
            "mis-wired, causing ADC2 to read high.",
            "3. <b>Divider component fault</b> — R3 (100kΩ) open or R4 (20kΩ) shorted "
            "would push PA2 to the supply rail.",
            "4. <b>Ribbon-induced fault</b> — front-panel ribbon induced noise on PA2 "
            "during boot.",
            "5. <b>LCD POR timing</b> — the user's own boards (this repo) reproduced an "
            "intermittent F21 traced to LCD initialization timing rather than actual "
            "over-voltage. See "
            "<font face='Courier'>failure-21-analysis.md</font> §3 for the full "
            "investigation."
        ]),
        ("Diagnostic procedure", [
            "1. <b>Measure U+ at J8 with a multimeter</b> with the box powered on, no "
            "patient cables. If U+ &gt; 17 V → adapter problem; swap to a regulated 15 V.",
            "2. If U+ ≤ 17 V and F21 still fires → <i>not</i> a supply problem. Move to "
            "ADC / divider / ribbon investigation per "
            "<font face='Courier'>failure-21-analysis.md</font> §3-§4.",
            "3. Measure resistance R3 → 100 kΩ ± 1%, R4 → 20 kΩ ± 1%. Check D5 (1N4148 "
            "clamp at PA2) is not shorted.",
            "4. Reseat the front-panel ribbon. If F21 was intermittent, this often "
            "clears it.",
        ]),
        ("Fix", [
            "Most cases: drop to a 15 V regulated supply. If U+ is in spec, see the deep "
            "investigation at "
            "<font face='Courier'>docs/troubleshooting/debug-notes/failure-21-analysis.md"
            "</font> — that file has the user's full LCD-POR-timing fix for the "
            "intermittent case."
        ]),
    ],
)


# ============================================================================
# F72 — internal state-variable overflow
# ============================================================================
build(
    code=72,
    title="State variable RAM[0x01F1] overflow (≥ 56)",
    summary=(
        "Failure 72 fires from the routine at <font face='Courier'>0x1a06</font>, which "
        "increments an accumulator at RAM <font face='Courier'>0x0214</font> and then "
        "checks a related state variable at <font face='Courier'>0x01F1</font>. If "
        "RAM[0x01F1] ever reaches ≥ 56 (0x38), F72 trips. This is a defensive check on "
        "a firmware-internal state machine — likely a step counter for a multi-stage "
        "operation (mode setup, ramp progression, audio sequencer phase). F72 normally "
        "indicates that the state machine got out of sync, often due to an interrupt "
        "race or corrupted RAM."
    ),
    meta_rows=[
        ["Code (decimal)", "72"],
        ["Branch site", "0x1a1e   (rjmp .-938 → 0x1676)"],
        ["Test type", "Internal state-variable bounds check"],
        ["When it runs", "Inside the routine at 0x1a06 — called from mode/ramp engine"],
        ["Hardware vs firmware?", "Firmware — almost never a hardware fault"],
    ],
    sections=[
        ("Disassembly evidence", [
            ("code",
             "    1a06:  push r30, r31\n"
             "    1a0a:  lds  r30, 0x0214      ; load accumulator\n"
             "    1a0e:  add  r30, r26         ; accumulator += r26 (the new step)\n"
             "    1a10:  sts  0x0214, r30      ; store back\n"
             "    1a14:  lds  r30, 0x01F1      ; load state variable\n"
             "    1a18:  cpi  r30, 0x38        ; ≥ 56?\n"
             "    1a1a:  brcs 0x1a20           ;   no → continue\n"
             "    1a1c:  ldi  r26, 0x48        ; ← loads code 72\n"
             "    1a1e:  rjmp 0x1676           ; ← FAILURE 72"),
            "RAM[0x01F1] is a step counter. The function adds whatever's in r26 to "
            "RAM[0x0214] (an accumulator), then aborts if the step counter is too high. "
            "In stock firmware this should never trip because the calling code resets "
            "the counter periodically."
        ]),
        ("Likely cause", [
            "1. <b>Custom firmware patch</b> — a patch that adds modes / ramps / step "
            "logic without resetting RAM[0x01F1] cleanly between cycles will run the "
            "counter up over time. Check any user-added f005 patches.",
            "2. <b>EEPROM corruption seeding bad state</b> at boot — reflash "
            "<font face='Courier'>backup_eeprom.bin</font>.",
            "3. <b>Interrupt race</b> in heavily-loaded modes (e.g. high-frequency "
            "rhythm modes) where an ISR fires inside the state-update path. This would "
            "be a real upstream bug.",
        ]),
        ("Diagnostic procedure", [
            "1. Note <b>which mode</b> was running when F72 fired — switch back to the "
            "stock f005 mode set and try to reproduce. If F72 stops, you have a custom-"
            "patch bug.",
            "2. Power-cycle and reflash EEPROM. If F72 reproduces from a clean EEPROM "
            "with stock firmware, that would be a real upstream bug worth reporting.",
            "3. There's no hardware-side fix — F72 is a firmware-state failure.",
        ]),
        ("Fix", [
            "Reflash stock <font face='Courier'>f005.bin</font> + clean "
            "<font face='Courier'>backup_eeprom.bin</font>. If reproducible from clean "
            "state, file upstream — but in practice this is vanishingly rare on stock "
            "firmware."
        ]),
    ],
)


# ============================================================================
# F80 — EEPROM/config readback out of range
# ============================================================================
build(
    code=80,
    title="EEPROM/config readback value out of range (≥ 40 / 0x28)",
    summary=(
        "Failure 80 fires on a value-range check that follows an EEPROM read. The check "
        "at <font face='Courier'>0x0790</font> compares an indexed value (in r30) to 40 "
        "(0x28); if r30 ≥ 40 the firmware trips F80. The preceding code path includes "
        "<font face='Courier'>call 0x19dc</font>, which is the EEPROM-read primitive "
        "(it polls EECR at I/O 0x1c). So F80 indicates a stored configuration byte (a "
        "mode index, calibration value, or saved-state pointer) that exceeds its valid "
        "range. Most often this means a corrupt EEPROM — first-boot of a freshly-flashed "
        "chip with no EEPROM init, or wear/corruption on a long-running unit."
    ),
    meta_rows=[
        ["Code (decimal)", "80"],
        ["Branch site", "0x0796   (rjmp .+3806 → 0x1676)"],
        ["Test type", "EEPROM-stored config byte range check"],
        ["When it runs", "During mode load / setting recall paths"],
        ["Hardware vs firmware?", "EEPROM contents — software fix (reflash EEPROM)"],
    ],
    sections=[
        ("Disassembly evidence", [
            ("code",
             "    19dc:  ; EEPROM read primitive\n"
             "    19de:  in   r28, 0x1c        ; EECR\n"
             "    19e0:  andi r28, 0x03        ; check EERE/EEWE busy bits\n"
             "    19e2:  brne 0x19de           ; spin until idle\n"
             "    19e4:  out  0x1f, r27        ; EEAR high\n"
             "    19e6:  out  0x1e, r26        ; EEAR low\n"
             "    19e8:  sbi  0x1c, 0          ; EERE = 1 → start read\n"
             "    19ec:  in   r0, 0x1d         ; EEDR → r0\n"
             "    19f0:  ret\n"
             "    ...\n"
             "    0756:  call 0x19dc           ; ← EEPROM read\n"
             "    075a:  mov  r26, r0          ; result into r26\n"
             "    075c:  rcall 0x0b98          ; (use the value)\n"
             "    ...\n"
             "    0790:  cpi  r30, 0x28        ; ≥ 40?\n"
             "    0792:  brcs 0x0798           ;   no → continue\n"
             "    0794:  ldi  r26, 0x50        ; ← loads code 80\n"
             "    0796:  rjmp 0x1676           ; ← FAILURE 80"),
            "Combined with the EEPROM read above the check, F80 is a sanity guard on a "
            "stored byte that should be a small index (0..39). The firmware likely "
            "stores the current/saved mode here, or a slot index into a table."
        ]),
        ("Likely cause", [
            "1. <b>First-boot of fresh chip</b> — virgin AVR EEPROM is all 0xFF (= 255), "
            "so any read of an uninitialized slot returns 255, which is &gt;&gt; 40 → F80.",
            "2. <b>EEPROM corruption</b> over time — power loss during write, lightning, "
            "ESD, etc.",
            "3. <b>Bus error during EEPROM read</b> — extremely rare; only if the AVR's "
            "Vcc is glitching.",
        ]),
        ("Diagnostic procedure", [
            "1. <b>If this is a first boot of a freshly-flashed chip</b>: the box may "
            "need to write an initial EEPROM image. Either flash the bundled "
            "<font face='Courier'>backup_eeprom.bin</font> from this repo "
            "(<font face='Courier'>avrdude -c &lt;programmer&gt; -p m16 -U "
            "eeprom:w:backup_eeprom.bin</font>), or run the firmware's normal first-boot "
            "init (some f005 builds initialize EEPROM if they detect 0xFF; others don't).",
            "2. <b>If this is a long-running unit suddenly throwing F80</b>: dump the "
            "EEPROM (<font face='Courier'>-U eeprom:r:current_eeprom.bin:r</font>) and "
            "compare to the known-good <font face='Courier'>backup_eeprom.bin</font>. "
            "Differences in the first ~64 bytes confirm corruption.",
            "3. Reflash known-good EEPROM and reboot.",
        ]),
        ("Fix", [
            "Reflash <font face='Courier'>backup_eeprom.bin</font>. F80 is virtually "
            "always EEPROM contents, not hardware — so don't go probing the board "
            "before you've tried the EEPROM reset."
        ]),
    ],
)

# ============================================================================
# Index PDF — overview of all failures
# ============================================================================
def build_index():
    fname = OUT_DIR / "failure-codes-index.pdf"
    doc = SimpleDocTemplate(
        str(fname), pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title="MK-312BT firmware failure codes — index",
    )
    story = []
    story.append(Paragraph("MK-312BT firmware failure codes — complete index", H1))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%Y-%m-%d')} from "
        f"<font face='Courier'>3-build-and-flash/firmware/backup_flash.bin</font>. "
        f"This is the exhaustive list — every <font face='Courier'>jmp/rjmp 0x1676</font> "
        f"in the firmware was traced to its preceding <font face='Courier'>"
        f"ldi r26, 0xNN</font>. The error_handler at 0x1676 prints "
        f"<font face='Courier'>\"Failure NN / Shut Off Power\"</font> and halts; "
        f"r26 at jmp time is the displayed code.", META))
    story.append(Spacer(1, 12))

    rows = [
        ["Code", "Branch", "Meaning", "Class", "Most likely cause"],
        ["10", "0x0bba", "DAC write value ≥ 224", "Firmware/state",
         "EEPROM corruption or pot/ribbon glitch"],
        ["15", "0x1396, 0x13c4", "Divide-by-zero", "Firmware bug",
         "Custom patch or RAM glitch (rare)"],
        ["16", "0x15fa", "Output-level mapping won't converge", "Hardware (pots)",
         "Front-panel ribbon, noisy pot, AVCC ripple"],
        ["20", "0x1494", "Output stage current sense fails (A or B)", "Hardware",
         "MOSFET Vt mismatch, transformer rev'd, R35/R46 wrong"],
        ["21", "0x16e4", "Wall adapter ≥ ~17.1 V", "Power",
         "18V/19V supply over-spec, or ADC reference / ribbon"],
        ["72", "0x1a1e", "State counter RAM[0x01F1] ≥ 56", "Firmware/state",
         "Custom patch bug or EEPROM corruption"],
        ["80", "0x0796", "EEPROM config byte ≥ 40", "EEPROM",
         "First boot of fresh chip; reflash EEPROM"],
    ]
    t = Table(rows, colWidths=[0.5 * inch, 1.2 * inch, 2.2 * inch, 1.1 * inch, 1.8 * inch])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9.5),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bbbbbb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Where to start", H2))
    story.append(Paragraph(
        "Each code has its own <font face='Courier'>failure-NN-analysis.pdf</font> in "
        "this directory with disassembly evidence, likely causes, and a diagnostic "
        "procedure. <b>Order of frequency on a fresh build</b>: F20 (output stage), F21 "
        "(supply voltage), F80 (EEPROM init). F10/F15/F16/F72 are rare in the wild and "
        "usually point at firmware patches or worn-out hardware on long-running units.",
        BODY))
    story.append(Paragraph("Caveat: dynamic dispatcher at 0x3ea", H2))
    story.append(Paragraph(
        "There's also one branch at <font face='Courier'>0x3ea</font> that does "
        "<font face='Courier'>jmp 0x1676</font> with a <i>dynamic</i> code — it loads "
        "r26 from <font face='Courier'>Y+34</font> and jumps if that value ≥ 4. So in "
        "principle the firmware can display Failure codes 4, 5, 6, 7, ... if some "
        "other code path stores those values into Y+34. None of the literal "
        "<font face='Courier'>ldi r26</font> sites elsewhere in the firmware load values "
        "in the 4-9 range, so the practical list of codes a stock f005 build will ever "
        "actually display is the seven above.",
        BODY))
    story.append(Paragraph("Method", H2))
    story.append(Paragraph(
        "Disassembly: <font face='Courier'>avr-objdump -m avr5 -D --target=binary "
        "backup_flash.bin</font>. The error_handler entry was identified by tracing the "
        "string <font face='Courier'>\"Failure \"</font> in flash and finding the "
        "routine that consumes r26 as a number to print. Every "
        "<font face='Courier'>(rjmp|jmp) 0x1676</font> reference was followed back to "
        "the immediately-preceding <font face='Courier'>ldi r26, 0xNN</font> "
        "instruction. Cross-checked against <font face='Courier'>f005.bin</font> "
        "(the canonical firmware file) — identical bytes at all 9 sites.",
        BODY))
    doc.build(story)
    return fname

idx = build_index()

# Print summary
import os
written = sorted(OUT_DIR.glob("failure-*-analysis.pdf")) + [idx]
for p in written:
    print(f"  {p.relative_to(REPO)}  ({os.path.getsize(p):,} B)")
print(f"\n{len(written)} files in {OUT_DIR.relative_to(REPO)}/")
