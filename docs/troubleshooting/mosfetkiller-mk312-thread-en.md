# mosfetkiller.de MK-312-BT thread (English translation)

**Source:** [forum.mosfetkiller.de viewtopic.php?t=64758&start=15](https://forum.mosfetkiller.de/viewtopic.php?t=64758&start=15)

**Original language:** German.
**Captured:** 2026-05-09. Translation by AI; original German posts preserved at the end of each entry for verification.

A German DIY-electronics forum thread (mosfetkiller.de = "MOSFET killer", a friendly e-stim builder community) covering MK-312-BT troubleshooting. The most important technical contribution in the thread is **MWU's correction to the published fuse settings** — `hfuse=0xDC` (the canonical value distributed with the project) breaks the RESET pin behavior; `hfuse=0xD9` is the correct value. Confirmed by another builder in the next post.

---

## Critical findings — read first

### 1. The published `hfuse=0xDC` may be incorrect

Per **MWU** (post #13) and confirmed by **MauiKano** (post #14): the canonical fuse values cause the boot-vector fuse to be enabled, which breaks the RESET pin behavior. If the chip boots into a row of solid white blocks on the LCD and won't reset:

| | Canonical (this repo) | MWU's correction |
|---|---|---|
| LFUSE | 0xFF | 0xFF (same) |
| **HFUSE** | **0xDC** | **0xD9** |

Decoding `0xDC` vs `0xD9`:

- `0xDC` = `1101 1100` → BOOTSZ=11 (256 words), **BOOTRST=0** (boot vector enabled — jump to bootloader on reset)
- `0xD9` = `1101 1001` → BOOTSZ=11 (256 words), **BOOTRST=1** (boot vector disabled — jump to 0x0000 on reset)

The other bits (JTAGEN, OCDEN, SPIEN, etc.) are unchanged. Only BOOTRST differs.

So `0xDC` only works if you're flashing the t002 bootloader **first** and the application firmware on top — the boot vector is supposed to point at the bootloader. If you're flashing application firmware **alone** (no bootloader), use `0xD9` so the chip starts at address 0x0000 on reset.

**Suggestion for this repo:** verify what fuses the various firmware files actually expect and update `docs/build-guide.md` accordingly. The current build guide says `hfuse=0xDC` universally, which is correct **only if the t002 bootloader path is followed**. For builders flashing `f005-HelloFriend.bin` or similar application-only firmware directly, `hfuse=0xD9` is the correct value.

### 2. F20 fix without replacing MOSFETs

Per **MWU** (post #13): instead of swapping mismatched FETs, you can compensate at R32/R43:

- Replace R32 and R43 (the 100 kΩ resistors in the gate-bias network) each with a 470 kΩ trim pot
- Power on, observe F20
- Dial both pots down by equal small amounts, press RESET (you'll need a momentary button to GND on the ISP RESET pin)
- Repeat until F20 clears
- Note the resistance values, then dial up further until F20 returns
- Pick the midpoint, replace pots with fixed resistors at that value

MWU's working value: **120 kΩ for both**. This contradicts the canonical 100 kΩ — the resistance needed depends on the specific MOSFETs installed. With matched FETs the canonical 100 kΩ should work; with off-spec FETs you may need to adjust.

Optional scope verification: scope CH1 (2 V/div) on the ISP RESET pin (one-shot trigger on falling edge), CH2 (10 mV/div) on R30 or one of the FET sources. After RESET you should see two pulse ramps during the self-test. The R32/R43 value range that produces visible passing ramps is what you're looking for.

---

## Per-post translation

### Post 1 — MaxZ (Luca), 2021-10-21

> Good evening everyone. Good news, the box runs!
>
> To help others, let me briefly describe the problems that led to it not working.
>
> The MOSFETs were, as suspected, not the problem. Even so, I tried whether the IRL520N functions identically to the LU120N (both Infineon) — yes, both are recognized by the software without issues.
>
> The problem was an almost invisible break in a solder joint. Probably the previous board didn't start because of a mismatched audio transformer. And on the first board I had the wrong firmware.
>
> Well, a chain of unfortunate circumstances, but I learned a lot from the troubleshooting. That's the most important part.
>
> Beforehand I tested the display itself — I wrote software in Microchip Studio that just outputs simple text. That worked, and afterward the ATmega running the firmware also showed me an error, when previously I'd only gotten an uninitialized display. Maybe it just needed to start up once before things continued.
>
> If anyone has the same problem or is interested in an ET-312 clone build, feel free to PM me. Maybe we can find a solution together.
>
> Thanks again for your tips, that really helped me a lot.
>
> LG, Luca

### Post 2 — ebastler (Paul Wilhelm), 2021-10-22

> Hey Luca, glad you could finally solve the problem. — Paul

### Post 3 — SeriousD, 2021-10-28

> Great that you solved it, I sent you a PM.

### Posts 4–9 — Bombenleger802, Paul, tobias966 (front-panel manufacturing discussion)

These posts cover front-panel manufacturing logistics — Schaeffer AG vs JLCPCB for engraved aluminum vs PCB front panels. Tobias confirms (post #9) that JLCPCB-produced PCB front panels look great. Not relevant to the electrical/firmware problems this archive covers.

### Post 10 — MauiKano, 2021-12-09

> One step further. Looks like I'm close. I can flash firmware. When I flash the initial firmware for the HC-05 Bluetooth module, I see the correct dialog on the display — meaning AVR runs and the display is wired correctly. But when I flash the regular MK-312 firmware (e.g. `Custom Boot Message f005-MK312-BT`), I get either "Failure 20 Shut Off Power!!" or, by reducing input voltage, I can also provoke "Battery Low Shut Off Power."
>
> From all of this I conclude that the MK-312 firmware is running on the AVR but hangs on Error 20 due to some hardware (or other) error. Does anyone know more?

### Post 11 — MauiKano, 2022-01-04

> Hello Luca, I have exactly the problem you described. A row of white blocks in the display.
>
> I'm flashing with a GALEP-5. I think I've set the fuses for the external crystal correctly. All firmware (BT config, "electrodes ready," and F005.bin) produces the same result. A new hardware build behaves identically. What ultimately solved it for you?
>
> Florian

### Post 12 — Thunderbolt (Luca), 2022-01-22

> Hello Florian, sorry for the late reply. I got your PM but I'd rather answer here so others get the benefit.
>
> As mentioned in my earlier post, the issue was mainly with the solder joints. I built the board 4 times in the end before it ran correctly.
>
> When things go badly there's a chain of circumstances.
>
> Check all solder joints again, especially around the op-amps and the ATmega.
>
> Also check that you unzipped the .zip correctly and the .bin isn't corrupted. That happened to me once and I always thought the board didn't work.
>
> You could also scope the output stage during startup — there should be a ramp on startup. (I only have this info from others.)
>
> If problems persist, just contact me again. — Luca

### Post 13 — Thunderbolt (MWU?), 2022-01-24 ⭐ KEY TECHNICAL CONTRIBUTION

> Hello everyone. (I found V1.3R + front PCB on easyEDA and had them made by JLCPCB. Three sets still available. Built two: they work!)
>
> **The fuses are not correct. No boot vector should be used.** You can tell because the RESET pin at ISP (add 10k pull-up to plus and 0.1 µF to GND) doesn't work. **Correct values are e.g. L:FF and H:D9** (I use L:3F H:C9).
>
> Now with the device powered on you can do a reset (briefly tie RESET pin to GND) and trigger a restart.
>
> **Error 21:** Supply voltage / wall adapter should be between 15–19 V.
>
> **Error 20:** Often comes when MOSFETs other than specified are used.
>
> Solution: adjust both 100 kΩ resistors R32 and R43.
>
> 1. Solder a pot (e.g. 470 kΩ) in place of each.
> 2. Install a momentary button to GND on the RESET pin of the ISP.
> 3. Set both pots to max R.
> 4. Power on the device.
> 5. Error: turn both pots down by the same small amount and press RESET.
> 6. At the same time, experiment with both pots.
> 7. Repeat until no more error.
> 8. Measure the pot resistance values out-of-circuit and remember them.
> 9. Continue tweaking until the error returns.
> 10. Determine values, calculate the midpoint of both, and install a matching fixed resistor.
>
> If you have a scope: CH1 (2 V/div) on the ISP RESET pin, one-shot trigger on falling edge. CH2 (10 mV/div) on R30 or one of the FET sources. After RESET you should see two pulse ramps during the self-test. (Important: one-shot trigger.) From a certain resistance up to a certain resistance it will work. I picked the middle and soldered it in. For me, it's **120 kΩ for both**.
>
> **Error 16:** Solution: factory reset. Hold UP/DOWN during power-on until the self-test completes.
>
> Best regards and good luck. MWU

### Post 14 — MauiKano, 2022-01-24

> Hello everyone. Many thanks to Luca and MWU. The solution was as MWU described: **correcting the high fuse setting to D9**. Now the box runs.
>
> Florian

### Post 15 — MauiKano, 2022-03-06

> Good evening everyone. My MK-312 BT runs with the known firmware, after some startup difficulties. Because I wanted to extend/modify the box, I started rebuilding the firmware. I now have a software state that I wouldn't yet call a production release, but the essential functions are implemented and working — so I'm publishing it as a first alpha release at https://github.com/MauiKano/DFD312. Looking forward to feedback from the ET/MK 312 community.

---

## Cross-reference to repo

- The `hfuse=0xD9` correction should be evaluated against the firmware files in `3-build-and-flash/firmware/`. If application-only firmware (e.g. `f005-HelloFriend.bin`) is flashed without the t002 bootloader, MWU's `0xD9` is likely the correct value, not the `0xDC` currently documented.
- The R32/R43 trim-pot procedure for F20 is an alternative path when MOSFET matching isn't possible (no spare FETs, no component tester, or working with a built board that already has soldered FETs). Documented in `docs/troubleshooting/debug-notes/failure-20-analysis.md` as the "Fix" section can be expanded with this procedure.
- The "row of white blocks on display" symptom is now linked to the wrong-fuse condition — worth documenting in the build guide alongside the LCD contrast explanation.
- MauiKano (post #15) wrote his own alternative firmware: [MauiKano/DFD312](https://github.com/MauiKano/DFD312). Could be added to ROADMAP.md as a firmware alternative to investigate.
