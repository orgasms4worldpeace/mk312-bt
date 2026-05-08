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
