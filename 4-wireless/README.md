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
