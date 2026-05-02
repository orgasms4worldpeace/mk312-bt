# MK-312BT

DIY clone of the ErosTek ET-312B e-stim power box, with bluetooth (HC-05) and optional WiFi (ESP8266) wireless control. This repo consolidates two abandoned upstreams into one 2026 reorganization:

- [CrashOverride85/mk312-bt](https://github.com/CrashOverride85/mk312-bt) — the box itself (boards, BOM, firmware, case)
- [Rangarig/MK312WIFI](https://github.com/Rangarig/MK312WIFI) — drop-in WiFi adapter, pulled into [`4-wireless/wifi/`](4-wireless/wifi/) as a git subtree

Control software (mk312-gui, ErosWeb, three-twelve-bee, restim, etc.) is **not bundled** — [`5-software/`](5-software/) is a links-only index pointing at upstream projects. Pick whichever fits your platform.

Credit for the original work goes to the upstream authors. Everything here ships under each upstream's original license.

## How to build one

The top-level layout follows the build path. Work through the numbered directories in order:

| Step | Directory | What you do |
|------|-----------|-------------|
| 1 | [`1-order-boards/`](1-order-boards/) | Send PCB gerbers to a fab (JLCPCB / PCBWay / etc.) |
| 2 | [`2-order-parts/`](2-order-parts/) | Import the BOM into Mouser, source remaining parts |
| 3 | [`3-build-and-flash/`](3-build-and-flash/) | Solder, print the case, flash the AVR |
| 4 | [`4-wireless/`](4-wireless/) | Pick **bluetooth** (HC-05) or **wifi** (ESP8266) — both pin-compatible |
| 5 | [`5-software/`](5-software/) | Pick a control client — links-only index of PyQt, web, and Python options |

For the end-to-end walkthrough, see **[docs/build-guide.md](docs/build-guide.md)**.

## Reference

- [`docs/build-guide.md`](docs/build-guide.md) — full assembly + flashing walkthrough
- [`docs/troubleshooting/`](docs/troubleshooting/) — original debug notes (annotated test-methodology PDF, F21 disassembly analysis) plus archived threads from the now-offline metafetish.club forum
- [`historical/`](historical/) — v1.2 / v1.3 boards, original Eagle source, build photos. Archaeology only; **don't build these today**

## Provenance & scope

### What this is

A 2026 reorganization of the dormant upstreams listed below into one build-journey monorepo. The numbered top-level directories (`1-order-boards/` → `5-software/`) encode the build sequence, so a newcomer walks the repo linearly instead of hunting across half a dozen abandoned projects. Scope: **boards, BOM, firmware, case, and build instructions**. Control software stays upstream where it's maintained.

This repo is **not** a fork claiming originality, **not** the "official" anything (there is no official), and **not** a maintained software hub. It's a curation and rehoming effort with attribution preserved.

### Hardware lineage

```
ErosTek ET-312B           commercial e-stim box (early 2000s, still sold)
   └─ metafetish/mk312-bt    community DIY clone, repo deleted ~Dec 2020
       └─ CrashOverride85/mk312-bt   preservation fork, current upstream for the box
           └─ this repo                 2026 reorganization
```

The v1.4 board files have hazy provenance — DM'd to CrashOverride85 shortly after the metafetish repo was deleted, with no original Eagle source. Several people have nonetheless built the design successfully. The older v1.2 / v1.3 boards (with original Eagle source) live in [`historical/`](historical/) for reference. Longer story in [`docs/build-guide.md`](docs/build-guide.md#provenance).

### WiFi adapter lineage

The optional WiFi adapter at [`4-wireless/wifi/`](4-wireless/wifi/) comes from [Rangarig/MK312WIFI](https://github.com/Rangarig/MK312WIFI) — a collaboration between **Rangarig** and **cLx**, with additional imports from [timduru's branch](https://github.com/timduru/MK312WIFI/commits/timdev/). It's pulled in as a `git subtree` (the only remaining bundled upstream after the 2026-04 cleanup), internally renamed for layout consistency (`MK312Wifi/` → `firmware/`, `MK312-wifi-pcb/` → `pcb/`) but otherwise unmodified. Upstream is dormant (last commit ~2020). The .NET reference client stays where upstream shipped it, at [`4-wireless/wifi/DotNetClient/`](4-wireless/wifi/DotNetClient/).

### Control software

[`5-software/`](5-software/) is a **links-only index**. Earlier versions of this repo bundled `clxjaguar/mk312-gui` (and briefly the .NET client) as subtrees; the 2026-04 cleanup unbundled both to keep scope on the hardware/firmware stack. The library that started it all — and the predecessor of every Python client listed in `5-software/` — is [kinkytofu/buttshock-py](https://github.com/kinkytofu/buttshock-py) (archived 2016), which first reverse-engineered the ET-312 serial protocol.

### Forum archive

The `metafetish.club` forum, where most community debugging knowledge accumulated, is now offline. Threads on building, Error 20, parts substitution, and firmware live as PDFs in [`docs/troubleshooting/`](docs/troubleshooting/).

### Credit

- **CrashOverride85** — preservation of the metafetish repo + ongoing upstream for the box
- **Rangarig** and **cLx** — MK312WIFI design, schematics, ESP firmware
- **timduru** — additional MK312WIFI code contributions
- **kinkytofu** — original ET-312 serial protocol library (`buttshock-py`)
- **clxjaguar** (cLx) — `mk312-gui` PyQt client, `mk312-raw-control`
- **fenbyfluid** — `three-twelve-bee` web client
- **boyinsea** — `ErosWeb` sub/dom remote-play client
- **diglet48** — `restim` audio-input signal generator
- **Rubberfate** — `mk312com` Python wrapper
- **Carumbad** — Home Assistant + MQTT bridges
- **The metafetish.club community** — board iteration plus decades of debug knowledge sitting in the archived threads
- **ErosTek** — designers of the ET-312B that this clones

License: whatever each upstream shipped with. This reorganization imposes no additional license — directories from upstream keep their upstream license; the new connective material (READMEs, build guide, BOM tooling) is offered freely.

## Getting help

The active community lives in the `#boxes-pulse-based-diy` and `#312-chat` channels on [Joanne's E-Stim Community Discord](https://discord.gg/rY8C27S).

## Safety

This is a high-voltage e-stim device. Don't injure yourself. The upstream authors and this maintainer take no responsibility for what you do with it.
