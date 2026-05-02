# Step 1 — Order boards

You need **two** boards to build a complete unit:

| Board | File | Notes |
|-------|------|-------|
| Main board (v1.4) | [`gerbers/v1.4-main-board.zip`](gerbers/v1.4-main-board.zip) | Latest revision. See [v1.4 release notes](v1.4-release-notes.txt) for changes vs v1.3 |
| Front panel (v1.2) | [`gerbers/v1.2-front-panel.zip`](gerbers/v1.2-front-panel.zip) | Front panel design unchanged — v1.2 is current |

Order them as **two separate items in one cart** — the per-board settings differ.

## Recommended fab

[JLCPCB](https://jlcpcb.com) — they detect 2-layer and dimensions automatically when you upload the zip.

## Per-board fab settings

| Setting | Main board | Front panel |
|---------|-----------|-------------|
| Layers | 2 | 2 |
| Thickness | 1.6 mm | 1.6 mm |
| Surface finish | HASL (Pb-free preferred) | HASL (Pb-free preferred) |
| Copper weight | 1 oz | 1 oz |
| Material | FR4 | FR4 |
| Solder mask | Any color | **Black** recommended (matches case) |
| Silkscreen | White | White |
| Different Design | 2 | 1 |
| Special instructions | V-score the panel as indicated | Place fab markings on **bottom** side |

"Different Design" differs because the main board panel holds 2 panelized designs; the front panel is a single design.

## Schematics & layout

For visual reference (don't send these to the fab):

- [`schematics/v1.4 Board Layout.png`](schematics/v1.4%20Board%20Layout.png)
- [`schematics/v1.4 Part Placement.png`](schematics/v1.4%20Part%20Placement.png)
- [`schematics/pages/`](schematics/pages/) — schematic pages 1-5

## Need the source files?

v1.4 ships gerbers only. To modify the design, grab the v1.3 Eagle source from [`../historical/eagle-source/`](../historical/eagle-source/).

→ Next: [Step 2 — Order parts](../2-order-parts/)
