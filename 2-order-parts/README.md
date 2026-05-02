# Step 2 — Order parts

Two BOM files, same parts, different jobs:

| File | Use it for |
|------|-----------|
| [`BOM_Mouser.csv`](BOM_Mouser.csv) | **Direct import into Mouser's BOM Tool** — strict 4-column format (`Mouser Part Number`, `Quantity`, `Manufacturer Part Number`, `Customer Part Number`). Headers in row 1, no title row, no extra columns — Mouser's importer needs it exactly this way or it silently drops columns. |
| [`BOM_full.csv`](BOM_full.csv) | Human-readable master with designators, descriptions, and both **Mouser** and **Amazon** search links per part. First row is a `Last modified:` date stamp. |

## How to use

1. Sign in to [mouser.com](https://www.mouser.com/) and open the **BOM Tool**.
2. Upload `BOM_Mouser.csv`.
3. Review and add to cart. If Mouser is out of stock on a part, check `BOM_full.csv` for the part number and search alternatives.
4. For anything Mouser doesn't carry (or that's cheaper elsewhere), use the Amazon links in `BOM_full.csv` — handy for screws, standoffs, headers, and the LCD.

## Read this before ordering

[`../1-order-boards/v1.4-release-notes.txt`](../1-order-boards/v1.4-release-notes.txt) lists v1.4 part changes and recommendations:

- C6, C7 should be **low-ESR** electrolytics
- For 42TU200 transformers and higher output, use 0.27 Ω at R30 and 680–820 µF at C6/C7
- R55 backlight: 100–220 Ω for New Haven LCDs
- J2-J7 can be substituted with [STX-3100-5N](https://www.mouser.com/ProductDetail/Kycon/STX-3100-5N) (no plastic back cover)

## Substitutions / parts you couldn't find?

The metafetish forum had useful threads on this — see [`../docs/troubleshooting/MK-312BT parts substitution - Estim - Metafetish.pdf`](../docs/troubleshooting/MK-312BT%20parts%20substitution%20-%20Estim%20-%20Metafetish.pdf).

→ Next: [Step 3 — Build and flash](../3-build-and-flash/)
