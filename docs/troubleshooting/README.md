# Troubleshooting

Two kinds of material here:
1. **`debug-notes/`** — original, evidence-based debug documents written for this repo (preferred starting point for live builds).
2. **`metafetish.club archive`** — saved forum threads from before the canonical MK-312BT discussion site went offline.

## Active debug notes (read these first)

| File | When to read |
|------|--------------|
| [`debug-notes/board-test-methodology.pdf`](debug-notes/board-test-methodology.pdf) | **Symptom: LCD shows solid blocks, no text.** Step-by-step bench procedure with annotated silkscreen + ATmega16/LCD pinout references. Power-rail, AVR-socket→LCD continuity, solder-bridge, and contrast/backlight tests with pass/fail decision tree. |
| [`debug-notes/failure-21-analysis.md`](debug-notes/failure-21-analysis.md) | Disassembly-grade analysis of the v1.4 boot self-test. Refutes the forum lore that "Failure 21 = channel B mirror of Failure 20" — F21 is actually the wall-adapter voltage sanity check at PA2 (≥17.1 V trips it). Includes the Newhaven ST7066U power-on reset timing hypothesis for the all-blocks-no-text symptom. |

## metafetish.club archive

The metafetish.club forum (the canonical MK-312BT discussion venue) went offline. These PDFs are saved threads from before the shutdown — preserved here because they contain the highest-quality archived troubleshooting information that exists for this board.

### What's here

| File | When to read |
|------|--------------|
| [`MK-312BT Failure 20 - Estim - Metafetish.pdf`](MK-312BT%20Failure%2020%20-%20Estim%20-%20Metafetish.pdf) | Box shows "Error 20" on boot — the most common build defect |
| [`Another Failure 20 with measurements and some test mode_ - Estim - Metafetish.pdf`](Another%20Failure%2020%20with%20measurements%20and%20some%20test%20mode_%20-%20Estim%20-%20Metafetish.pdf) | Failure 20 deeper dive with scope measurements + test mode usage |
| [`MK312BT Firmware and function issues (Failure 20), debug suggestions_ - Estim - Metafetish.pdf`](MK312BT%20Firmware%20and%20function%20issues%20%28Failure%2020%29%2C%20debug%20suggestions_%20-%20Estim%20-%20Metafetish.pdf) | Firmware-side debugging when hardware looks fine |
| [`MK-312BT Transformer Question - Estim - Metafetish.pdf`](MK-312BT%20Transformer%20Question%20-%20Estim%20-%20Metafetish.pdf) | Picking transformers, 42TU200 vs 42TL004 |
| [`MK-312BT parts substitution - Estim - Metafetish.pdf`](MK-312BT%20parts%20substitution%20-%20Estim%20-%20Metafetish.pdf) | Substitutes for parts Mouser is out of |
| [`Some oscillograms from estim units - Estim - Metafetish.pdf`](Some%20oscillograms%20from%20estim%20units%20-%20Estim%20-%20Metafetish.pdf) | Reference scope traces for a working unit |
| [`Tri Phase Cable on MK312BT - Estim - Metafetish.pdf`](Tri%20Phase%20Cable%20on%20MK312BT%20-%20Estim%20-%20Metafetish.pdf) | Tri-phase output cable wiring |
| [`Getting the Firmware for MK312 - Estim - Metafetish.pdf`](Getting%20the%20Firmware%20for%20MK312%20-%20Estim%20-%20Metafetish.pdf) | Where the AVR firmware actually comes from |
| [`Is the MK-312 BT modern_ - Estim - Metafetish.pdf`](Is%20the%20MK-312%20BT%20modern_%20-%20Estim%20-%20Metafetish.pdf) | Background / context — is this design still worth building |

## Live community

For ongoing help: `#boxes-pulse-based-diy` and `#312-chat` on [Joanne's E-Stim Community Discord](https://discord.gg/rY8C27S).
