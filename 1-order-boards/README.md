# Step 1 — Order boards

You need **two** PCBs to build a working unit, and there's a third optional one most builders should order at the same time:

| Board | File | Required? | Notes |
|---|---|---|---|
| Main board (v1.4) | [`gerbers/v1.4-main-board.zip`](gerbers/v1.4-main-board.zip) | **Yes** | Latest revision. See [v1.4 release notes](v1.4-release-notes.txt) for changes vs v1.3 |
| Front panel (v1.2) | [`gerbers/v1.2-front-panel.zip`](gerbers/v1.2-front-panel.zip) | **Yes** | Front panel design unchanged — v1.2 is current |
| WiFi adapter (optional) | [`../4-wireless/wifi/pcb/jlcpcb-package/gerbers.zip`](../4-wireless/wifi/pcb/jlcpcb-package/gerbers.zip) | Optional but recommended | If you're already paying JLCPCB shipping for the main board + front panel, the marginal cost to add this is ~$5–10. See [combining orders](#combine-with-the-wifi-adapter-while-you-pay-shipping) below. |

Order each as a **separate item in one JLCPCB cart** — the per-board settings differ, but they ship together.

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

## Combine with the WiFi adapter while you pay shipping

The MK-312-BT supports two wireless options — the original HC-05 Bluetooth module (no PCB needed) and a small WiFi adapter daughter-board that's pin-compatible with the HC-05 socket. The adapter board is its own JLCPCB order with **SMT assembly** (one part, the AMS1117-3.3 regulator), and you hand-solder six through-hole parts after.

If you're already submitting an order for the main board + front panel, the WiFi adapter can ride along in the same cart. JLCPCB lets you submit multiple PCB jobs in one order and ship them together — you only pay shipping once.

| Board | Order type | Setup |
|---|---|---|
| Main board (v1.4) | PCB only | Settings table above |
| Front panel (v1.2) | PCB only | Settings table above |
| WiFi adapter | **PCB + SMT assembly** (one part) | Full step-by-step at [`../4-wireless/wifi/pcb/jlcpcb-package/README.md`](../4-wireless/wifi/pcb/jlcpcb-package/README.md) |

Cost reality check (5-board minimum at JLCPCB, mid-2026 pricing):
- Main board × 5: ~$8–15 PCBs + ~$10–25 shipping
- Front panel × 5: ~$8–15
- WiFi adapter × 5 with SMT: ~$20–25 (PCBs + AMS1117-3.3 assembly)
- **Combined order ships once** — adding the WiFi adapter to a same-day order saves a second shipping charge

You don't have to commit to building WiFi units to order the boards — having spares means you can decide per unit whether to use the HC-05 (cheaper, simpler) or the WiFi adapter (better macOS / iOS support — see [`../4-wireless/README.md`](../4-wireless/README.md)).

## Schematics & layout

For visual reference (don't send these to the fab):

- [`schematics/v1.4 Board Layout.png`](schematics/v1.4%20Board%20Layout.png)
- [`schematics/v1.4 Part Placement.png`](schematics/v1.4%20Part%20Placement.png)
- [`schematics/pages/`](schematics/pages/) — schematic pages 1-5

## Need the source files?

v1.4 ships gerbers only — no Eagle source was ever released for v1.4. To modify the design you'd need to either reverse the gerbers in KiCad/Eagle, or work from the older v1.3 Eagle source preserved upstream at [`CrashOverride85/mk312-bt`](https://github.com/CrashOverride85/mk312-bt) (note: v1.3 has known issues that v1.4 fixes — porting changes is non-trivial).

→ Next: [Step 2 — Order parts](../2-order-parts/)
