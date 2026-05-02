# Step 4 — Wireless control

The MK-312BT exposes a serial protocol on the same header that drives the wireless module. Pick one of two pin-compatible options:

## Bluetooth (HC-05) — [`bluetooth/`](bluetooth/)

- **Original / canonical** option. Uses an HC-05 ZS-040 module
- Cheapest, most documented, works with any Bluetooth Classic SPP client
- Pairing: `MK-312BT` / pin `1234`
- Range and reliability hit the usual Bluetooth Classic limits
- Auto-config flow: flash a one-time `.bin` to the AVR that AT-configures the HC-05 for you. See [`bluetooth/hc05-setup.md`](bluetooth/hc05-setup.md)

## WiFi (ESP8266) — [`wifi/`](wifi/)

- **Drop-in replacement** for the HC-05 — pin-compatible. Plug an ESP8266-01S module into the same socket.
- Better range and reliability than Bluetooth, easier integration with VR and network apps
- Configuration: power on → device boots into AP mode (`WifiAP` shown on LCD) → connect with phone → set your WiFi → device joins the network and shows its IP on the LCD
- Communication: UDP broadcast `MK312-ICQ` on port 8842 returns the device IP, then TCP on port 8843 (one client at a time)
- Source: [Rangarig/MK312WIFI](https://github.com/Rangarig/MK312WIFI), pulled in as a git subtree
- Includes the ESP firmware (Arduino), a custom KiCad PCB design, and a .NET example client

### Ordering the adapter PCB — [`wifi/pcb/jlcpcb-package/`](wifi/pcb/jlcpcb-package/)

Drop-in upload bundle for **JLCPCB SMT-only assembly**: gerbers, BOM, and CPL prebuilt. JLC pre-mounts the only SMD part (U1, AMS1117-3.3 regulator); you hand-solder the 6 through-hole parts (caps, transistor, button, headers). ~$20-25 for 5 boards. See [`wifi/pcb/jlcpcb-package/README.md`](wifi/pcb/jlcpcb-package/README.md) for the upload walkthrough and THT parts shopping list.

## Which should I use?

| Use case | Pick |
|----------|------|
| Standard / phone app control | Bluetooth (HC-05) |
| VR headset, network app, or "BT just doesn't work for me" | WiFi (ESP8266) |
| Scripting the protocol from Python or Unity | WiFi — TCP is friendlier than rfcomm |

## The serial header is the same for both

Both modules use the same physical pinout (TX/RX/GND/VCC/STATE) on the MK-312BT mainboard. Swap between them without changing the box itself.

## Open question — OSOYOO ESP8266 module as a third option?

The [OSOYOO ESP8266 WiFi module](https://osoyoo.com/2020/12/20/osoyoo-esp8266-wi-fi-module/) advertises itself as a 6-pin module in HC-05 footprint with a built-in 5V→3.3V converter. If true, it would physically drop into the same socket as the HC-05 with no MK312WIFI PCB to fabricate.

**Status: unverified — likely won't "just work."** The product page documents 5V tolerance and a 6-pin layout (VCC, GND, E_RX, E_TX, RST, KEY), but stays silent on the two questions that decide whether it functions as a transparent serial-over-WiFi bridge:

- Does it ship with a transparent UART-over-TCP/UDP bridge mode out of the box, or only AT-command operation? Their tutorials reference AiThinker firmware, which is AT-controlled — the host sends AT commands rather than reading/writing serial bytes.
- Can the baud rate be set to **19200** (what the MK-312BT speaks)?

Even with "yes" to both, the existing client software ([clxjaguar/mk312-gui upstream](https://github.com/clxjaguar/mk312-gui) and the [.NET reference client](wifi/DotNetClient/) bundled here) speaks the MK312WIFI protocol (UDP `MK312-ICQ` discovery on port 8842, TCP control on 8843) — an OSOYOO module won't speak that without custom firmware. You'd need to fork the GUI's transport, write a small bridge, or flash MK312Wifi.ino onto the OSOYOO module (assuming GPIO0/1/2/3 are accessible — they may not be).

**TL;DR:** physically a candidate; protocol-wise unproven and probably needs work. Stick with [`wifi/`](wifi/) (build the small PCB) unless you want to experiment on the firmware and client.
