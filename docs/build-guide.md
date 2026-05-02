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
| `cr-custom-boot-messages/f005-HelloFriend.bin` | **Recommended default — application firmware.** Patched frankenbutt-f005 with a "Hello Friend" boot screen. Flash this and the box runs. |
| `cr-custom-boot-messages/f005-ElectrodesReady.bin` | Alternative application: same f005 build, "Electrodes Ready" boot screen. |
| `other-fw/f005.bin` | Alternative application: unpatched frankenbutt-f005, no custom boot message. |
| `other-fw/t002_bootloader.bin` | **Optional ET-312 bootloader.** Flash this *first* if you want to update the firmware over the LINK port later without dragging the USBasp out again. Then flash one of the f005 application firmwares on top. By itself the bootloader doesn't run the box — you still need the application. |
| `other-fw/unpatched_312-16.upg` | **Source input for the patcher** — not flashable directly. Encrypted ET-312 v1.6 firmware blob from ErosTek. Feed into buttshock fw-utils when rebuilding from source. See [Build from source](#build-from-source-advanced) below. |

All bundled `.bin` files include the LCD character-map fix (left/right arrows instead of up/down). If you just want a working box, flash `f005-HelloFriend.bin` and skip ahead. If you want field-updatable firmware, flash `t002_bootloader.bin` first and then `f005-HelloFriend.bin`.

### Pick a programmer

Ranked from "just buy this" to "if you have one already":

| Programmer | Cost | Why pick it |
|------------|------|-------------|
| **[Adafruit USBtinyISP v2.0](https://www.adafruit.com/product/46)** | ~$22 | Drop-in for the USBasp use case (use `-c usbtiny` instead of `-c usbasp`). Adafruit-quality build, current firmware, includes 6-pin and 10-pin ribbon cables, status LEDs work out of the box. **Best balance of reliability and price.** |
| **[DIAMEX USB-ISP-Programmer V4](https://www.diamex.de/dxshop/USB-ISP-Programmer-PROG-USB-V4)** | ~$25 | German-made, current USBasp firmware, no driver dance. Best choice if you'll flash more than one board. Use `-c usbasp`. |
| **[Pololu USB AVR Programmer v2.1](https://www.pololu.com/product/3172)** | ~$22 | Speaks STK500v2 (use `-c stk500v2`), exceptionally reliable, includes 6-pin cable and integrated USB-to-serial adapter — bonus, you can use it for the LINK port too. |
| **DIYmall USBasp** ([Amazon B08F9FZKP9](https://www.amazon.com/dp/B08F9FZKP9)) | ~$10 | Cheapest option that explicitly ships with the **jumper cap installed** (lights the activity LEDs) and the **10→6-pin adapter included**. The defaults that the BOM pick (B0885RKVMC) is missing. |
| **HiLetgo USBasp** ([Amazon B00AX4WQ00](https://www.amazon.com/HiLetgo-ATMEGA8-Programmer-USBasp-Cable/dp/B00AX4WQ00)) | ~$8 | Most popular cheap clone. Has power + write LEDs; verify the listing includes the 6-pin adapter (varies by seller revision). |
| **Arduino UNO/Nano + ArduinoISP sketch** | $0 if you have one | Slower but uses what you already own. Uses `-c avrisp` — see [Arduino-as-ISP](#flash-with-arduino-as-isp) below. |
| **[Atmel-ICE](https://www.microchip.com/en-us/development-tool/ATATMEL-ICE)** | $80–100 | Microchip's official tool. Overkill unless you're doing real AVR work. Use `-c atmelice_isp`. |

> ⚠️ **The current BOM pick — KeeYees [B0885RKVMC](https://amazon.com/dp/B0885RKVMC) — works but has a real problem:** it ships **without the J1 jumper installed**, so the status LEDs stay dark and you can't tell if the USBasp is actually doing anything. The fix is either to drop a 0.1" jumper cap on J1 yourself ($0.50 in any electronics drawer) or to pick one of the better options above. For a single build the KeeYees is fine if you don't mind blind-flashing; for a kit you'll use again, the Adafruit USBtinyISP is the real recommendation.

**Cheap-clone gotchas in general:**
- **Stale firmware** → slow SPI. Add `-B 8` to the avrdude command if you get sync errors. Higher = slower.
- **Proprietary non-USBasp firmware** → some ship with AT89-style firmware that avrdude can't talk to. If your OS sees "USBTiny" or similar instead of "USBasp," return it.
- **Missing 10→6-pin adapter** → the MK-312BT's ISP header (JP1) is 6-pin, not the 10-pin standard the USBasp output uses. Verify the listing includes the adapter or buy one separately for ~$2.
- **Missing or absent jumpers** → JP1/J1 controls LED activity on most clones; without it, no visible feedback. Dropping a jumper cap on yourself is fine if you're comfortable with that.

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

### The three things you actually need to do

Everything else above is supporting detail. The actual flashing is three commands. If you understand what each flag means, you can adapt them to any programmer / chip / firmware file.

#### Step 1 — Identify your programmer's avrdude name

avrdude doesn't auto-detect what's plugged in; you have to tell it via the `-c` flag. Here's what to use:

| Hardware you have | `-c` flag value |
|-------------------|-----------------|
| USBasp clone (the BOM pick, the HiLetgo, the DIAMEX, basically anything labeled "USBasp") | `usbasp` |
| Arduino UNO/Nano running the ArduinoISP sketch | `avrisp` (and you'll also need `-P <port> -b 19200`) |
| Atmel/Microchip Atmel-ICE | `atmelice_isp` |
| Atmel AVRISP mkII | `avrispmkII` |

Don't know what you've got? List every supported programmer:

```sh
avrdude -c help 2>&1 | head -40
```

For this guide we'll use `-c usbasp` since that's what the BOM lists.

#### Step 2 — Set the fuses

Fuses are tiny configuration bits stored in the chip that control hardware behavior — most importantly, where the chip gets its clock from. The MK-312BT board has an external 8 MHz crystal soldered on, but the ATmega16 ships configured for its slow internal RC oscillator. You have to switch it once per chip.

```sh
avrdude -c usbasp -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m
```

What each flag means:

| Flag | Meaning |
|------|---------|
| `avrdude` | The flasher program itself |
| `-c usbasp` | Use the USBasp programmer (from Step 1) |
| `-p m16` | Target chip is an ATmega16. (`m16a` works too — the A is silicon revision, same fuse map) |
| `-U lfuse:w:0xFF:m` | **U**pload to memory area `lfuse` (low fuse byte), action `w` (write), value `0xFF`, format `m` (immediate, the value is right there in the command) |
| `-U hfuse:w:0xDC:m` | Same idea for the high fuse byte: write `0xDC` |

**Why `0xFF` and `0xDC`?** Those values configure: external 8+ MHz crystal, JTAG disabled, EEPROM preserved across flashes, brownout detector at 4.3 V. Full bit-by-bit breakdown in the [Fuse byte reference](#fuse-byte-reference) below.

> ⚠️ **Don't fat-finger the fuse values.** Wrong fuses can lock the chip out of ISP — recovering it requires a high-voltage parallel programmer. Copy/paste the command above; don't retype.

avrdude will read the current fuses, write the new values, and read them back to verify. Look for `lfuse verified` and `hfuse verified`.

#### Step 3 — Flash the firmware

```sh
avrdude -c usbasp -p m16 -U flash:w:f005-HelloFriend.bin
```

Same flags as before, with one new `-U` operation:

| Flag | Meaning |
|------|---------|
| `-U flash:w:f005-HelloFriend.bin` | Memory area `flash` (program code), action `w` (write), source = the file `f005-HelloFriend.bin`. avrdude auto-detects the file format from the extension (`.bin` = raw binary, `.hex` = Intel HEX). |

avrdude erases flash, writes the new firmware, then reads it back byte-for-byte to verify. Takes ~30 seconds on a USBasp. You'll see `verified` at the end if all good.

Power-cycle the box and you should see the boot screen.

#### Useful extra flags

| Flag | When to add it |
|------|----------------|
| `-v` | Verbose. Shows what avrdude is doing — add it any time something's not working. |
| `-B 8` | Slow down the SCK (clock) line. Cheap USBasp clones often need this if you get "target doesn't answer." Higher number = slower. Try `-B 32` if `-B 8` doesn't help. |
| `-n` | Dry run / no-write. Reads but doesn't write. Useful for testing the connection before committing to a fuse change. |
| `-e` | Erase chip first (avrdude does this automatically before `flash:w:`, so you rarely need it explicitly). |
| `-P <port>` | Specify the serial port. Only needed for serial-based programmers like Arduino-as-ISP — USBasp uses libusb and doesn't need a port. |
| `-b <baud>` | Baud rate. Same: only for serial-based programmers (Arduino-as-ISP needs `-b 19200`). |

#### Test the connection before flashing

Optional but useful — run avrdude in just-look-at-the-chip mode to confirm the wiring is right before you commit:

```sh
avrdude -c usbasp -p m16 -v
```

Expect `AVR device initialized and ready to accept instructions` followed by the device signature `0x1e9403` (ATmega16) or `0x1e9489` (ATmega16A). If you get "target doesn't answer," check ISP cable pin 1 orientation, that the board is powered, and try `-B 8` to slow SCK.

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

### Build from source (advanced)

The `.bin` files in this repo are pre-built. To rebuild from scratch:

1. **Get the toolchain.** macOS: `brew install avr-gcc`. Linux: `sudo apt install gcc-avr binutils-avr avr-libc`. Windows: install [WinAVR](https://sourceforge.net/projects/winavr/) (it bundles avr-gcc).
2. **Get the source.** The project is **buttshock-et312-frankenbutt-f005**. Clone it from GitHub if it's still there, or grab a copy from the e-stim community Discord (`#312-chat`).
3. **Get the original ET-312 firmware blob.** ErosTek ships their firmware encrypted/scrambled. The `buttshock-et312-firmware` toolchain has a script that downloads and unscrambles it:
   ```sh
   git clone https://github.com/buttshock/buttshock-et312-firmware
   cd buttshock-et312-firmware
   scripts/fw-utils.py --downloadfw
   ```
   Per [cLx's notes](http://clx.freeshell.org/mk312bt.html), this download path may not work anymore — if it fails, the unscrambled blob is also floating around the same Discord / Telegram channels.
4. **Build the patched version:**
   ```sh
   cd ../buttshock-et312-frankenbutt/m005
   make
   ```
   This produces `m005.bin` ready for `avrdude -U flash:w:m005.bin`.
5. The MK-312BT-specific patches (left/right arrows for the LCD character map) are already applied in the bundled `f005-*.bin` files in this repo. If you build from clean upstream you'll need to re-apply those, or you'll see garbled arrows on screen.

### Internal oscillator? Don't.

There's a workaround involving the chip's calibration byte and `OSCCAL` if you skip the external 8 MHz crystal. It's fragile per-chip, and gets you timing/interrupt/serial failures whenever it's slightly off. Forget this crap. Use the external crystal, period.

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

## Bluetooth (HC-05) configuration

The HC-05 module ships with default settings (name "HC-05", PIN 1234, baud 9600) — it needs to be reconfigured before it'll talk to the MK-312BT. Skip this entire section if you're using the WiFi adapter instead — see [`4-wireless/wifi/`](../4-wireless/wifi/).

> **macOS users:** HC-05 / Bluetooth Classic SPP is unreliable on macOS Monterey+ (Apple deprecated SPP support). Pairing works but data drops out. Use the [WiFi adapter](../4-wireless/wifi/) instead.

### Two ways to configure it

| Method | Effort | When to pick |
|--------|--------|--------------|
| **Manual via USB-TTL serial adapter** ⭐ | Plug HC-05 into laptop, send AT commands. ~5 minutes. | Recommended. You already need a USB-TTL adapter for the LINK port anyway (BOM lists `amazon.com/dp/B07D6LLX19`). |
| **Auto-config via one-shot AVR firmware** | Flash a special firmware that AT-configures the HC-05 in-place from the AVR side, then flash the real firmware back. | Only useful if you're building several boards or have no USB-TTL adapter. Firmware: [`4-wireless/bluetooth/MK-312BT V1.2 HC-05 Initialization ATMEGA16.bin`](../4-wireless/bluetooth/) (BASIC source `.bas` also included). |

### Manual config (recommended path)

**👉 See [`4-wireless/bluetooth/hc05-setup.md`](../4-wireless/bluetooth/hc05-setup.md) for the complete walkthrough** — it covers the three quirks that quietly break first-time setups (no local echo, CR+LF requirement, fixed 38400 baud in command mode), per-platform terminal setup (picocom on macOS/Linux, Arduino IDE Serial Monitor or Termite on Windows), the IPSCAN power-vs-responsiveness tradeoff with a comparison table, and the macOS "Disconnected" cosmetic quirk.

Quick summary of what you'll do:

1. **Wire** USB-TTL adapter to HC-05: VCC↔VCC, GND↔GND, **TX↔RXD**, **RX↔TXD** (the cross is the most common mistake — each board labels pins from its own perspective). If your HC-05 breakout has no button, also wire 3.3 V to the HC-05's `EN` pin.
2. **Enter AT mode**: hold the button on the HC-05 breakout (or pull `EN` high) while connecting power. LED should blink slowly (~once every 2 s). Fast blink = data mode, retry.
3. **Find the serial device**: `ls /dev/cu.usbserial-*` (macOS), `ls /dev/ttyUSB*` (Linux), Device Manager (Windows).
4. **Open a terminal at 38400 baud with CR+LF and local echo enabled** (AT mode is hardcoded to 38400 regardless of what you set with `AT+UART`):
   ```sh
   picocom -b 38400 --omap crcrlf --echo /dev/cu.usbserial-XXXXXXXX
   ```
5. **Test**: type `AT` + Enter → expect `OK`. If nothing comes back, see the troubleshooting in `hc05-setup.md`.
6. **Configure** (each command should reply `OK`):
   ```
   AT+NAME=MK-312BT
   AT+UART=19200,0,0
   AT+PSWD=1234
   AT+POLAR=1,1
   AT+IPSCAN=1024,1,1024,512
   ```
7. **Verify** by reading values back: `AT+NAME?`, `AT+UART?`, `AT+PSWD?`, `AT+IPSCAN?`.
8. **Solder pin 32** of the HC-05 inner module to the breakout board (it's the STATE pin — drives the front-panel "Radio" LED). See [`HC05PINOUT.png`](../4-wireless/bluetooth/HC05PINOUT.png).
9. **Plug into the MK-312BT** at the J9 "Radio Header" socket. Pair from your host with PIN `1234`.

#### A note on IPSCAN

The community-default `AT+IPSCAN=1024,1,1024,1` makes the HC-05 nearly invisible (~5 mA idle) but slow to reconnect (~30 s after every power-on). The more practical `1024,1,1024,512` gives ~15–20 mA idle and <2 s reconnect by keeping page-scan at full duty cycle while killing the inquiry-scan that dominates idle current. Use `1024,512,1024,512` (HC-05 default) only if you've replaced the 7805 with a switching regulator (see cLx's page for the mEZD71201A-G drop-in mod, currently silicon for ~$15).

`hc05-setup.md` has the full table comparing all three settings against the stock 7805 thermal limits.

### Auto-config alternative

If you'd rather not buy a USB-TTL adapter, the repo includes a one-shot AVR firmware that configures the HC-05 in-place:

1. Solder pin 32 of the HC-05 inner module first (it's required for the auto-config to know the HC-05 is present).
2. Flash [`4-wireless/bluetooth/MK-312BT V1.2 HC-05 Initialization ATMEGA16.bin`](../4-wireless/bluetooth/) onto the ATmega16 using the same avrdude commands from the [Firmware section](#firmware-flashing-the-avr) above.
3. Plug the HC-05 into the board's J9 socket.
4. Hold the button on the HC-05 breakout, power up the MK-312BT, release after 2 seconds. HC-05's LED should blink slowly (~0.5 Hz) — that's command mode.
5. Watch the LCD: it'll display progress and finally "HC-05 OK" (or similar).
6. Power off, flash the real firmware (`t002_bootloader.bin`, or one of the alternatives) back onto the AVR.
7. If it stops on "Communicating with HC-05," your fuses are wrong — make sure the external 8 MHz crystal fuses are set per the [Firmware section](#firmware-flashing-the-avr). Don't try to make this work with the internal RC oscillator.

### Pairing

After config, pair from your host with PIN `1234`:

| Platform | How |
|----------|-----|
| **macOS** | System Settings → Bluetooth → "MK-312BT" → 1234. After ~30 s the panel will show "Disconnected" — this is cosmetic; the bond is permanent. Verify with `ls /dev/cu.MK-312BT*`. **SPP support is poor on Monterey+; consider the WiFi adapter.** |
| **Linux** | `bluetoothctl` → `pair XX:XX:XX:XX:XX:XX` → 1234. To get a serial port: `sudo rfcomm bind 0 XX:XX:XX:XX:XX:XX` → use `/dev/rfcomm0`. |
| **Windows** | Settings → Devices → Bluetooth → "MK-312BT" → 1234. A virtual COM port appears in Device Manager. |
| **Android** | Settings → Bluetooth → "MK-312BT" → 1234. App connects to the bonded device. |
| **iOS** | Doesn't speak Bluetooth Classic SPP at all. Use the WiFi adapter. |

Then point your control client (e.g., [`mk312-gui`](https://github.com/clxjaguar/mk312-gui)) at the assigned serial port at 19200 baud.

## 3D Printable Case

STL files for a 3D printable case are in [`../3-build-and-flash/case/`](../3-build-and-flash/case/). For hardware, this case requires:

- 4 M2.5x20 screws
- up to 3 M2.5x5 screws
- some dampening for the battery (double sided foam tape may work)
