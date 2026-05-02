# Step 5 — Software

Once the box is built, flashed, and equipped with a wireless adapter (or wired through the LINK port with an RS-232 cable), you need a client to control it. **This directory is a links-only index** — no bundled forks. Use the upstream projects directly.

Earlier versions of this repo bundled `clxjaguar/mk312-gui` as a git subtree. The 2026-04 cleanup removed it — this repo focuses on the hardware/PCB/firmware stack, not on maintaining forks of someone else's control GUI. Pick whichever client below matches your transport and platform, and follow its install instructions.

The MK312WIFI bundled .NET reference client at [`../4-wireless/wifi/DotNetClient/`](../4-wireless/wifi/DotNetClient/) stays in place — part of the upstream MK312WIFI package (shipped alongside the firmware and PCB) and a useful Unity/VR starting point. Not an end-user GUI.

## Recommended

| Client | Transport | Platform | Status | When to pick |
|--------|-----------|----------|--------|--------------|
| **[clxjaguar/mk312-gui](https://github.com/clxjaguar/mk312-gui)** | LINK serial cable, **MK312WIFI bridge** (UDP/TCP) | Win/Mac/Linux (PyQt5) | Active 2025-10 | **Default pick.** Speaks the WiFi-adapter protocol natively (cLx co-authored MK312WIFI). The canonical PyQt control GUI. |
| **[fenbyfluid/three-twelve-bee](https://github.com/fenbyfluid/three-twelve-bee)** ([live demo](https://three-twelve-bee.netlify.app)) | Web Serial API (Chrome/Edge) | Any OS with Chrome/Edge | Stale 2024-01 | Browser-based — no install. Targets ET-312 specifically; protocol-compatible with MK-312-BT. Ships the ErosLink routine viewer. |
| **[boyinsea/ErosWeb](https://github.com/boyinsea/ErosWeb)** | Web Serial API (USB-serial cable to LINK port) | Mac/Win/iPad (Chrome/Edge for sub) | Stale 2020-10 | Sub/Dom remote-play architecture with PeerJS voice/video built in. |

## Other / specialized

| Project | What | Notes |
|---------|------|-------|
| [clxjaguar/mk312-raw-control](https://github.com/clxjaguar/mk312-raw-control) | Python "link mode" override via serial — for protocol experimentation | Active 2026-02 |
| [diglet48/restim](https://github.com/diglet48/restim) | Audio-input signal generator (funscript / video sync) | Active 2026-04. **Caveat:** the restim wiki's [commercial-hardware page](https://github.com/diglet48/restim/wiki/commercial-hardware) admits the 312-family audio-input integration is theoretically capable but **never validated end-to-end**. Treat as experimental. |
| [Rubberfate/mk312com](https://github.com/Rubberfate/mk312com) | Lower-level Python wrapper library | Stale 2021. A library, not a GUI — useful for custom integrations. |
| [Carumbad/HomeAssistant_ET312](https://github.com/Carumbad/HomeAssistant_ET312) | Home Assistant integration | Active 2026-04. ET-312 native, protocol-compatible with MK-312-BT. |
| [Carumbad/et312_mqtt](https://github.com/Carumbad/et312_mqtt) | MQTT bridge | Stale 2020. |
| [kinkytofu/buttshock-py](https://github.com/kinkytofu/buttshock-py) | Original Python ET-312 protocol library | Archived 2016 — historical reference, predecessor of all the above. |

## What's in the MK312WIFI bundle (for completeness)

(See note above on the .NET reference client at [`../4-wireless/wifi/DotNetClient/`](../4-wireless/wifi/DotNetClient/) — kept with the WiFi package as upstream shipped it.)

## Bluetooth (HC-05) clients?

If you went the bluetooth route in step 4, **none of the above speak Bluetooth Classic SPP** — they're all serial-cable or WiFi-bridge clients. Options:

- An Android app from the e-stim community (search the [#312-chat Discord](https://discord.gg/rY8C27S) channel)
- A serial-over-Bluetooth shim on Windows/Linux (HC-05 paired as virtual COM port)
- **macOS users: HC-05 won't work reliably** because Apple deprecated SPP. Use the WiFi adapter instead.

## What you need physically

Whatever client you pick, you'll need one of:
- An **MK312WIFI adapter** (built per [`../4-wireless/wifi/`](../4-wireless/wifi/)) — pin-compatible drop-in for the HC-05 socket, talks WiFi
- An **HC-05 module** (BOM-listed) — works on Win/Linux/Android, **broken on macOS Monterey+**
- A **USB-to-RS232 cable** for the LINK port (BOM lists the [DSD-TECH FT232RL cable](https://www.amazon.com/DSD-TECH-RS232-Serial-FT232RL/dp/B07XXWVH69/) under "PC Link Cable") — works everywhere
