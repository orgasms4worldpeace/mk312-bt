# Step 2 — Order parts

Two BOM files, same parts, different jobs:

| File | Use it for |
|------|-----------|
| [`BOM_Mouser.csv`](BOM_Mouser.csv) | **Direct import into Mouser's BOM Tool** — strict 4-column format (`Mouser Part Number`, `Quantity`, `Manufacturer Part Number`, `Customer Part Number`). Headers in row 1, no title row, no extra columns — Mouser's importer needs it exactly this way or it silently drops columns. |
| [`BOM_full.csv`](BOM_full.csv) | Human-readable master with designators, descriptions, and both **Mouser** and **Amazon** search links per part. First row is a `Last modified:` date stamp. |

## How to use

1. Sign in to [mouser.com](https://www.mouser.com/) and open the **BOM Tool**.
2. Upload `BOM_Mouser.csv`.
3. Review and add to cart. If Mouser is out of stock on a part, check `BOM_full.csv` for the part number and search alternatives.
4. For anything Mouser doesn't carry (or that's cheaper elsewhere), use the Amazon links in `BOM_full.csv` — handy for screws, standoffs, headers, and the LCD.

## Read this before ordering

[`../1-order-boards/v1.4-release-notes.txt`](../1-order-boards/v1.4-release-notes.txt) lists v1.4 part changes and recommendations:

- C6, C7 should be **low-ESR** electrolytics
- For 42TU200 transformers and higher output, use 0.27 Ω at R30 and 680–820 µF at C6/C7
- R55 backlight: 100–220 Ω for New Haven LCDs
- J2-J7 can be substituted with [STX-3100-5N](https://www.mouser.com/ProductDetail/Kycon/STX-3100-5N) (no plastic back cover)

## Critical parts — these BOMs deliberately over-order

A few parts ship with **higher quantities than one board strictly needs**. This is intentional. Don't reduce them.

| Part | Designators | Per-board need | BOM qty | Why over-ordered |
|------|-------------|----------------|---------|------------------|
| **IRL520N** | Q1, Q2, Q4, Q5 | 4 | 12 | The single biggest cause of Failure 20 is Vt mismatch within the IRL520 quartet. Typical batch spread from a Mouser reel is 200-400 mV; you need to sort and pick 4 within ≤20-30 mV. 3× over-order is the minimum to reliably find a tight quartet. |
| **IRF9Z24NPBF** | Q3, Q6 | 2 | 6 | Q3/Q4 sit in the F20 calibration servo loop in linear-region operation — Vt mismatch eats calibration headroom. Match the pair within ≤50 mV. Also reject any with Vt > 3.3 V. |
| **R35, R46** (200 kΩ) | R35, R46 | 2 | 4 | Op-amp bias network for the output stage. Wrong value (or a damaged trace) is the second-highest-yield F20 root cause after MOSFET mismatch. Spares cost pennies. |
| **R30** (0.27 Ω 1 W) | R30 | 1 | 3 | Current-sense resistor — its value is what the firmware calibrates against. Easy to damage during desolder rework on a failing board, and value-critical to F20 scaling. |
| **XTAL1** (8 MHz) | XTAL1 | 1 | 2 | Silent killer for ATmega ISP programming — a cracked or cold-soldered crystal makes the chip un-flashable and looks identical to a "dead chip" symptom. Cheap insurance. |

### Why the matching tolerances differ between IRL520N and IRF9Z24N

Both are TO-220 MOSFETs, but they play **completely different roles** in the F20 self-test, so the matching rules are different:

**IRF9Z24N (Q3, Q6) — in the calibration servo loop. Tighter is better.**

The firmware's F20 test is a closed-loop DAC ramp: it nudges the DAC down 64 times in ~16 mV steps, looking for current through R30 to settle below ~78 mV. A working unit settles around step 42, leaving roughly **22 steps of headroom** (~484 mV at the Q3 gate). Every mV that Q3's Vt deviates from the working baseline (Infineon ~2.98 V) eats some of that headroom:

| Q3 Vt offset from baseline | Steps consumed (of 22) | Result |
|---|---|---|
| 0 mV (Vt ≈ 2.98 V) | 0 | full headroom — bumerang's working reference |
| +100 mV (Vt ≈ 3.08 V) | ~5 | comfortable |
| +220 mV (Vt ≈ 3.20 V) | ~10 | half eaten — still passes |
| +300 mV (Vt ≈ 3.28 V) | ~14 | marginal — only 8 steps for any other tolerance |
| +600 mV (Vt ≈ 3.58 V — Vishay PBF) | ~27 | **exceeds headroom → F20 fails** |

So for Q3/Q6 the rule is **(a) absolute Vt matters more than match-tightness** and **(b)** the pair should match within ≤50 mV ideal / ≤100 mV acceptable.

**Pick clusters by absolute Vt, in this priority order:**

| Vt cluster | Verdict | Why |
|---|---|---|
| **2.85–3.05 V** | **Use first** | Within ±50 mV of bumerang's known-working baseline. Full calibration headroom. |
| 3.05–3.20 V | Acceptable | ~3–10 calibration steps eaten. Still passes with comfortable margin. |
| 3.20–3.30 V | **Marginal** | ~10–14 steps eaten. Only ~8 steps left for any other tolerance (R30 drift, op-amp offset, IRL520 mismatch). Use only if no lower-Vt parts available, and pair both Q3 and Q6 from the same range. |
| **> 3.30 V** | **Reject** | Borderline failure. Vt of 3.58 V (Vishay PBF) is the documented forum-confirmed F20 failure point. |

The reason **lower Vt within the in-spec range is better**: each mV of Vt above the working baseline is one mV of calibration headroom you've already spent before any other component tolerance gets to push you toward F20. There's no upside to picking a 3.25 V part when you have a 3.00 V part in the same order.

### No shortcut on supplier or batch — here's why

**Three things have to be right** in the part number for the chip to work:

| Element | Required value | Wrong values |
|---|---|---|
| Suffix "N" | **Yes — `IRF9Z24N…`** | Without "N": older die, higher Vt |
| RoHS marking | **`…PBF`** (Pb-free) | Non-PBF versions are EOL |
| Manufacturer | **Infineon** (Mouser 942-IRF9Z24NPBF) | Vishay `IRF9Z24PBF` (no N) has Vt ~3.58 V — documented F20 failure (forum: bumerang #10). Chinese counterfeits have smaller dies. |

Only the Infineon `IRF9Z24NPBF` from a reputable distributor (Mouser, Digi-Key, Element14) is known to work.

**Within Infineon supply, you can't cherry-pick by batch or date code:**

1. Infineon's datasheet allows Vgs(th) of 2.0–4.0 V — a 2 V spec window. Lot-to-lot variation exists within that.
2. Infineon doesn't publish per-lot Vt distribution data. Their public Product Qualification Report shows aggregate process distributions, not "lot 2024-Q3 averaged 2.95 V."
3. Mouser/Digi-Key don't expose date codes pre-purchase, and won't filter orders by date code.
4. No forum or community dataset correlates IRF9Z24N date codes with measured Vt at statistically useful sample sizes.

So there's no upstream selection knob — every IRF9Z24NPBF order is a random draw from the in-spec distribution. The **only working strategy** is order 3× what you need (BOM is set up for this), sort post-delivery, keep the low-Vt cluster.

**IRL520N (Q1, Q2, Q4, Q5) — switches outside the servo loop. Looser tolerance, different concern.**

These four FETs alternate switching to drive the transformer primary in opposite directions, generating the bipolar (Lilly) wave on the output. They aren't part of F20 calibration at all — F20 doesn't directly care about their Vt. What their Vt mismatch *does* affect is **pulse symmetry**: if Q1 and Q2 have different turn-on thresholds, the positive and negative halves of the bipolar pulse won't match in shape, which causes electromigration at metal electrodes over time and can feel asymmetric to the user.

Practical target is ≤20 mV ideal / ≤50 mV acceptable per pair. **30 mV is a fine middle ground** — tight enough that pulse asymmetry stays well below human-perceptible thresholds and well below electromigration risk, loose enough that you can actually hit it with a 12-piece sample.

### Pick the right tester for the job

| Tester | Resolution | Use for |
|---|---|---|
| **LCR-P1** (or LCR-T7-style 2-decimal Mega328 variant) | 2 decimals (mV) | **Vt matching** — the only kind of tester that has the resolution to sort within ≤30 mV |
| Plain Mega328 / DSC-TC4 (1 decimal) | 1 decimal (~50 mV) | Absolute Vt sanity, pinout check, "is this part dead?" — **not matching** |

The LCR-P1 will show readings like `Vt = 1.94 V` instead of `Vt = 1.9 V`. That second decimal is what lets you distinguish a 1.91 from a 1.94 and build a tight quartet. The plain Mega328 will round both to "1.9" and you'll get a useless flat distribution.

The LCR-P1 has its own quirks though — readings jitter ~30–100 mV run-to-run because of gate-charge memory in the FET, probe contact pressure variation, and the tester's own ramp-and-detect algorithm. **You have to control for those or your matching pool looks artificially noisy.**

### Procedure — get stable LCR-P1 readings

Per FET, in order:

1. **Short S↔G with tweezers** (touch the leftmost lead to the rightmost lead on a TO-220 for 1–2 seconds). This drains residual gate charge from previous tests. Skipping this step is the #1 cause of run-to-run jitter.
2. **Hold the FET only by the metal tab.** Body heat on the leads shifts Vt by ~6 mV/°C — fingers running 10°C above ambient skew readings 60 mV. Tweezers or pliers preferred.
3. **Insert into the test socket consistently.** Same orientation every time; firm seating; don't reseat mid-reading.
4. **Press TEST. Wait for the result. Read.**
5. **Wait ~30 seconds before testing the same FET again** (thermal stabilization — the tester's small drain-current pulse warms the die slightly, and ambient handling has warmed the package).
6. **Take 5 readings per FET. Drop the highest and lowest. Average the middle 3.** Use that mean for sorting.
7. Write the Vt on the FET package with a sharpie before moving on, so you don't lose track.

The LCR-P1 itself benefits from a "warm-up" — run 2–3 throwaway tests when you first power it on to let its ADC reference and firmware state stabilize before recording real data.

If the run-to-run spread on a single FET is still > 50 mV after this procedure, your tester or socket has a problem (worn ZIF contacts, dead battery, EMI). Borrow a different unit before trusting the data.

Full sort-and-pair logic (which positions get which Vt cluster) is in [`../docs/troubleshooting/debug-notes/failure-20-analysis.md`](../docs/troubleshooting/debug-notes/failure-20-analysis.md) → "MOSFET matching procedure".

## Substitutions / parts you couldn't find?

The metafetish forum had useful threads on this — see [`../docs/troubleshooting/MK-312BT parts substitution - Estim - Metafetish.pdf`](../docs/troubleshooting/MK-312BT%20parts%20substitution%20-%20Estim%20-%20Metafetish.pdf).

→ Next: [Step 3 — Build and flash](../3-build-and-flash/)
