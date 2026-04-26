# Step 2 — Order parts

Three BOM files, same data, different formats:

| File | Use it for |
|------|-----------|
| [`BOM-mouser-cart.csv`](BOM-mouser-cart.csv) | **Direct import into Mouser's BOM Tool** — fastest path to a cart |
| [`BOM-with-amazon.xlsx`](BOM-with-amazon.xlsx) | Human-readable spreadsheet with both Mouser **and Amazon** links per part |
| [`BOM-full.csv`](BOM-full.csv) | Master copy — same as the xlsx plus a `Sourced?` column for tracking what you've already bought |

## How to use

1. Sign in to [mouser.com](https://www.mouser.com/) and open their **BOM Tool**.
2. Upload `BOM-mouser-cart.csv`.
3. Review and add to cart. Some parts may need substitution if Mouser is out of stock — check `BOM-with-amazon.xlsx` for the part number and search alternatives.
4. Anything Mouser doesn't carry (or that's cheaper elsewhere): cross-reference `BOM-with-amazon.xlsx` for Amazon links — useful for screws, standoffs, headers, the LCD, etc.

## Read this before ordering

[`../1-order-boards/v1.4-release-notes.txt`](../1-order-boards/v1.4-release-notes.txt) lists v1.4 part changes and recommendations:

- C6, C7 should be **low-ESR** electrolytics
- For 42TU200 transformers + higher output: use 0.27 Ω at R30, 680–820 µF at C6/C7
- R55 backlight: 100–220 Ω for New Haven LCDs
- J2-J7 can be substituted with [STX-3100-5N](https://www.mouser.com/ProductDetail/Kycon/STX-3100-5N) (no plastic back cover)

## Substitutions / parts you couldn't find?

The metafetish forum had useful threads on this — see [`../docs/troubleshooting/MK-312BT parts substitution - Estim - Metafetish.pdf`](../docs/troubleshooting/MK-312BT%20parts%20substitution%20-%20Estim%20-%20Metafetish.pdf).

→ Next: [Step 3 — Build and flash](../3-build-and-flash/)
