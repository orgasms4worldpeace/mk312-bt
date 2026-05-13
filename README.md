# MK-312BT

DIY build of the **ErosTek ET-312B** e-stim power box, with Bluetooth (HC-05) or WiFi (ESP8266) wireless control. Boards, BOM, firmware, case, and the documentation needed to actually build one.

> ⚠️ **Safety.** This is a high-voltage device. Don't injure yourself. No warranty.

## How to build one

Work through the numbered directories in order. The full step-by-step walkthrough is in **[`build-guide.md`](build-guide.md)**.

| Step | Directory | What you do |
|------|-----------|-------------|
| 1 | [`1-order-boards/`](1-order-boards/) | Send the main-board + front-panel gerbers to JLCPCB |
| 2 | [`2-order-parts/`](2-order-parts/) | Import the BOM into Mouser. Pre-match MOSFETs by Vt — this prevents Error 20 |
| 3 | [`3-build-and-flash/`](3-build-and-flash/) | Solder, print the case, flash the ATmega16A |
| 4 | [`4-wireless/`](4-wireless/) | Pick **Bluetooth** (HC-05) or **WiFi** (ESP8266 — required for macOS / iOS) |
| 5 | [`5-software/`](5-software/) | Pick a control client (links to upstream projects — none bundled) |

If anything misbehaves, [`3-build-and-flash/troubleshooting/`](3-build-and-flash/troubleshooting/) has per-failure-code analyses and the archived metafetish.club forum threads.

## Speculative work in progress

See [`Roadmap.md`](Roadmap.md) for hardware/firmware ideas that haven't been verified end-to-end yet. Nothing in there is on the build path until it lands in the numbered directories.

## What this repo is (and isn't)

A 2026 reorganization of two dormant upstream projects into one build-journey monorepo. Scope: **boards, BOM, firmware, case, build instructions**. Control software stays upstream where it's maintained.

- Upstream for the box: [CrashOverride85/mk312-bt](https://github.com/CrashOverride85/mk312-bt) — boards, firmware, case
- Upstream for the WiFi adapter: [Rangarig/MK312WIFI](https://github.com/Rangarig/MK312WIFI) — pulled into [`4-wireless/wifi/`](4-wireless/wifi/) as a `git subtree`
- Control clients (`mk312-gui`, `ErosWeb`, `three-twelve-bee`, `restim`, etc.): index at [`5-software/`](5-software/) — install whichever from its own repo

This repo is **not** a fork claiming originality, **not** the "official" MK-312BT (there is no official), and **not** a maintained software hub. It's a curation effort with attribution preserved.

### Hardware lineage

```
ErosTek ET-312B               commercial e-stim box (early 2000s, still sold)
└─ metafetish/mk312-bt        community DIY clone, repo deleted ~Dec 2020
   └─ CrashOverride85/mk312-bt   preservation fork, current upstream
      └─ this repo                  2026 reorganization
```

v1.4 board files were DM'd to CrashOverride85 shortly after the metafetish repo was deleted, with no original Eagle source. The design has been built successfully by several people. v1.2 / v1.3 boards (with Eagle source) live in the upstream `CrashOverride85/mk312-bt` repo for anyone who wants to modify the design. Longer story in [`build-guide.md`](build-guide.md#provenance).

### Forum archive

The `metafetish.club` forum — where most community debugging knowledge accumulated — is now offline. Threads on building, Error 20, parts substitution, and firmware live as PDFs in [`3-build-and-flash/troubleshooting/`](3-build-and-flash/troubleshooting/).

## Credit

| Person / project | What they did |
|---|---|
| **CrashOverride85** | Preserved the metafetish repo; ongoing upstream for the box |
| **Rangarig** & **cLx** | MK312WIFI design, schematics, ESP firmware |
| **timduru** | Additional MK312WIFI code contributions |
| **kinkytofu** | [`buttshock-py`](https://github.com/kinkytofu/buttshock-py) — original ET-312 serial-protocol library, predecessor of every Python client |
| **clxjaguar** (cLx) | [`mk312-gui`](https://github.com/clxjaguar/mk312-gui) PyQt client, `mk312-raw-control` |
| **fenbyfluid** | [`three-twelve-bee`](https://github.com/fenbyfluid/three-twelve-bee) web client |
| **boyinsea** | [`ErosWeb`](https://github.com/boyinsea/ErosWeb) sub/dom remote-play client |
| **diglet48** | [`restim`](https://github.com/diglet48/restim) audio-input signal generator |
| **Rubberfate** | [`mk312com`](https://github.com/Rubberfate/mk312com) Python wrapper |
| **Carumbad** | Home Assistant + MQTT bridges |
| **The metafetish.club community** | Board iteration + decades of debug knowledge sitting in the archived threads |
| **ErosTek** | Designers of the ET-312B that this clones |

License: each upstream's original license carries over. New connective material in this repo (READMEs, `build-guide.md`, BOM tooling) is offered freely.

## Getting help

The active community lives in the `#boxes-pulse-based-diy` and `#312-chat` channels on [Joanne's E-Stim Community Discord](https://discord.gg/rY8C27S).
