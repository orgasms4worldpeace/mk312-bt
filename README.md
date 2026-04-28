# MK-312BT

DIY clone of the ErosTek ET-312B e-stim power box, with bluetooth (HC-05) and optional WiFi (ESP8266) wireless control. This repo is a 2026 reorganization and consolidation of two abandoned upstreams:

- [CrashOverride85/mk312-bt](https://github.com/CrashOverride85/mk312-bt) — the box itself (boards, BOM, firmware, case)
- [Rangarig/MK312WIFI](https://github.com/Rangarig/MK312WIFI) — drop-in WiFi adapter, pulled into [`4-wireless/wifi/`](4-wireless/wifi/) as a git subtree

Control software (mk312-gui, ErosWeb, three-twelve-bee, restim, etc.) is **not bundled** — [`5-software/`](5-software/) is a links-only index pointing at upstream projects. Pick whichever fits your platform.

Original work credit goes to the upstream authors. Everything here is licensed under whatever the upstream repos shipped with.

## How to build one

The top-level layout follows the build path. Work through the numbered directories in order:

| Step | Directory | What you do |
|------|-----------|-------------|
| 1 | [`1-order-boards/`](1-order-boards/) | Send PCB gerbers to a fab (JLCPCB / PCBWay / etc.) |
| 2 | [`2-order-parts/`](2-order-parts/) | Import the BOM into Mouser, source remaining parts |
| 3 | [`3-build-and-flash/`](3-build-and-flash/) | Solder, print the case, flash the AVR |
| 4 | [`4-wireless/`](4-wireless/) | Pick **bluetooth** (HC-05) or **wifi** (ESP8266) — both pin-compatible |
| 5 | [`5-software/`](5-software/) | Pick a control client — links-only index of upstream PyQt / web-based / Python options |

For the comprehensive end-to-end walkthrough, see **[docs/build-guide.md](docs/build-guide.md)**.

## Reference

- [`docs/build-guide.md`](docs/build-guide.md) — full assembly + flashing walkthrough
- [`docs/troubleshooting/`](docs/troubleshooting/) — original debug notes (annotated test-methodology PDF, F21 disassembly analysis) plus archived threads from the now-offline metafetish.club forum
- [`historical/`](historical/) — v1.2 / v1.3 boards, original Eagle source, build photos. Kept for archaeology; **not what you want to build today**

## Getting help

The active community lives in the `#boxes-pulse-based-diy` and `#312-chat` channels on [Joanne's E-Stim Community Discord](https://discord.gg/rY8C27S).

## Safety

This is a high-voltage e-stim device. Don't injure yourself. The upstream authors and this maintainer assume no responsibility for what you do with it.
