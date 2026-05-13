# Step 3 — Build and flash

Boards arrived, parts arrived. Time to solder, print the case, flash the AVR.

The full walkthrough — assembly checklist, MOSFET matching, firmware flashing for macOS/Linux/Windows, fuse settings, HC-05 configuration — is in [`build-guide.md`](../build-guide.md) at the repo root.

## What's in this directory

| | |
|---|---|
| [`firmware/`](firmware/) | Pre-built `.bin` files for the ATmega16A + a quick-reference avrdude command |
| [`case/`](case/) | 3D-printable case STL + Fusion 360 source (v1.26) |
| [`troubleshooting/`](troubleshooting/) | Failure-code analyses, board test methodology, archived metafetish forum threads |

## Hardware you'll need (beyond the BOM)

- **AVR programmer** for the 6-pin ISP header (JP1) — USBasp clone ([B0885RKVMC](https://amazon.com/dp/B0885RKVMC) includes the 10→6-pin adapter) or anything avrdude supports
- **Case hardware** — 4× M2.5×20 screws, up to 3× M2.5×5 screws, double-sided foam tape for battery dampening

## When something goes wrong

- **Error 20 on first boot** → almost always mismatched MOSFETs. See [`troubleshooting/debug-notes/failure-20-analysis.md`](troubleshooting/debug-notes/failure-20-analysis.md) for the R32/R43 diagnostic and the pre-build matching procedure.
- **LCD shows solid blocks, no text** → see [`troubleshooting/debug-notes/board-test-methodology.pdf`](troubleshooting/debug-notes/board-test-methodology.pdf) for the bench procedure.
- **Anything else** → [`troubleshooting/`](troubleshooting/) has every other failure code and the metafetish forum archive.

→ Next: [Step 4 — Wireless control](../4-wireless/)
