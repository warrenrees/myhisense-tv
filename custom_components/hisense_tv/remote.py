"""Remote platform for Hisense TV."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    CONF_MODEL,
    CONF_SW_VERSION,
    DEFAULT_NAME,
)
from .coordinator import HisenseTVDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Mapping of common remote button names to TV key codes
KEY_MAPPING = {
    # Power
    "power": "KEY_POWER",
    "power_on": "KEY_POWER",
    "power_off": "KEY_POWER",
    # Navigation
    "up": "KEY_UP",
    "down": "KEY_DOWN",
    "left": "KEY_LEFT",
    "right": "KEY_RIGHT",
    "select": "KEY_OK",
    "ok": "KEY_OK",
    "enter": "KEY_OK",
    # Menu
    "back": "KEY_RETURNS",
    "return": "KEY_RETURNS",
    "menu": "KEY_MENU",
    "home": "KEY_HOME",
    "exit": "KEY_EXIT",
    # Volume
    "volume_up": "KEY_VOLUMEUP",
    "volume_down": "KEY_VOLUMEDOWN",
    "mute": "KEY_MUTE",
    # Playback
    "play": "KEY_PLAY",
    "pause": "KEY_PAUSE",
    "stop": "KEY_STOP",
    "fast_forward": "KEY_FAST_FORWARD",
    "rewind": "KEY_REWIND",
    "ff": "KEY_FAST_FORWARD",
    "rw": "KEY_REWIND",
    # Channels
    "channel_up": "KEY_CHANNELUP",
    "channel_down": "KEY_CHANNELDOWN",
    # Numbers
    "0": "KEY_0",
    "1": "KEY_1",
    "2": "KEY_2",
    "3": "KEY_3",
    "4": "KEY_4",
    "5": "KEY_5",
    "6": "KEY_6",
    "7": "KEY_7",
    "8": "KEY_8",
    "9": "KEY_9",
    # Colors
    "red": "KEY_RED",
    "green": "KEY_GREEN",
    "yellow": "KEY_YELLOW",
    "blue": "KEY_BLUE",
    # Extras
    "info": "KEY_INFO",
    "subtitle": "KEY_SUBTITLE",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hisense TV remote from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    async_add_entities([HisenseTVRemote(coordinator, entry)])


class HisenseTVRemote(CoordinatorEntity[HisenseTVDataUpdateCoordinator], RemoteEntity):
    """Representation of a Hisense TV remote."""

    _attr_has_entity_name = True
    _attr_name = "Remote"
    _attr_supported_features = RemoteEntityFeature.ACTIVITY

    def __init__(
        self,
        coordinator: HisenseTVDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the remote."""
        super().__init__(coordinator)
        self._entry = entry
        self._device_id = entry.data.get(CONF_DEVICE_ID)
        self._attr_unique_id = f"{self._device_id}_remote" if self._device_id else f"{entry.entry_id}_remote"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_id = self._entry.data.get(CONF_DEVICE_ID)
        mac = self._format_mac(device_id) if device_id else None

        info = DeviceInfo(
            identifiers={(DOMAIN, device_id or self._entry.entry_id)},
            name=self._entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="Hisense",
            model=self._entry.data.get(CONF_MODEL),
            sw_version=self._entry.data.get(CONF_SW_VERSION),
        )

        if mac:
            info["connections"] = {(CONNECTION_NETWORK_MAC, mac)}

        return info

    def _format_mac(self, device_id: str) -> str | None:
        """Format device_id as MAC address."""
        if not device_id or len(device_id) != 12:
            return None
        return ":".join(device_id[i:i+2] for i in range(0, 12, 2)).upper()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.available

    @property
    def is_on(self) -> bool | None:
        """Return if TV is on."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("is_on", False)

    @property
    def current_activity(self) -> str | None:
        """Return current activity (app name or source)."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("app") or self.coordinator.data.get("source")

    @property
    def activity_list(self) -> list[str] | None:
        """Return list of activities (apps)."""
        # Could populate with apps list
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the TV on."""
        await self.coordinator.async_turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the TV off."""
        await self.coordinator.async_turn_off()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send remote commands."""
        num_repeats = kwargs.get("num_repeats", 1)
        delay_secs = kwargs.get("delay_secs", 0.2)

        for _ in range(num_repeats):
            for cmd in command:
                # Map common names to TV keys
                key = KEY_MAPPING.get(cmd.lower(), cmd.upper())
                if not key.startswith("KEY_"):
                    key = f"KEY_{key}"

                await self.coordinator.async_send_key(key)

                if delay_secs > 0:
                    import asyncio
                    await asyncio.sleep(delay_secs)

    async def async_learn_command(self, **kwargs: Any) -> None:
        """Learn a command (not supported)."""
        _LOGGER.warning("Learning commands is not supported on Hisense TV")

    async def async_delete_command(self, **kwargs: Any) -> None:
        """Delete a command (not supported)."""
        _LOGGER.warning("Deleting commands is not supported on Hisense TV")
