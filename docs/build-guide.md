# MK-312BT build guide

Comprehensive end-to-end walkthrough — board ordering, parts, assembly, firmware, and HC-05 bluetooth configuration. For the at-a-glance journey, see the [root README](../README.md).

## Provenance

The "original" content here came from the `metafetish/mk312-bt` repo at the point it was deleted (~27 Dec 2020), preserved by [CrashOverride85](https://github.com/CrashOverride85/mk312-bt). v1.4 files (gerbers, schematics, notes — no Eagle source) were DM'd to that maintainer shortly after the original was deleted; provenance of v1.4 itself is hazy but the design has been successfully built by several people. See the [v1.4 release notes](../1-order-boards/v1.4-release-notes.txt) for changes vs v1.3 before ordering parts.

The metafetish.club forum is now offline — surviving posts are archived in [`troubleshooting/`](troubleshooting/).

The active community lives in the `#boxes-pulse-based-diy` and `#312-chat` channels on [Joanne's E-Stim Community Discord](https://discord.gg/rY8C27S).


## Parts ordering information

See the Documentation link above for BOMs.

Prebuilt Mouser cart for electronic components of the v1.3R board:
https://www.mouser.com/ProjectManager/ProjectDetail.aspx?AccessID=a2725b2f11

You will still need screws/standoffs/cases etc, which can be sourced
elsewhere as listed in the spreadsheet.

## Board ordering instructions

Preferred board house is https://jlcpcb.com

You'll need 2 gerber zip files (click links to download):

- [v1.2 Front Panel](../1-order-boards/gerbers/v1.2-front-panel.zip) — the front panel design hasn't changed since v1.2
- [v1.4 Main Board](../1-order-boards/gerbers/v1.4-main-board.zip) — current main board revision

**NOTE:** Order Front Panel and Main Board as seperate items (but they
can be in the same cart), due to difference in "Different Design"
setting. See below.

- 2 Layer PCB and Dimensions should be detected when you upload the
  zip with the gerbers
- Quantity: No requirement, choose whatever you like
- Thickness: 1.6
- PCB Color:
   - Main Boards: No requirement, choose whatever you like
   - Front Panel: Black is recommended, but not required. Choose whatever you like otherwise.
- Surface finish: HASL
- Copper weight: 1oz
- Gold fingers: No
- Material: Standard FR4
- Panel by jlcpcb: No
- Different Design 
   - Main Boards: 2
   - Front Panel: 1
- Remarks:
   - Main Boards: V Score the Main Boards panel as indicated.
   - Front Panel: Place all Fab Markings (Serial Numbers/Date Codes) on the BOTTOM side of the front panel board.
   
## Error 20: match the MOSFETs before you solder

Error 20 is by far the most common first-boot failure. It almost always traces to mismatched MOSFETs — when the IRL520 quartet or the IRF9Z24 pair have meaningfully different gate threshold voltages (Vt), the output stage can't keep R32 and R43 balanced and the firmware throws Error 20. The DAC (LTC1661) can contribute too, but the MOSFETs are the dominant cause and the only one you can prevent with five minutes of measurement.

**Before soldering**, measure the Vt of every IRL520 and every IRF9Z24 with a component tester (a cheap one that works fine: [amazon.com/dp/B0DDBPWYP8](https://www.amazon.com/dp/B0DDBPWYP8)). Group them by Vt and pick a tight set for each board:

- Bad set — `Vt = 1.82 V, 1.91 V, 2.21 V, 2.34 V` — half a volt of spread, will probably throw Error 20
- Good set — `Vt = 1.90 V, 1.91 V, 1.91 V, 1.92 V` — within ~20 mV, works reliably

Use four closely-matched IRL520s for one board, and likewise pair up the two IRF9Z24s.

**If the board is already built and Error 20 shows up**, measure the DC voltage across R32 and across R43 with the unit powered on:

- Both should read between **4.0 V and 4.4 V**.
- Far more important: **the two readings should be very close to each other**. A clear difference between R32 and R43 is the smoking gun for a MOSFET mismatch.

If R32 and R43 are matched and in range, the FETs aren't the issue — check FET orientation, transformer orientation, and that R35/R46 are 200 kΩ. If R32 and R43 are mismatched, the practical fix is to desolder the MOSFETs and drop in a matched set.

Background reading: [`troubleshooting/MK-312BT Failure 20 - Estim - Metafetish.pdf`](troubleshooting/MK-312BT%20Failure%2020%20-%20Estim%20-%20Metafetish.pdf).

## Board Assembly Instructions - IMPORTANT

1. Trim Potentiometer knobs to correct length if desired
2. Use black permanent marker to black out front panel hole walls if
   desired
3. Cut the tabs off of the base of the pots so the board sits flush
   with the display facade if desired
4. To correctly fit LCD - solder header to LCD board first. Next
   insert LCD panel into front panel daughter board. Then put screws
   on front panel facade and finger tighten M2.5 screws first. Adjust
   positions as needed so everything lines up and sits well. Finally
   solder LCD header to front panel daughter board.
5. Make sure Pin 32 (LED2) on the HC-05 module is actually soldered
   and making connection to the ZS-040 break out board or "Radio" LED
   may not function on the front panel
6. Be very careful not to bridge pins when soldering the LM 2941
   (U14). Apply heat to 1 pad only and carefully apply solder. If a
   bridge occurs - remove the IC, clean the pads throughly with flux
   and solder wick and then retry. Pins 2 and 3 can be bridged because
   they are both ground. Ensure that no other pins are bridged. Check
   with multimeter continuity tester for bridges before power on!
7. Make sure to check the orientation of all electrolytic caps. (+)
   indicates the positive and a solid white "|" indicates the negative.
8. **MAKE SURE YOUR POWER PLUG IS CENTER POSITIVE OR THINGS WILL GO
   BADLY.** If you fuck up and plug in a reversed polarity supply -
   replace electrolytic caps C1 and C4.
9. Please remember to adjust the LCD contrast potentiometer - if
   incorrectly set the unit and backlight will power on but the
   interface will not be displayed.
10. Place transformers with P facing the output jacks (yes we are
    using the transformers "backwards" if you follow orientation given
    in the transformer datasheet )
11. Trim pins of 4066 IC (U3) Socket on the front panel board flush
    before soldering so buttons can clear. If the buttons still
    interfere, carefully disassemble the button and cut off the bit of
    the plastic housing that interferes with the 4066 IC socket pins.
12. Using side cutters cut off the screw boss/screw mount on the case
    that touches/interferes with the ribbon cable socket on the
    display board.
13. The LCD display has metal retention tabs that may short the
    soldered leads of C43. When installing the display board ensure
    that this does not happen (shorten the capacitor leads and bend
    the offending metal tab out of the way if necessary
14. If Error 20 is encountered on first boot, see the **Error 20** section above — it covers MOSFET matching (the usual cause) and the R32/R43 voltage check that diagnoses it.

## Firmware: flashing the AVR

The board uses an **ATmega16A** clocked from an external **8 MHz crystal**. Flashing has three steps regardless of platform: connect a programmer to the 6-pin ISP header (JP1), set fuses so the chip uses the crystal, then write the firmware. The firmware itself is a raw `.bin` file that you can pull straight out of [`3-build-and-flash/firmware/`](../3-build-and-flash/firmware/).

### Pick a firmware

| File | What it is |
|------|-----------|
| `cr-custom-boot-messages/f005-HelloFriend.bin` | Patched frankenbutt-f005 with a "Hello Friend" boot screen — **recommended default**. |
| `cr-custom-boot-messages/f005-ElectrodesReady.bin` | Same firmware, "Electrodes Ready" boot screen. |
| `other-fw/f005.bin` | Unpatched frankenbutt-f005 (no custom boot message). |
| `other-fw/t002_bootloader.bin` | t002 bootloader — flash first if you want field-updatable firmware over the LINK port. |

All four already include the LCD character-map fix (left/right arrows instead of up/down) so you don't need to patch the source yourself. If you want to modify the firmware, the upstream project is **buttshock-et312-frankenbutt-f005** — the .bin files in this repo are pre-built from that source.

### Pick a programmer

| Programmer | Cost | Notes |
|------------|------|-------|
| **USBasp clone** — what the BOM lists ([B0885RKVMC](https://amazon.com/dp/B0885RKVMC), includes the 10→6-pin adapter the board needs); fallback alternative [HiLetgo B00AX4WQ00](https://amazon.com/dp/B00AX4WQ00) | $5–15 | Default cheap option. Quality varies — see gotchas below. |
| **DIAMEX USBasp** ([diamex.de](https://www.diamex.de/dxshop/USB-ISP-Programmer-PROG-USB-V4)) | ~$25 | German-made, current firmware, no driver dance. Worth it if you'll flash more than one board. |
| **Arduino UNO/Nano + ArduinoISP sketch** | $0 if you have one | Slower but works. Uses `-c avrisp` instead of `-c usbasp` — see Arduino-as-ISP section below. |

**USBasp clone gotchas.** Cheap clones often ship with: stale firmware (slow SPI — pass `-B 8` if you get sync errors); proprietary non-USBasp firmware (if avrdude can't see it but Windows enumerates it as "USBTiny" or similar, return it); or no 10→6-pin adapter (the MK-312BT board uses a 6-pin ISP header, not 10-pin — verify the listing includes the adapter or buy one separately).

### Install avrdude

#### macOS (Homebrew)

```sh
brew install avrdude
```

That's it. USBasp works out of the box, no driver setup.

#### Linux (Debian / Ubuntu / Mint)

```sh
sudo apt install avrdude
```

For non-root USB access add a udev rule (otherwise you'll need `sudo` on every flash):

```sh
sudo tee /etc/udev/rules.d/99-usbasp.rules <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="16c0", ATTR{idProduct}=="05dc", GROUP="plugdev", MODE="0666"
EOF
sudo udevadm control --reload-rules
sudo usermod -aG plugdev $USER   # log out and back in for this to take effect
```

#### Windows

1. Install avrdude. Pick one:
   - [WinAVR](https://sourceforge.net/projects/winavr/) — bundles avrdude + GCC, last release is dated but works fine for flashing
   - Standalone modern build from [mariusgreuel/avrdude](https://github.com/mariusgreuel/avrdude/releases)
   - GUI wrapper if you want one: [AVRDUDESS](https://github.com/ZakKemble/AVRDUDESS)
2. Plug the USBasp in. Windows will fail to install a driver — expected.
3. Install [Zadig](https://zadig.akeo.ie/), select **USBasp** in the device dropdown, set the driver target to **libusb-win32**, click **Replace Driver**.
4. avrdude can now talk to the USBasp.

### Flash with USBasp

Same commands on macOS, Linux, and Windows. Run them from the directory containing the .bin file (or use a full path).

**1. Test the connection** — the chip should reply with "AVR device initialized":

```sh
avrdude -c usbasp -p m16 -v
```

If it says "target doesn't answer," check ISP cable orientation (pin 1 to pin 1 — look at the silkscreen) and try slowing SCK with `-B 8`:

```sh
avrdude -c usbasp -B 8 -p m16 -v
```

**2. Set the fuses** for the external 8 MHz crystal — do this once per chip:

```sh
avrdude -c usbasp -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m
```

**3. Flash the firmware:**

```sh
avrdude -c usbasp -p m16 -U flash:w:f005-HelloFriend.bin
```

Power-cycle the box and you should see the boot screen.

### First-time walkthrough (USBasp on macOS — same idea on Linux/Windows)

If you've never flashed an AVR before, here's the full sequence for your own machine, with what to expect at each step. Examples are macOS; the Linux and Windows equivalents are noted inline.

**1. Verify avrdude is installed.**

```sh
avrdude -? | head -2
```

Should print `Usage: avrdude [options]` and a version line. If "command not found," go back and run `brew install avrdude` (macOS), `sudo apt install avrdude` (Linux), or install one of the Windows builds linked above.

**2. Plug in the USBasp** (USB cable to your Mac, ISP cable not yet connected to the board).

**3. Confirm the OS sees the USBasp** — this rules out a dead cable / dead clone before you try avrdude.

- **macOS**:
  ```sh
  system_profiler SPUSBDataType | grep -A 4 -i usbasp
  ```
  Expect something like `Product ID: 0x05dc`, `Vendor ID: 0x16c0`, `Manufacturer: www.fischl.de`. If you get nothing, the USBasp isn't being detected — try a different USB cable / port. If it's a USB-C-only Mac, you need a USB-A→C adapter; some cheap adapters don't pass enough current to power a USBasp.
- **Linux**: `lsusb | grep -i usbasp` → `Bus 001 Device 005: ID 16c0:05dc Van Ooijen Technische Informatica`
- **Windows**: Device Manager → look under **libusb-win32 devices** for "USBasp" (only appears after you've run Zadig per the Install step above).

**4. Confirm avrdude can talk to the USBasp** even before connecting it to the board. With nothing plugged into the ISP cable yet:

```sh
avrdude -c usbasp -p m16 -v
```

You'll see avrdude's banner, then either:
- `avrdude: error: program enable: target doesn't answer.` → **good**. avrdude reached the USBasp; the USBasp couldn't reach a chip because nothing's connected. Move to step 5.
- `avrdude: error: could not find USB device with vid=0x16c0 pid=0x5dc` → bad. avrdude can't see the USBasp. On macOS this almost always means avrdude is missing libusb — re-install: `brew reinstall avrdude`. On Linux, missing udev rule (see install section) or you forgot to log out/in after `usermod`. On Windows, Zadig wasn't run or you replaced the wrong driver.

**5. Connect the USBasp to the board.** The board's ISP header is **JP1**, a 6-pin connector near the ATmega. Use the 10→6-pin adapter that came with your USBasp.

Pin 1 is marked on both ends — usually a small triangle / dot on the silkscreen and a red stripe on the ribbon cable. **Match pin 1 to pin 1**. Backwards orientation won't damage anything but it won't work.

**6. Power the board** with its normal 18 V supply. The USBasp's VCC line is also live (5 V from USB), but the board's regulator dominates — no conflict in practice. (If your USBasp has a "VCC supply" jumper, you can set it OFF to be safe, but it's not required.)

**7. Test the connection to the chip:**

```sh
avrdude -c usbasp -p m16 -v
```

Now you should see `avrdude: AVR device initialized and ready to accept instructions` followed by the device signature `0x1e9403` (ATmega16) or `0x1e9489` (ATmega16A). If you get "target doesn't answer":
- Cable backwards (most common) — flip the 6-pin connector
- Board not powered
- Try `avrdude -c usbasp -B 8 -p m16 -v` to slow SCK (cheap clones often need this)

**8. Set the fuses** (one-time, per chip):

```sh
avrdude -c usbasp -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m
```

avrdude reads the current fuses, writes the new values, reads them back to verify. You'll see `lfuse verified` and `hfuse verified`.

**9. Flash the firmware** — `cd` into the firmware folder first so the relative path resolves:

```sh
cd /path/to/mk312-bt/3-build-and-flash/firmware/cr-custom-boot-messages
avrdude -c usbasp -p m16 -U flash:w:f005-HelloFriend.bin
```

You'll see writing/reading progress bars and `verified` at the end. The whole flash takes ~30 seconds on a USBasp.

**10. Disconnect, power-cycle, smile.** Pull the ISP cable, unplug the 18 V supply, plug it back in. The LCD should show "Hello Friend" briefly, then the main menu. If you get "Error 20," see the [Error 20 section](#error-20-match-the-mosfets-before-you-solder) above.

### Flash with Arduino-as-ISP

If you don't have a USBasp but do have an Arduino UNO/Nano lying around, it works as a programmer:

1. Open Arduino IDE → **File → Examples → 11. ArduinoISP → ArduinoISP** → upload to the Arduino.
2. Wire the Arduino to the MK-312BT ISP header: pin 10 → RESET, 11 → MOSI, 12 → MISO, 13 → SCK, plus 5 V and GND. Add a 10 µF cap between the Arduino's RESET and GND to stop the IDE auto-resetting it during flash operations.
3. Find the Arduino's serial port:
   - **macOS**: `ls /dev/cu.usb*` → e.g., `/dev/cu.usbmodem14101`
   - **Linux**: `ls /dev/ttyACM*` → e.g., `/dev/ttyACM0`
   - **Windows**: Device Manager → Ports → look for "Arduino", e.g., `COM7` (use `\\.\COM7` in avrdude commands)

Test, set fuses, flash — same three steps, just `-c avrisp -P <port> -b 19200` instead of `-c usbasp`:

```sh
# macOS / Linux
avrdude -c avrisp -P /dev/cu.usbmodem14101 -b 19200 -p m16 -t
avrdude -v -c avrisp -P /dev/cu.usbmodem14101 -b 19200 -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m
avrdude -v -c avrisp -P /dev/cu.usbmodem14101 -b 19200 -p m16 -U flash:w:f005-HelloFriend.bin
```

```cmd
:: Windows (substitute your COM port number)
avrdude -c avrisp -P \\.\COM7 -b 19200 -p m16 -t
avrdude -v -c avrisp -P \\.\COM7 -b 19200 -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m
avrdude -v -c avrisp -P \\.\COM7 -b 19200 -p m16 -U "flash:w:f005-HelloFriend.bin"
```

### Fuse byte reference

| Fuse | Value | Means |
|------|-------|-------|
| Low fuse  | `0xFF` | External crystal (8 MHz+), max startup time |
| High fuse | `0xDC` | JTAG disabled, EEPROM preserved across flash, BOD enabled at 4.3 V |

**Don't fat-finger these.** Wrong fuse bytes can lock out ISP — recovery requires an HV (parallel) programmer. Copy/paste the commands above; don't retype.

### Internal oscillator fallback (don't)

If you really don't want to install the external 8 MHz crystal, you have to set the calibration byte for the internal oscillator. Read the chip's calibration byte first (`avrdude -t` then `dump calibration` — the fourth byte is the 8 MHz calibration value, or use Atmel Studio to read the oscillator calibration byte). Then program that byte into address `0x3fff` in your firmware. Calibration bytes differ per chip even within the same batch. The firmware reads that byte at startup to set `OSCCAL`. If it's wrong, expect timing, interrupt, and serial-communication failures.

Just use an external crystal dammit.

## MK312-BT Original Fab Notes

(These are the old fab notes from the repo, mostly kept here for
history sake. Ordering instructions above cover most of this.)

### Main Boards

1. V Score the Main Boards panel as indicated.
2. Main Boards has 2 board designs panelized on 1 panel.
3. Thickness is standard 1.6mm (0.063inches)
4. Board is 2 layers
5. HASL Finish - Pb Free Preferred if possible, otherwise Pb HASL is OK
6. 1oz copper
7. FR4 material
8. Main Boards : Green solder mask, White Silkscreen (silkscreen BOTH top and bottom sides)
9. ITAR : NO
10. IPC-A-610 - Class2 (If possible - otherwise ignore)
11. Main Board Dimensions : (193.04mm x 104.14mm) or (7.600 inches x 4.100 inches) 

### Front Panel Boards

1. Place all Fab Markings (Serial Numbers/Date Codes) on the BOTTOM side of the front panel board. 
2. Thickness is standard 1.6mm (0.063inches)
3. Board is 2 layers
4. HASL Finish - Pb Free Preferred if possible, otherwise Pb HASL is OK
5. 1oz copper
6. FR4 material
7. Front Panel Boards : Black Solder Mask, While Silkscreen
8. ITAR : NO
9. IPC-A-610 - Class2 (If possible - otherwise ignore)
10. Front Panel Board Dimensions :  (196.85mm x 58.72mm) or (7.750inches x 2.312inches) 

## Bluetooth Serial Configuration

Refer to
[https://www.itead.cc/wiki/Serial_Port_Bluetooth_Module_(Master/Slave)_:_HC-05](https://www.itead.cc/wiki/Serial_Port_Bluetooth_Module_(Master/Slave)_:_HC-05)
for more information.

```
// Test command to check if we are communicating (expect to receive OK)
AT

//Name the module
AT+NAME=MK-312BT 

//Set baud rate to be same as the ATMEGA16
AT+UART=19200,0,0

//Set the pairing password
AT+PSWD=1234

//Set the LED Indicator polarity (1 = High Drive 0 = Low Drive)
AT+POLAR=1,1

// Reduce power consumption by increasing the scan interval. Without
// this it consumes ~43mA when not connected and causes the 5v regulator
// to get toasty (but still within operational temp range)
AT+IPSCAN=1024,1,1024,1 
```

To do this automatically:
1. Solder Pin32 of the HC05 module (see [HC05PINOUT.png](../4-wireless/bluetooth/HC05PINOUT.png) for reference)
2. Flash the included bin file onto the ATMEGA16
3. Plug the HC-05 bluetooth radio into the board (ensure pin 32 is
   soldered to the carrier board)
4. Place HC-05 in command mode by holding down the button on the HC-05
   module, power up MK-312BT and release button after 2 seconds. LEDs
   on HC-05 will blink slowly (0.5 Hz) to indicate command mode.
5. Watch GUI until it says the HC-05 configuration is finished and
   flash normal firmware back on to the ATMEGA16
6. If program stops on "Communicating with HC-05" make sure OSCCAL
   value for 8 MHz R/C position is copied to &H3FFF of bin location or
   use external 8 MHz crystal with appropriate fuse bits set (FFS use
   the external crystal)

## 3D Printable Case

STL files for a 3D printable case are in [`../3-build-and-flash/case/`](../3-build-and-flash/case/). For hardware, this case requires:

- 4 M2.5x20 screws
- up to 3 M2.5x5 screws
- some dampening for the battery (double sided foam tape may work)
