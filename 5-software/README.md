# Step 5 — Software

You've built the box, flashed it, and added a wireless adapter. Now you need a client to control it.

## Recommended client: mk312-gui — [`mk312-gui/`](mk312-gui/)

A PyQt-based GUI by **cLx** (co-author of the WiFi adapter). Pulled in here as a git subtree from [clxjaguar/mk312-gui](https://github.com/clxjaguar/mk312-gui).

Speaks two transports:

- **WiFi** — talks the MK312WIFI bridge protocol (UDP discovery on port 8842, TCP control on 8843). Works with the [`4-wireless/wifi/`](../4-wireless/wifi/) adapter
- **Serial** — for the ET-312-style "link mode" cable (PC ↔ box over RS232). Less common, but useful for protocol experimentation

Bonus: ships with a [LUA mpv script](mk312-gui/utils/) that lets you drive the box from video subtitles — i.e. video-synchronized remote control via timed cues in an `.srt` file.

### Install + run

```bash
cd 5-software/mk312-gui
pip install -r requirements.txt   # pyserial, PyQt5
python mk312-gui.py
```

### Pull upstream updates

```bash
git subtree pull --prefix=5-software/mk312-gui https://github.com/clxjaguar/mk312-gui main --squash
```

## Other clients (linked, not bundled)

| Project | Language | What | Status |
|---------|----------|------|--------|
| [clxjaguar/mk312-raw-control](https://github.com/clxjaguar/mk312-raw-control) | Python | "Link mode" override via serial — bypass running programs to do experiments and direct measurements | Active (2026-02) |
| [Rubberfate/mk312com](https://github.com/Rubberfate/mk312com) | Python | Lower-level MK-312 communication wrapper library | Stale (2021) |
| [Carumbad/HomeAssistant_ET312](https://github.com/Carumbad/HomeAssistant_ET312) | Python | Home Assistant integration (ET-312, mostly applicable to MK-312BT) | Active (2026-04) |
| [Carumbad/et312_mqtt](https://github.com/Carumbad/et312_mqtt) | Python | MQTT bridge — control via any MQTT client | Stale (2020) |
| [.NET client](dotnet-client/) | C# | Reference C# implementation, originally bundled with MK312WIFI — useful as a Unity/VR starting point | Stale (2020) |
| [kinkytofu/buttshock-py](https://github.com/kinkytofu/buttshock-py) | Python | The original ET-312 protocol library — predecessor of all the above | Archived (2016) |

## Bluetooth clients?

If you used [`4-wireless/bluetooth/`](../4-wireless/bluetooth/) (HC-05) instead of WiFi, **mk312-gui won't connect** — it doesn't speak Bluetooth Classic SPP. You'll need a different client (e.g. an Android app from the e-stim community) or a serial-over-Bluetooth shim. Or just use the WiFi adapter.
