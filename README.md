# Home Assistant Integration — Xantech Audio

A custom Home Assistant integration that exposes each enabled zone of a Xantech
MRC88 amplifier as a `media_player` entity, with full control over power,
volume, mute, and source selection.

Communicates directly with the [PyXantech](https://github.com/carlsteinhilber/pyxantech)
Flask app running on your Raspberry Pi. No MQTT broker required.

---

## Installation

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=xantech)

> **Note:** The button above requires [My Home Assistant](https://my.home-assistant.io/) to be set up (links your HA instance to the my.home-assistant.io redirect service). If you haven't set that up, follow the manual steps below.

---

## Requirements

- Home Assistant (2023.6 or later)
- PyXantech Flask app running and accessible on your LAN

---

## Manual Installation

1. Copy the `custom_components/xantech/` folder into your Home Assistant
   configuration directory so the path looks like:

   ```
   <ha_config_dir>/custom_components/xantech/
   ```

   On most installations `<ha_config_dir>` is `/config` (inside the container)
   or the folder that contains your `configuration.yaml`.

2. Restart Home Assistant.

3. Go to **Settings → Devices & Services → Add Integration**.

4. Search for **Xantech Audio** and click it.

5. Enter the IP address and port of the Raspberry Pi running PyXantech
   (default port: `5000`). Click **Submit**.

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
