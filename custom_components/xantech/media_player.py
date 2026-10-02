"""Xantech media player entities — one per enabled zone."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, XantechCoordinator

_LOGGER = logging.getLogger(__name__)

# Flask hardware range: 0–38
VOLUME_MAX = 38

SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SELECT_SOURCE
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one XantechZone entity for each zone returned by the API."""
    coordinator: XantechCoordinator = hass.data[DOMAIN][entry.entry_id]

    zones_data: dict = coordinator.data or {}
    entities = []
    for zone_key, zone_data in zones_data.items():
        n = int(zone_key)
        name = (zone_data.get("name") or "").strip() or f"Zone {n}"
        entities.append(XantechZone(coordinator, n, name))

    async_add_entities(entities)


class XantechZone(CoordinatorEntity[XantechCoordinator], MediaPlayerEntity):
    """A single Xantech audio zone exposed as a media_player entity."""

    _attr_has_entity_name = False  # name IS the entity name (e.g. "Living Room")

    def __init__(
        self, coordinator: XantechCoordinator, zone_num: int, name: str
    ) -> None:
        super().__init__(coordinator)
        self._zone_num = zone_num
        self._attr_name = name
        self._attr_unique_id = f"xantech_zone_{zone_num}"
        self._attr_supported_features = SUPPORTED_FEATURES
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"zone_{zone_num}")},
            "name": name,
            "manufacturer": "Xantech",
            "model": "MRC88 Audio Zone",
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def _zone_data(self) -> dict:
        data = self.coordinator.data or {}
        # API returns string keys ("1", "2", …)
        return data.get(str(self._zone_num)) or {}

    # ------------------------------------------------------------------
    # State properties
    # ------------------------------------------------------------------

    @property
    def state(self) -> MediaPlayerState:
        return (
            MediaPlayerState.ON
            if self._zone_data.get("power")
            else MediaPlayerState.OFF
        )

    @property
    def volume_level(self) -> float | None:
        v = self._zone_data.get("volume")
        return round(v / VOLUME_MAX, 4) if v is not None else None

    @property
    def is_volume_muted(self) -> bool | None:
        return self._zone_data.get("mute")

    @property
    def source(self) -> str | None:
        """Return the display name of the current source."""
        src_num = self._zone_data.get("source")
        if src_num is not None:
            return self.coordinator.sources.get(int(src_num))
        return None

    @property
    def source_list(self) -> list[str]:
        """Return display names of all available sources."""
        return list(self.coordinator.sources.values())

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def async_turn_on(self) -> None:
        await self.coordinator.async_update_zone(self._zone_num, {"power": True})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self.coordinator.async_update_zone(self._zone_num, {"power": False})
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        fl_vol = round(volume * VOLUME_MAX)
        await self.coordinator.async_update_zone(self._zone_num, {"volume": fl_vol})
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        await self.coordinator.async_update_zone(self._zone_num, {"muted": mute})
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select source by display name."""
        for num, name in self.coordinator.sources.items():
            if name == source:
                await self.coordinator.async_update_zone(
                    self._zone_num, {"source": num}
                )
                await self.coordinator.async_request_refresh()
                return
        _LOGGER.warning("Xantech: unknown source %r", source)
