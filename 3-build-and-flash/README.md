# Step 3 — Build and flash

Boards arrived, parts arrived — now you put it together.

## Where the actual walkthrough lives

**[`../docs/build-guide.md`](../docs/build-guide.md)** — assembly checklist, the [Error 20 prevention/diagnosis](../docs/build-guide.md#error-20-match-the-mosfets-before-you-solder) section, full [firmware flashing walkthrough](../docs/build-guide.md#firmware-flashing-the-avr) for macOS/Linux/Windows (programmer choice, avrdude install, fuse settings, what every flag means), and the [HC-05 configuration](../docs/build-guide.md#bluetooth-hc-05-configuration) section.

## What's in this directory

| | |
|--|--|
| [`firmware/`](firmware/) | Pre-built `.bin` files ready to flash. `t002_bootloader.bin` is the default. See [`firmware/README.md`](firmware/README.md) for the file index and a quick-reference avrdude command. |
| [`case/`](case/) | 3D-printable case (`.stl`) plus Fusion 360 source (`.f3d`). v1.26 |

## Hardware you'll also need

A programmer for the 6-pin ISP header (JP1):

- A **USBasp clone** — BOM lists [`amazon.com/dp/B0885RKVMC`](https://amazon.com/dp/B0885RKVMC), which includes the 10→6-pin adapter the board needs
- Or anything else avrdude supports — Arduino UNO/Nano with the ArduinoISP sketch, DIAMEX USBasp, Atmel-ICE. The build guide covers each.

For the case:

- 4× M2.5×20 screws
- up to 3× M2.5×5 screws
- battery dampening (double-sided foam tape works)

## If something goes wrong

- **Error 20 on first boot** → almost always mismatched MOSFETs. See [Error 20 in the build guide](../docs/build-guide.md#error-20-match-the-mosfets-before-you-solder) — covers the R32/R43 voltage diagnostic and the pre-build MOSFET matching procedure.
- **Backlight on but blank screen** → adjust the LCD contrast pot.
- **Anything else** → [`../docs/troubleshooting/`](../docs/troubleshooting/) for the archived metafetish forum threads (Error 20, parts substitution, transformer questions, oscilloscope traces).

→ Next: [Step 4 — Wireless control](../4-wireless/)
