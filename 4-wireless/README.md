# Step 4 — Wireless control

The MK-312BT exposes a serial protocol on the same header used by the wireless module. You have two pin-compatible options — pick one:

## Bluetooth (HC-05) — [`bluetooth/`](bluetooth/)

- **Original / canonical** option. Uses an HC-05 ZS-040 module
- Cheapest, most documented, works with any Bluetooth Classic SPP client
- Pairing: `MK-312BT` / pin `1234`
- Range / reliability are the usual Bluetooth Classic limitations
- Auto-config flow available — flash a one-time `.bin` to the AVR that AT-configures the HC-05 for you. See [`bluetooth/hc05-setup.md`](bluetooth/hc05-setup.md)

## WiFi (ESP8266) — [`wifi/`](wifi/)

- **Drop-in replacement** for the HC-05 — pin-compatible, just plug the ESP8266-01S module in instead
- Better range, more reliable than Bluetooth, easier integration with VR / network apps
- Configuration: power on → device boots into AP mode (`WifiAP` shown on LCD) → connect with phone → set your WiFi → device joins network and shows IP on LCD
- Communication: UDP broadcast `MK312-ICQ` on port 8842 returns the device IP, then TCP on port 8843 (single client at a time)
- Source: [Rangarig/MK312WIFI](https://github.com/Rangarig/MK312WIFI), pulled in as a git subtree
- Includes the ESP firmware (Arduino), a custom KiCad PCB design, and a .NET example client

## Which should I use?

| Use case | Pick |
|----------|------|
| Standard / phone app control | Bluetooth (HC-05) |
| VR headset, network app, or "BT just doesn't work for me" | WiFi (ESP8266) |
| You want to play with the protocol from a script / Unity | WiFi — TCP is friendlier than rfcomm |

## The serial header is the same for both

Both modules use the same physical pinout (TX/RX/GND/VCC/STATE) on the MK-312BT mainboard. You can swap between them without changing the box itself.
