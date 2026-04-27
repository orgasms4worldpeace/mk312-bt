# Notes for AI assistants working in this repo

## What this repo is

A 2026 reorganization of two abandoned upstream projects, consolidated into one journey-oriented monorepo:

- [CrashOverride85/mk312-bt](https://github.com/CrashOverride85/mk312-bt) — the MK-312BT box itself (boards, BOM, AVR firmware, 3D-printed case)
- [Rangarig/MK312WIFI](https://github.com/Rangarig/MK312WIFI) — the optional WiFi adapter (ESP8266 firmware + small PCB), **pulled in as a `git subtree`** at `4-wireless/wifi/`
- [clxjaguar/mk312-gui](https://github.com/clxjaguar/mk312-gui) — PyQt control GUI, **pulled in as a `git subtree`** at `5-software/mk312-gui/`

The user is `orgasms4worldpeace`. The clone of the upstream `mk312-bt` was their starting point; the subtree pulls and reorganization happened in this repo.

## Top-level layout follows the build path

```
1-order-boards/   → Send PCB gerbers to a fab (JLCPCB / PCBWay / etc.)
2-order-parts/    → Import the BOM into Mouser, source remaining parts
3-build-and-flash/  → Solder, print the case, flash the AVR
4-wireless/       → Pick bluetooth (HC-05) or wifi (ESP8266) — both pin-compatible
5-software/       → Install mk312-gui (PyQt) — or pick another client
docs/             → Comprehensive build guide + troubleshooting archive
historical/       → v1.2/v1.3 boards, original Eagle source, build photos (archaeology, not for builders)
```

The numbered prefix is intentional — it encodes the build sequence in GitHub's alphabetical file listing, so a builder lands on the repo and sees `1 → 2 → 3 → 4 → 5` at a glance.

## Conventions

- **Firmware lives near the chip it runs on.** AVR firmware for the box is at `3-build-and-flash/firmware/`; ESP firmware for the WiFi adapter is at `4-wireless/wifi/firmware/`. Two `firmware/` directories in different parents — context disambiguates them.
- **Clients (anything that talks to the box from a PC/phone/etc.) all live under `5-software/`.** Including the .NET client — even though it originated bundled inside the MK312WIFI subtree upstream, it's logically a client and so lives in `5-software/dotnet-client/` here.
- **PCB design + ordering live together where they make sense.** Main board + front panel ordering at `1-order-boards/` (mandatory boards). The optional WiFi adapter PCB lives at `4-wireless/wifi/pcb/` (alongside the wifi firmware that runs on it) — its JLCPCB upload bundle is at `4-wireless/wifi/pcb/jlcpcb-package/`.
- **Photos referenced by a README live next to that README.** The MK312WIFI upstream README references `media/foo.png` paths — so `media/` stays inside `4-wireless/wifi/` to keep image links working.
- **Numbered prefixes make the journey obvious.** Don't add new top-level directories without thinking about whether they fit a journey step. If they don't, put them in `docs/` or as a sub-of-something.

## Subtree boundaries

`4-wireless/wifi/` and `5-software/mk312-gui/` are git subtree boundaries. Pulling upstream updates:

```bash
git subtree pull --prefix=4-wireless/wifi      https://github.com/Rangarig/MK312WIFI  main --squash
git subtree pull --prefix=5-software/mk312-gui https://github.com/clxjaguar/mk312-gui main --squash
```

The MK312WIFI subtree has been **internally reorganized** (Contents table in its `README.md` updated, `MK312Wifi/` → `firmware/`, `MK312-wifi-pcb/` → `pcb/`, `DotNetClient/` moved out to `5-software/`). Future subtree pulls from upstream `Rangarig/MK312WIFI` will have **merge conflicts** on these renamed paths — resolve manually, preferring the local path structure. Both upstreams are effectively dormant (last upstream commits 2020-ish for MK312WIFI, occasional cLx pushes for mk312-gui), so this is rare.

## Git identity (important)

This repo lives at `orgasms4worldpeace/mk312-bt`. The local repo's git config is set to commit as `orgasms4worldpeace` with the privacy-preserving noreply email `277349748+orgasms4worldpeace@users.noreply.github.com`. Don't change it.

Both `avosj` (the user's primary GitHub identity) and `orgasms4worldpeace` are authenticated via gh CLI. **`orgasms4worldpeace` must be the active gh account when pushing.** If a push fails with 403, run `gh auth switch -u orgasms4worldpeace` first.

## Local hooks

There's a global hook at `~/.claude/hooks/block-dangerous-git.py` that intercepts destructive git operations (force push, reset --hard, etc.). It will block such commands at the tool boundary. The user can run them themselves with the `!` prefix in Claude Code if needed — don't try to bypass.

## Repo state

- **Visibility: PRIVATE.** Switched from public on 2026-04-26 at the user's request. Don't expose anything assuming public visibility.
- The user is non-technical with respect to PCB design but has hardware-savvy intuition. Translate technical findings into concrete cost / build-time tradeoffs when proposing options (e.g., "$25 vs $80 for 5 boards" rather than just "PCBA setup fees").
- The user prefers concise responses. Don't restate what you just did at the end of every message.

## When in doubt

- Run `git log --oneline -10` to see how recent commits were structured (commit-message style is descriptive, multi-paragraph for non-trivial changes).
- Read the per-section `README.md` in whatever directory you're working in — they explain "what's here and why."
- Check `docs/build-guide.md` for the comprehensive end-to-end builder walkthrough — it's the closest thing to authoritative project documentation.
