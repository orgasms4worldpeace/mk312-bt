# Historical artifacts

**Don't build from this folder.** Go back to [the root README](../README.md) and follow the numbered directories.

This folder preserves earlier MK-312BT board revisions and their source artifacts. Kept around because:

- Some builders still work from v1.2 / v1.3 boards they ordered years ago
- The Eagle source (`.brd` / `.sch`) lives here — v1.4 ships gerbers only, so to **modify** the design, start from the v1.3 source
- The build photos in [`images/`](images/) make a useful visual sanity check when assembling

## Contents

| | |
|--|--|
| [`boms/`](boms/) | Original Mouser BOM CSVs and the OpenOffice / Excel masters from the upstream repo |
| [`eagle-source/`](eagle-source/) | Eagle CAD source for v1.2 main board, v1.2 front panel, v1.3B and v1.3R main boards. Includes the Seeed Gerber generator CAM job |
| [`gerbers/`](gerbers/) | Output gerbers for v1.2 main board, v1.2 front panel, and v1.3 (revised) main board |
| [`images/`](images/) | Build photos for v1.0 and v1.2 |

## Note on v1.4

v1.4 is the current revision (see [`../1-order-boards/`](../1-order-boards/)). It changes only the **main board** — the v1.2 front panel design is still the right one to build.
