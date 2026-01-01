"""Data update coordinator for Hisense TV."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL, STATE_FAKE_SLEEP, CONF_DEVICE_ID

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
        self._device_info_fetched = False

    @property
    def available(self) -> bool:
        """Return if TV is available."""
        return self._available

    async def _async_update_device_info(self) -> None:
        """Fetch and update device info in the device registry."""
        if self._device_info_fetched:
            return

        try:
            device_info = await self.tv.async_get_device_info(timeout=5)
            _LOGGER.debug("Got device info: %s", device_info)

            if not device_info:
                _LOGGER.warning("No device info returned from TV")
                return

            device_id = self.entry.data.get(CONF_DEVICE_ID)
            _LOGGER.debug("Config entry device_id: %s", device_id)

            if not device_id:
                device_id = device_info.get("network_type")
                _LOGGER.debug("Using network_type as device_id: %s", device_id)

            # Update device registry - try device_id first, then entry_id as fallback
            device_registry = dr.async_get(self.hass)
            device_entry = None

            # Try with device_id from device info
            if device_id:
                device_entry = device_registry.async_get_device(
                    identifiers={(DOMAIN, device_id)}
                )
                _LOGGER.debug("Lookup by device_id %s: found=%s", device_id, device_entry is not None)

            # Fallback to entry_id (used when device_id was None during setup)
            if not device_entry:
                device_entry = device_registry.async_get_device(
                    identifiers={(DOMAIN, self.entry.entry_id)}
                )
                _LOGGER.debug("Lookup by entry_id %s: found=%s", self.entry.entry_id, device_entry is not None)

            if device_entry:
                updates = {}
                model = device_info.get("model_name")
                sw_version = device_info.get("tv_version")
                name = device_info.get("tv_name")

                _LOGGER.debug("Device info - model: %s, sw_version: %s, name: %s",
                             model, sw_version, name)

                if model and model != device_entry.model:
                    updates["model"] = model
                if sw_version and sw_version != device_entry.sw_version:
                    updates["sw_version"] = sw_version
                if name and name != device_entry.name:
                    updates["name"] = name

                if updates:
                    device_registry.async_update_device(device_entry.id, **updates)
                    _LOGGER.info("Updated device info: %s", updates)
                else:
                    _LOGGER.debug("No device info updates needed")
            else:
                _LOGGER.warning("Device not found in registry with id: %s", device_id)

            self._device_info_fetched = True

        except Exception as err:
            _LOGGER.warning("Error fetching device info: %s", err)

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

            # Update device info on first successful connection
            await self._async_update_device_info()

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
