# Firmware

Pre-built `.bin` files ready to flash to the ATmega16A on the main board.

| File | What it is |
|------|-----------|
| `cr-custom-boot-messages/f005-HelloFriend.bin` | **Default application firmware.** Patched frankenbutt-f005 with "Hello Friend" boot screen. Flash this and the box runs. |
| `cr-custom-boot-messages/f005-ElectrodesReady.bin` | Alternative application: same f005 build, "Electrodes Ready" boot screen |
| `other-fw/f005.bin` | Alternative application: unpatched frankenbutt-f005, no custom boot message |
| `other-fw/t002_bootloader.bin` | **Optional ET-312 bootloader.** Flash *first* if you want to update firmware over the LINK port later without dragging the USBasp out again. Then flash an f005 application on top. By itself the bootloader doesn't run the box. |
| `other-fw/unpatched_312-16.upg` | **Source input for the patcher** — not flashable directly. Encrypted ET-312 v1.6 firmware blob. Feed into buttshock fw-utils when rebuilding from source. |
| `backup_eeprom.bin`, `backup_flash.bin` | Reference dumps from a working unit (read with `avrdude -U eeprom:r:... -U flash:r:...`) |

All bundled `.bin` files work with the MK-312BT's LCD out of the box.

## How to flash

See **[`docs/build-guide.md` → Firmware: flashing the AVR](../../docs/build-guide.md#firmware-flashing-the-avr)** for the full Win/Mac/Linux walkthrough — programmer choice, avrdude install per platform, fuse settings, and exact commands for both USBasp and Arduino-as-ISP.

Quick reference (USBasp, all platforms):

```sh
# Set fuses (do this once per chip)
avrdude -c usbasp -p m16 -U lfuse:w:0xFF:m -U hfuse:w:0xDC:m

# Flash firmware
avrdude -c usbasp -p m16 -U flash:w:cr-custom-boot-messages/f005-HelloFriend.bin
```

## Source

The firmware is a patched version of **buttshock-et312-frankenbutt-f005**. The patches handle the LCD character-map differences from the original ET-312. To rebuild from source, see the upstream buttshock project.
