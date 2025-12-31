"""Data update coordinator for Hisense TV."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL, STATE_FAKE_SLEEP

_LOGGER = logging.getLogger(__name__)


class HisenseTVDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data updates from Hisense TV."""

    def __init__(
        self,
        hass: HomeAssistant,
        tv,  # AsyncHisenseTV
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.tv = tv
        self.entry = entry
        self._available = True

    @property
    def available(self) -> bool:
        """Return if TV is available."""
        return self._available

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from TV."""
        try:
            # Check connection
            if not self.tv.is_connected:
                _LOGGER.debug("TV disconnected, attempting reconnect")
                connected = await self.tv.async_connect(timeout=5)
                if not connected:
                    self._available = False
                    raise UpdateFailed("Failed to connect to TV")

            self._available = True

            # Get current state
            state = await self.tv.async_get_state(timeout=3)

            # Determine power state
            is_on = True
            if state:
                if state.get("statetype") == STATE_FAKE_SLEEP:
                    is_on = False
            else:
                # No state response - TV might be off or unreachable
                is_on = False

            # Get volume (only if TV is on)
            volume = None
            is_muted = False
            if is_on:
                try:
                    volume = await self.tv.async_get_volume(timeout=2)
                except Exception:
                    pass

            # Build data dict
            data = {
                "is_on": is_on,
                "state": state,
                "volume": volume,
                "is_muted": is_muted,
                "source": state.get("sourcename") if state else None,
                "app": state.get("currentappname") if state else None,
            }

            return data

        except Exception as err:
            self._available = False
            raise UpdateFailed(f"Error communicating with TV: {err}") from err

    async def async_turn_on(self) -> None:
        """Turn TV on."""
        await self.tv.async_power_on()
        await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn TV off."""
        await self.tv.async_power_off()
        await self.async_request_refresh()

    async def async_volume_up(self) -> None:
        """Increase volume."""
        await self.tv.async_volume_up()
        await self.async_request_refresh()

    async def async_volume_down(self) -> None:
        """Decrease volume."""
        await self.tv.async_volume_down()
        await self.async_request_refresh()

    async def async_mute(self) -> None:
        """Toggle mute."""
        await self.tv.async_mute()
        await self.async_request_refresh()

    async def async_set_volume(self, volume: int) -> None:
        """Set volume level."""
        await self.tv.async_set_volume(volume)
        await self.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self.tv.async_set_source(source)
        await self.async_request_refresh()

    async def async_send_key(self, key: str) -> None:
        """Send remote key."""
        await self.tv.async_send_key(key)

    async def async_launch_app(self, app_name: str) -> None:
        """Launch app."""
        await self.tv.async_launch_app(app_name)
        await self.async_request_refresh()

    async def async_get_apps(self) -> list[dict] | None:
        """Get available apps."""
        return await self.tv.async_get_apps()

    async def async_get_sources(self) -> list[dict] | None:
        """Get available sources."""
        return await self.tv.async_get_sources()
