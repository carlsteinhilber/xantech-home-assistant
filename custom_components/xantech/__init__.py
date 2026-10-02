"""Xantech Audio integration for Home Assistant."""
from __future__ import annotations

import logging
import re
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

DOMAIN = "xantech"
PLATFORMS = [Platform.MEDIA_PLAYER]
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xantech from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    session = async_get_clientsession(hass)

    coordinator = XantechCoordinator(hass, session, host, port)
    await coordinator.async_fetch_config()
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class XantechCoordinator(DataUpdateCoordinator):
    """Manages polling of Xantech zone states from the Flask API."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession,
                 host: str, port: int) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.session = session
        self.host = host
        self.port = port
        # source_num (int) -> display name (str), ordered by source number
        self.sources: dict[int, str] = {}

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    async def async_fetch_config(self) -> None:
        """Fetch source and zone config from /api/config."""
        try:
            async with self.session.get(
                f"{self.base_url}/api/config",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except Exception as err:
            _LOGGER.warning("Could not fetch /api/config: %s", err)
            return

        sources: dict[int, str] = {}
        for s in data.get("sources", []):
            if s.get("enabled") and s.get("name", "").strip():
                num = int(s["source"])
                sources[num] = s["name"].strip()
        self.sources = dict(sorted(sources.items()))
        _LOGGER.debug("Xantech sources: %s", self.sources)

    async def _async_update_data(self) -> dict:
        """Fetch all zone states from /api/zones."""
        try:
            async with self.session.get(
                f"{self.base_url}/api/zones",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching Xantech zones: {err}") from err

    async def async_update_zone(self, zone_num: int, props: dict) -> bool:
        """Send a PUT request to update a single zone."""
        try:
            async with self.session.put(
                f"{self.base_url}/api/zones/{zone_num}",
                json=props,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
                return True
        except Exception as err:
            _LOGGER.error("Error updating zone %d: %s", zone_num, err)
            return False
