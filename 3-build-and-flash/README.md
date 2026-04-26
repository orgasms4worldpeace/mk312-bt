# Step 3 — Build and flash

Once the boards arrive and the parts are sourced, this is where you put it together.

## Detailed walkthrough

The comprehensive build guide lives at **[`../docs/build-guide.md`](../docs/build-guide.md)** — assembly checklist, common mistakes (LCD orientation, transformer direction, electrolytic polarity, the Pin 32 trap on the HC-05), AVR fuse settings, OSCCAL notes.

## What's in this directory

| | |
|--|--|
| [`firmware/`](firmware/) | Flash images (`.bin`), an EEPROM backup, and a custom boot message variant in [`firmware/f005/`](firmware/f005/). See [`firmware/README.md`](firmware/README.md) for fuse/flashing details |
| [`case/`](case/) | 3D-printable case (`.stl`) plus the Fusion 360 source (`.f3d`). v1.26 |

## Hardware you'll also need

For the case:

- 4× M2.5×20 screws
- up to 3× M2.5×5 screws
- some battery dampening (double-sided foam tape works)

For flashing the AVR:

- An ICSP programmer (USBasp, AVRISP mkII, etc.)
- avrdude or Atmel Studio
- See [`../docs/build-guide.md#mk312-bt-firmware`](../docs/build-guide.md) for the fuse byte settings

## If something goes wrong

- **Error 20 on first boot** → check FET + transformer orientation, verify R35/R46 are 200 kΩ. Full diagnosis: [`../docs/troubleshooting/MK-312BT Failure 20 - Estim - Metafetish.pdf`](../docs/troubleshooting/MK-312BT%20Failure%2020%20-%20Estim%20-%20Metafetish.pdf)
- **Backlight on but blank screen** → adjust the LCD contrast pot
- **General weirdness** → [`../docs/troubleshooting/`](../docs/troubleshooting/)

→ Next: [Step 4 — Wireless control](../4-wireless/)
