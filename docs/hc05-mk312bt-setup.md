# Configuring an HC-05 Bluetooth Module for the mk312-bt

A cross-platform setup guide covering hardware, terminal configuration, the three quirks that quietly break most first-time setups, and the IPSCAN power/responsiveness tradeoff that matters for thermal and battery behavior.

---

## What you need

| Item | Notes |
|---|---|
| HC-05 module | ZS-040 breakout (with onboard button) is easiest |
| USB-to-TTL adapter | FTDI FT232RL or CP2102; must support 3.3V logic |
| 4 jumper wires | Female-to-female if the HC-05 has male headers |
| Terminal program | picocom (macOS/Linux), Arduino Serial Monitor or Termite (Windows) |

Any 3.3V-capable USB-to-TTL adapter will work for the HC-05 step. The DSD TECH SH-U09C5 (with a 1.8/2.5/3.3/5V slide switch) is preferred if you're building a full mk312-bt because the same adapter can later be used on the mk312's LINK port, which requires 1.8–3.6V signal levels.

---

## Wiring

| USB-TTL adapter | HC-05 |
|---|---|
| VCC (3.3V or 5V — both work; ZS-040 has its own regulator) | VCC |
| GND | GND |
| TX | RXD |
| RX | TXD |

The TX/RX cross is the single most common wiring error. Each board's pin labels are written from its own perspective: "TX" on one side connects to "RX" on the other.

If your HC-05 breakout has no button, also wire the adapter's 3.3V output to the HC-05's EN (or KEY) pin. If it has a button, leave EN unconnected.

---

## Entering AT mode

The HC-05 has two operating modes:

- **Data mode** — normal Bluetooth operation; runs at the configured baud (default 9600). AT commands ignored.
- **AT/command mode** — runs at a fixed 38400 baud. Accepts configuration commands.

To enter AT mode:

1. Disconnect VCC from the HC-05.
2. Press and hold the button on the breakout.
3. Reconnect VCC.
4. Release the button after ~2 seconds.

The status LED should now blink slowly, roughly once every 2 seconds. Fast blinking (~2 per second) means it booted into data mode and AT commands will not work — power-cycle and try again.

---

## Why first-time setups fail

The HC-05 has three undocumented behaviors that quietly break naive terminal sessions:

1. **No local echo.** Characters you type are not echoed. The screen stays blank until the module replies, so it feels like the keyboard is dead.
2. **Requires CR+LF line endings.** Every command must terminate with `\r\n`. Most terminals send only `\r` on Enter, and the module silently waits for a `\n` that never arrives.
3. **AT mode is hard-coded to 38400 baud.** Whatever baud you set with `AT+UART` applies only to data mode. Command mode is always 38400.

Nearly every "my HC-05 doesn't respond" thread online is one of these three.

---

## Connecting the terminal

### macOS

Find the device:

```
ls /dev/cu.usbserial-*
```

Connect:

```
picocom -b 38400 --omap crcrlf --echo /dev/cu.usbserial-XXXXXXXX
```

Install picocom via Homebrew if needed: `brew install picocom`.

Exit with `Ctrl-A` then `Ctrl-X`.

### Linux

Find the device:

```
ls /dev/ttyUSB*
```

Connect:

```
picocom -b 38400 --omap crcrlf --echo /dev/ttyUSB0
```

Install picocom: `sudo apt install picocom` (Debian/Ubuntu) or equivalent.

If you get a permission error, add yourself to the dialout group: `sudo usermod -aG dialout $USER`, then log out and back in.

### Windows

The COM port appears in Device Manager → Ports (COM & LPT) as "USB Serial Port (COMx)".

The simplest option is the **Arduino IDE Serial Monitor**:

1. Tools → Port → select COMx
2. Open Serial Monitor (magnifying-glass icon)
3. Baud rate dropdown (bottom right): **38400**
4. Line ending dropdown: **Both NL & CR**

Type commands in the input box and press Enter.

**Termite** (free, from CompuPhase) is also a clean option. Configure: 38400 baud, 8N1, "Append CR-LF" enabled, "Local echo" enabled.

PuTTY works but is fiddlier — it doesn't natively send CR+LF on Enter, requiring manual CTRL-J after each Enter, or workaround scripts. Avoid PuTTY for this task unless it's already installed and you don't want to add another tool.

---

## Verifying communication

Type:

```
AT
```

Press Enter. Expected reply: `OK`.

| Reply | Meaning |
|---|---|
| `OK` | Working correctly |
| `ERROR:(0)` | Command not recognized — almost always missing `\n` line ending |
| (nothing) | Wiring (TX/RX swap), wrong baud, or not in AT mode |

---

## Configuration for the mk312-bt

Once `AT` returns `OK`, send these in order. Each should reply `OK`.

```
AT+NAME=MK-312BT
AT+UART=19200,0,0
AT+PSWD=1234
AT+POLAR=1,1
```

| Command | Purpose |
|---|---|
| `AT+NAME=MK-312BT` | Bluetooth advertising name |
| `AT+UART=19200,0,0` | Data-mode baud / 1 stop bit / no parity — matches the mk312's ATmega16 |
| `AT+PSWD=1234` | Pairing PIN |
| `AT+POLAR=1,1` | LED polarity for the radio LED on the mk312 front panel |

The IPSCAN command from the original mk312-bt repo is intentionally omitted here — it deserves its own section because the right value depends on your build.

---

## The IPSCAN tradeoff

`AT+IPSCAN` controls how often the HC-05's radio listens for inquiries (new devices wanting to discover it) and pages (already-paired devices wanting to reconnect). Format:

```
AT+IPSCAN=<inq_interval>,<inq_window>,<page_interval>,<page_window>
```

All four values are in 0.625ms units. The window must be ≤ the interval. The window-to-interval ratio is the radio's listening duty cycle.

| Pair | Controls |
|---|---|
| `inq_interval, inq_window` | Discovery by new (unpaired) devices |
| `page_interval, page_window` | Reconnection by already-paired devices |

### Three sensible settings

| Setting | Idle draw | New-device discovery | Paired reconnect | Best for |
|---|---|---|---|---|
| `1024,512,1024,512` (HC-05 default) | ~43 mA | <5 s | <2 s | Switching regulator installed, or always wall-powered |
| `1024,1,1024,512` (hybrid) | ~15–20 mA | 30 s – minutes | <2 s | Stock 7805, fast reconnect priority |
| `1024,1,1024,1` (mk312 repo default) | ~5–8 mA | 30 s – minutes | 30 s+ | Stock 7805, battery-life priority |

### Why the mk312 repo picks the most aggressive setting

The mk312-bt project ships with `1024,1,1024,1` because the stock 7805 linear regulator must dissipate the HC-05's 43mA idle draw as heat at 12V input — enough to make the regulator noticeably warm. Reducing both duty cycles to ~0.1% drops idle current to roughly 5–8mA, eliminating the thermal load and substantially extending battery life.

The cost is responsiveness. Cold discovery may take a minute or more. More importantly, even already-paired devices will take 30+ seconds to reconnect after every power-on, because the page-scan window is narrower than most hosts' default page-scan timeouts.

### The hybrid is the practical sweet spot

`1024,1,1024,512` cuts the inquiry-scan to near zero — where most of the idle current goes, since the radio is broadcasting "I exist" continuously to nobody — while keeping page-scan at the default duty cycle so paired devices reconnect promptly. Discovery of new devices is slow, but that only matters during initial pairing, and you can temporarily revert to the default just for that one event.

### If you've installed a switching regulator

The cLx article (clx.freeshell.org/mk312bt.html) recommends replacing the 7805 with a drop-in 5V switching regulator such as the Texas Instruments mEZD71201A-G. With that mod, the thermal pressure is gone and battery life is markedly better even at full HC-05 idle draw. Use the default `1024,512,1024,512` and get fast everything with no tradeoff.

### Applying your choice

Re-enter AT mode and send the command:

```
AT+IPSCAN=1024,1,1024,512
```

(or whichever value you've chosen). Other settings are unaffected. IPSCAN can be changed independently any time.

---

## Verifying the configuration

Re-enter AT mode and read back the values:

```
AT+NAME?
AT+UART?
AT+PSWD?
AT+IPSCAN?
```

Confirm each response matches what you set. Common readback formats:

```
+NAME:MK-312BT
+UART:19200,0,0
+PSWD:"1234"
+IPSCAN:1024,1,1024,512
```

(Quote style on `PSWD` varies by firmware revision.)

---

## Pairing

Exit AT mode (close picocom or terminal) and power-cycle the HC-05 **without** holding the button. The LED should now blink fast — data mode, ready to advertise.

Pair from your host as you would any Bluetooth device, using PIN `1234`. The host will assign a serial port to the bonded device.

| Platform | Serial port path |
|---|---|
| macOS | `/dev/cu.MK-312BT` (or similar) |
| Linux | `/dev/rfcomm0` after `sudo rfcomm bind 0 <MAC>` |
| Windows | `COMx` — assigned automatically; visible in Device Manager |

### macOS quirk: "Disconnected" in the Bluetooth panel

On macOS, the System Settings Bluetooth panel will display "Disconnected" 15–30 seconds after pairing, even though pairing succeeded. This is documented Apple behavior across multiple HC-05/Classic-SPP forum threads — macOS only maintains an active RFCOMM channel when an application has the serial port open. The pairing/bonding is permanent.

To verify pairing actually worked:

```
ls /dev/cu.MK-312BT*
```

If the device exists, you're paired. Open it from any application and the panel will flip back to "Connected":

```
picocom -b 19200 /dev/cu.MK-312BT
```

Linux and Windows do not exhibit this cosmetic issue.

---

## Reconfiguring later

Settings persist in the HC-05's flash and survive power cycles. To change them later — including after the module is installed in the mk312 — there's no need to desolder anything: pull the HC-05 daughterboard, jumper to the USB-to-TTL adapter exactly as in the wiring section, hold the button during power-up, and you're back at the AT prompt at 38400 baud.

The mk312 also accepts an RS232 cable plugged into its LINK port, which physically disconnects the Bluetooth module — useful for debugging if the Bluetooth side ever misbehaves in the field.

---

## Quick reference

**Connect (macOS/Linux):**
```
picocom -b 38400 --omap crcrlf --echo <device>
```

**Configure for mk312-bt:**
```
AT+NAME=MK-312BT
AT+UART=19200,0,0
AT+PSWD=1234
AT+POLAR=1,1
AT+IPSCAN=1024,1,1024,512
```

**Verify:**
```
AT+NAME?
AT+UART?
AT+PSWD?
AT+IPSCAN?
```

**Exit picocom:** `Ctrl-A` then `Ctrl-X`.
