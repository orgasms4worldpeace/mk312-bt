# Firmware

Pre-built `.bin` files ready to flash to the ATmega16A on the main board.

| File | What it is |
|------|-----------|
| `cr-custom-boot-messages/f005-HelloFriend.bin` | **Default application firmware.** Patched frankenbutt-f005 with "Hello Friend" boot screen. Flash this and the box runs. |
| `cr-custom-boot-messages/f005-ElectrodesReady.bin` | Alternative: same f005 build, "Electrodes Ready" boot screen |
| `other-fw/f005.bin` | Alternative: unpatched frankenbutt-f005, no custom boot message |
| `backup_eeprom.bin`, `backup_flash.bin` | Reference dumps from a working unit (read with `avrdude -U eeprom:r:... -U flash:r:...`). Source for the disassembly-based [`../troubleshooting/debug-notes/`](../troubleshooting/debug-notes/) analyses. |

All bundled `.bin` files include the LCD character-map fix (left/right arrows instead of up/down) and work with the MK-312BT's stock display.

## How to flash

See **[`build-guide.md` → Firmware: flashing the AVR](../../build-guide.md#firmware-flashing-the-avr)** for the full Win/Mac/Linux walkthrough — programmer choice, avrdude install per platform, fuse settings, and exact commands for both USBasp and Arduino-as-ISP.

Quick reference (USBasp, all platforms):

```sh
# Set fuses (do this once per chip)
avrdude -c usbasp -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m

# Flash firmware
avrdude -c usbasp -p m16 -U flash:w:cr-custom-boot-messages/f005-HelloFriend.bin
```

## Source

The firmware is a patched version of **buttshock-et312-frankenbutt-f005**. The patches handle the LCD character-map differences. To rebuild from source, see the upstream buttshock project.
