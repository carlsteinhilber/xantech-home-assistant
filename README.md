# Home Assistant Integration — Xantech Audio

A custom Home Assistant integration that exposes each enabled zone of a Xantech
MRC88 amplifier as a `media_player` entity, with full control over power,
volume, mute, and source selection.

Communicates directly with the [PyXantech](https://github.com/carlsteinhilber/pyxantech)
Flask app running on your Raspberry Pi. No MQTT broker required.

---

## Requirements

- Home Assistant (2023.6 or later)
- PyXantech Flask app running and accessible on your LAN

---

## Installation

**Step 1 — Copy the integration files**

Copy the `custom_components/xantech/` folder into your Home Assistant
configuration directory so the path looks like:

```
<ha_config_dir>/custom_components/xantech/
```

On most installations `<ha_config_dir>` is `/config` (inside the container)
or the folder that contains your `configuration.yaml`.

**Step 2 — Restart Home Assistant**

The integration will not appear until HA is restarted.

**Step 3 — Add the integration**

Once HA has restarted, click the button below (requires [My Home Assistant](https://my.home-assistant.io/)):

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=xantech)

Or navigate manually: **Settings → Devices & Services → Add Integration** → search for **Xantech Audio**.

**Step 4 — Enter your Pi details**

Enter the IP address and port of the Raspberry Pi running PyXantech (default port: `5000`) and click **Submit**.

Home Assistant will connect to the Flask API, discover all enabled zones,
and create one `media_player` entity per zone. Zone names come from the
PyXantech configuration.

---

## Entities

Each zone appears as a `media_player` entity supporting:

| Feature | Detail |
|---|---|
| Power on/off | `turn_on` / `turn_off` |
| Volume | 0–100% (scaled to 0–38 on hardware) |
| Mute / Unmute | Toggle or explicit |
| Source selection | Dropdown of sources from PyXantech config |

State is polled from the Flask API every 30 seconds.

---

## Automations

Because zones are standard `media_player` entities, all built-in HA
automation actions and conditions work out of the box — including
Google Assistant / Alexa voice commands via the HA cloud integration.

Example automation trigger: "Turn on Living Room when I arrive home"
→ `media_player.turn_on` on `media_player.living_room`

---

## Updating Sources

If you add or remove sources in PyXantech, restart Home Assistant (or reload
the integration via **Settings → Devices & Services → Xantech Audio → ⋮ → Reload**)
to pick up the new source list.

---

## Known Limitations

- **IP is fixed** at setup time. If the Pi's IP changes, remove and re-add
  the integration.
- Zone entities are created once at startup. If you add or remove zones in
  PyXantech, reload the integration.
