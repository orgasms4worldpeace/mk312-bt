# Firmware

Pre-built `.bin` files ready to flash to the ATmega16A on the main board.

| File | What it is |
|------|-----------|
| `cr-custom-boot-messages/f005-HelloFriend.bin` | Patched frankenbutt-f005 with "Hello Friend" boot screen — **recommended default** |
| `cr-custom-boot-messages/f005-ElectrodesReady.bin` | Same firmware, "Electrodes Ready" boot screen |
| `other-fw/f005.bin` | Unpatched frankenbutt-f005 (no custom boot message) |
| `other-fw/t002_bootloader.bin` | t002 bootloader — flash first if you want field-updatable firmware over the LINK port |
| `backup_eeprom.bin`, `backup_flash.bin` | Reference dumps from a working unit (read with `avrdude -U eeprom:r:... -U flash:r:...`) |

All four user firmwares already include the LCD character-map fix (left/right arrows instead of up/down) so you don't need to patch the source yourself.

## How to flash

See **[`docs/build-guide.md` → Firmware: flashing the AVR](../../docs/build-guide.md#firmware-flashing-the-avr)** for the full Win/Mac/Linux walkthrough — programmer choice, avrdude install per platform, fuse settings, and the exact commands for both USBasp and Arduino-as-ISP.

Quick reference (USBasp, all platforms):

```sh
# Set fuses (do this once per chip)
avrdude -c usbasp -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m

# Flash firmware
avrdude -c usbasp -p m16 -U flash:w:cr-custom-boot-messages/f005-HelloFriend.bin
```

## Source

The firmware is a patched version of **buttshock-et312-frankenbutt-f005**. The patches in this repo handle the LCD character-map differences from the original ET-312. To rebuild from source, see the upstream buttshock project.
