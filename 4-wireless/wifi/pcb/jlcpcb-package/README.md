# JLCPCB-ready package — MK312 WiFi adapter

A drop-in upload bundle for ordering the [MK312WIFI adapter PCB](../) from JLCPCB with **SMT-only assembly**: JLC pre-mounts the one SMD part (U1, the 3.3V regulator); you hand-solder the 6 through-hole parts.

This is the **cheapest path** for this board (~$20-25 for 5 boards). See the [cost comparison in `4-wireless/README.md`](../../../README.md) — full PCBA-with-THT runs $65-100+ because of THT setup fees, and DIY-everything is $12-17 (you'd hand-solder one extra SOT-223).

## Files in this package

| File | What it is | Upload to JLC |
|------|------------|---------------|
| [`gerbers.zip`](gerbers.zip) | Standard KiCad gerbers (9 files) — copper, masks, silkscreen, edge cuts, drill | ✅ Yes |
| [`bom.csv`](bom.csv) | BOM: just U1 (AMS1117-3.3, LCSC `C6186`) — the only part JLC assembles | ✅ Yes (in PCBA tab) |
| [`cpl.csv`](cpl.csv) | Pick-and-place: position and rotation for U1 | ✅ Yes (in PCBA tab) |
| [`cpl-all-parts.csv`](cpl-all-parts.csv) | Full pick-and-place (all 7 parts) — reference only, not uploaded | ❌ No |

## Step-by-step at JLCPCB

1. Go to https://jlcpcb.com → **Order Now**
2. Upload `gerbers.zip`
3. PCB settings — defaults are fine. Confirm:
   - **Layers: 2**
   - **Dimensions: 30 × 17 mm** (auto-detected)
   - **Quantity: 5** (minimum) or however many you want
   - **PCB Color: any** (green default is cheapest)
   - **Surface Finish: HASL (with lead)** — cheapest, fine for hand-soldering. Lead-free HASL or ENIG also work
4. Scroll down → enable **PCB Assembly**
   - **Assembly Side: Top side** (U1 is on top)
   - **Tooling holes: Added by JLCPCB** (free, optional)
   - **PCBA Qty: 5** (or however many you want assembled)
5. Click **Confirm** → upload `bom.csv` for the BOM and `cpl.csv` for the CPL
6. JLC shows a parts review screen. Confirm:
   - **U1 / AMS1117-3.3 / C6186** — should be flagged as **Basic** part (no extended-part fee). Rock-solid — JLC has stocked this for years
7. Confirm placement preview — U1 should sit roughly at the middle-left of the board
8. Save to cart → checkout

## What you'll receive

5 boards (or however many) with **only U1 (the SOT-223 regulator) pre-soldered on the top side**. The 6 holes for the THT parts stay empty — that's expected.

## Then hand-solder these 6 THT parts

Buy from Mouser/Digikey/Amazon/AliExpress — these are commodity parts:

| Ref | Part | Qty per board | Sourcing notes |
|-----|------|----------------|----------------|
| C1, C2 | 100 nF (0.1 µF) ceramic disc capacitor, 50V, 2.54mm pitch | 2 | Any generic 100nF disc cap |
| Q1 | PN2222A NPN transistor, TO-92 | 1 | PN2222A or 2N2222A interchangeable |
| SW1 | 6mm tactile pushbutton switch, 4-pin THT | 1 | Standard "Omron-style" tactile switch |
| J1 | 1×6 male pin header, **right-angle**, 2.54mm pitch | 1 | Plugs into the MK-312BT mainboard's HC-05 socket — **angled is critical** |
| J2 | 2×4 female socket header, 2.54mm pitch | 1 | The ESP-01S plugs into this — make sure it's **female** (socket), not male |

You also need the **ESP-01S module itself** (~$2 on AliExpress / Amazon). It plugs into J2 after assembly.

## Soldering order (suggested)

1. C1, C2 (lowest profile first — easier with the board flat)
2. Q1 (TO-92, watch flat-side orientation per silkscreen)
3. SW1 (tactile button)
4. J2 (2×4 socket — solder pins straight; the ESP-01S plugs in later)
5. J1 (1×6 right-angle header — pins point outward from the board edge to plug into the MK-312BT)
6. Plug in the ESP-01S module — done

Total hand-soldering: ~5-10 minutes per board.

## Verifying assembly

Before plugging into the MK-312BT:

1. Visually check J1 orientation — pin 1 should match the MK-312BT's HC-05 socket pin 1 (see the [MK312WIFI README](../../README.md) for the pinout table)
2. Multimeter continuity check from J1's VCC pin → U1 input → U1 output → ESP socket VCC pin (J2)
3. Power check: apply 5V to J1's VCC/GND, measure 3.3V at J2's VCC pin — must read 3.3V before plugging the ESP in
4. If 3.3V is good, plug in the ESP-01S, install in the MK-312BT, power on. The LCD should show `WifiAP` on first boot

## Caveats / things to verify before clicking "submit"

- **LCSC Part C6186 stock**: rock-solid Basic part historically, but verify on JLC's PCBA Parts Library at order time
- **Rotation of U1**: the CPL specifies 0° rotation. KiCad's `Regulator_Linear:AMS1117-3.3` footprint puts pin 1 at upper-left at 0° — JLC's expected orientation for SOT-223 also puts pin 1 upper-left at 0°. They should match. If JLC's preview shows U1 visibly rotated wrong, edit the rotation in their web UI before confirming
- **Footprint check**: the upstream MK312WIFI project author generated these gerbers for v1.2 of their design. Builders have used them successfully — this is not a fresh untested PCB
- **THT parts library at JLC**: irrelevant for the SMT-only path (you're not asking JLC to source them). But if you ever switch to full PCBA-with-THT, expect some of the 6 THT parts to need substitutes from JLC's smaller THT inventory

## Regenerating from source

The KiCad source is at [`../kicad-source/`](../kicad-source/) (sibling of this package). With KiCad 6+ installed:

```bash
cd ../kicad-source
kicad-cli pcb export gerbers MK312-Wifi.kicad_pcb --output ../jlc-fresh-gerbers/
kicad-cli pcb export pos MK312-Wifi.kicad_pcb --format csv --units mm \
  --use-drill-file-origin --output cpl-fresh.csv
```

This package was hand-built from the upstream `fab-files.zip` (originally `MK312WIFI_PCB_v1.2_Fabrication_Files.zip`) plus manual parsing of the `.kicad_pcb` source for placements.

