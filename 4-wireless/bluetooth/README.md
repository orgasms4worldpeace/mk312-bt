# Bluetooth (HC-05)

The original wireless option for the MK-312BT. An HC-05 ZS-040 module plugs into the J9 "Radio Header" socket.

## Files in this directory

| File | What it is |
|------|-----------|
| **[`hc05-setup.md`](hc05-setup.md)** | **Canonical configuration walkthrough.** Wiring, AT-mode entry, per-platform terminal setup (picocom on macOS/Linux, Arduino IDE Serial Monitor or Termite on Windows), every AT command you need, the IPSCAN power tradeoff with comparison table, pairing per OS, and the macOS "Disconnected" cosmetic quirk. **Read this when configuring an HC-05.** |
| `HC05PINOUT.png` | HC-05 inner module pinout. Solder pin 32 (STATE) to the breakout board to drive the front-panel "Radio" LED. |
| `MK-312BT V1.2 HC-05 Initialization ATMEGA16.bin` | One-shot AVR firmware that auto-configures the HC-05 from the box itself — useful only without a USB-TTL adapter. Flash it, plug HC-05 in, power on with HC-05 button held, watch LCD. Then re-flash with the real firmware. |
| `MK-312BT V1.2 HC-05 Initialization ATMEGA16.bas` | BASIC source of the auto-config firmware (BASCOM-AVR), for reference and modification. |
| `AT COMMANDS README.txt` | Original short-form AT command list. Superseded by `hc05-setup.md`. |

## Which HC-05 module to buy

Not all HC-05 modules are equal. After building several units, the **DSD Tech HC-05 Pass-through Module ([Amazon B01G9KSAF6](https://www.amazon.com/DSD-TECH-HC-05-Pass-through-Communication/dp/B01G9KSAF6))** has been the most reliable for mk312-bt builds, for two reasons:

- **Pin 32 (STATE) is already soldered to the breakout board.** This is the #1 fiddly step on cheap clones — you have to manually wire-bridge a 0.5 mm pad on the inner module to drive the front-panel "Radio" LED. The DSD Tech variant ships with this connection already made.
- **Stable AT-mode firmware.** Some JY-MCU and generic ZS-040 clones reject `AT+NAME?` queries even when the name was set successfully (see warning in [`hc05-setup.md`](hc05-setup.md)) and have other quirks. DSD Tech modules pass the standard AT command set without surprises.

Generic ZS-040 modules from random sellers will work too if you're willing to solder pin 32 yourself and tolerate AT-command quirks — but for a build-once, ship-it unit, the DSD Tech version is worth the extra $1–2.

## Quick start

If you'd rather skip the reading: pair as `MK-312BT` with PIN `1234`, but configure those values onto the HC-05 first — it ships as `HC-05` / `1234` / 9600 baud and the box speaks 19200. See [`hc05-setup.md`](hc05-setup.md) for how.

## Heads up

- **macOS Monterey+ has poor Bluetooth Classic SPP support.** HC-05 pairs, but data sessions drop. Use the [WiFi adapter](../wifi/) instead.
- **iOS doesn't speak SPP at all** — WiFi adapter is your only option.
- **HC-05 idle draw is ~43 mA on default settings**, which makes the stock 7805 linear regulator run warm. Either swap to a switching regulator (mEZD71201A-G drop-in) or set `AT+IPSCAN=1024,1,1024,512` to drop idle to ~15 mA. See the IPSCAN section in `hc05-setup.md`.

→ Back to [Step 4 — Wireless](../README.md) | Up to [build guide → Bluetooth](../../docs/build-guide.md#bluetooth-hc-05-configuration)
