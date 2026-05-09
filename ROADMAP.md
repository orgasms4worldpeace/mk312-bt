# Roadmap

Speculative ideas, unverified hardware, and "would be nice if" investigations that aren't part of the build path. Move items into the main docs only after they're verified end-to-end on real hardware.

---

## OSOYOO ESP8266 module as a third wireless option

The [OSOYOO ESP8266 WiFi module](https://osoyoo.com/2020/12/20/osoyoo-esp8266-wi-fi-module/) advertises itself as a 6-pin module in HC-05 footprint with a built-in 5 V → 3.3 V converter. If true, it would physically drop into the same socket as the HC-05 with no MK312WIFI PCB to fabricate.

**Status: unverified — likely won't "just work."** The product page documents 5 V tolerance and a 6-pin layout (VCC, GND, E_RX, E_TX, RST, KEY), but stays silent on the two questions that decide whether it functions as a transparent serial-over-WiFi bridge:

- Does it ship with a transparent UART-over-TCP/UDP bridge mode out of the box, or only AT-command operation? Their tutorials reference AiThinker firmware, which is AT-controlled — the host sends AT commands rather than reading/writing serial bytes.
- Can the baud rate be set to **19200** (what the MK-312BT speaks)?

Even with "yes" to both, the existing client software ([clxjaguar/mk312-gui upstream](https://github.com/clxjaguar/mk312-gui) and the [.NET reference client](4-wireless/wifi/DotNetClient/) bundled here) speaks the MK312WIFI protocol (UDP `MK312-ICQ` discovery on port 8842, TCP control on 8843) — an OSOYOO module won't speak that without custom firmware. You'd need to fork the GUI's transport, write a small bridge, or flash MK312Wifi.ino onto the OSOYOO module (assuming GPIO0/1/2/3 are accessible — they may not be).

**TL;DR:** physically a candidate; protocol-wise unproven and probably needs work. Stick with [`4-wireless/wifi/`](4-wireless/wifi/) (build the small PCB) unless you want to experiment on the firmware and client.

---

## bkifft/MK-312WS — alternative ESP32 wireless adapter

[`bkifft/MK-312WS`](https://github.com/bkifft/MK-312WS) is an ESP32-based webserver replacement for the HC-05 socket. ESP32 D1 Mini dev board plugs into a small carrier PCB (KiCad source + gerbers v1/v2/v3 included; v4 marked buggy by the author). Browser-only UI at `http://mk-312ws.local`, no separate client software install.

bkifft is the same builder from the Metafetish forum threads (#8 in the parts substitution thread) — real engineering, not a hobby drive-by. 16 stars, last commit 2022-10-02 (~3.5 years dormant).

### Why it's interesting

- No SMT assembly required — plug an off-the-shelf ESP32 dev board into the carrier
- No client software install — any browser works
- Bigger MCU (ESP32 vs ESP-01S) gives headroom for future features
- Built-in GUI with knobs, mode select, battery display

### Why it's NOT a replacement for the current Rangarig MK312WIFI

Looked at the actual source (`MK-312WS.ino`, `mk312.cpp`, `mk312.h`):

| Feature | Rangarig MK312WIFI | bkifft MK-312WS |
|---|---|---|
| Mode select | ✅ | ✅ |
| Read battery | ✅ | ✅ |
| LevelA / LevelB direct write | ✅ | ❌ planned |
| MultiAdjust (MA) | ✅ | ❌ planned |
| startRamp | ✅ | ❌ commented out in source |
| CutLevels | ✅ | ❌ |
| DisableADC / EnableADC (pot override) | ✅ | ❌ |
| User program upload | ✅ via raw protocol | ❌ planned |
| EEPROM read/write | ✅ via raw protocol | ❌ |
| Recording / playback | ❌ | ❌ planned |
| **Raw protocol proxy** (lets mk312-gui, .NET ref, ErosWeb, three-twelve-bee connect) | ✅ TCP 8843 | ❌ — `handleWebSocketMessage_ws_bytes()` is an empty function; "raw byte websocket" is in the author's `2do.txt` |
| Encryption | ✅ optional | ❌ |
| Configurable AP password | ✅ | ❌ hardcoded `12345678` |

The web UI exposes a fraction of the box's capability, and the empty byte-passthrough means no existing client software can talk to it. The repo went dormant before shipping the planned features.

### Bar to make this the default

- Wire up the empty `handleWebSocketMessage_ws_bytes()` to proxy raw bytes (the table-stakes feature) — would let existing clients connect
- Or: ship the listed planned features in the web UI to reach UI-only feature parity with mk312-gui
- Active maintenance (or someone forking it forward)
- Make the AP password configurable
- Resolve the unanswered "bt overrules webserver?" note in `notes.txt`

Until then: alternative to investigate, not a replacement.
