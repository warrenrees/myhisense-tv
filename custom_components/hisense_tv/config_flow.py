"""Config flow for Hisense TV integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import ssdp
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry as dr

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    CONF_MAC,
    CONF_MODEL,
    CONF_SW_VERSION,
    DEFAULT_NAME,
    DEFAULT_PORT,
    TIMEOUT_CONNECT,
)

_LOGGER = logging.getLogger(__name__)

# Import library
import sys
from pathlib import Path

lib_path = Path(__file__).parent.parent.parent
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from hisense_tv import AsyncHisenseTV


async def validate_connection(hass: HomeAssistant, host: str, port: int) -> dict[str, Any]:
    """Validate we can connect to the TV."""
    tv = AsyncHisenseTV(
        host=host,
        port=port,
        use_dynamic_auth=False,  # Don't require MAC for initial validation
        enable_persistence=False,
    )

    try:
        connected = await tv.async_connect(timeout=TIMEOUT_CONNECT)
        if not connected:
            raise CannotConnect("Failed to connect")

        # Get device info
        device_info = await tv.async_get_device_info(timeout=5)
        tv_info = await tv.async_get_tv_info(timeout=5)

        await tv.async_disconnect()

        result = {
            "name": DEFAULT_NAME,
            "model": None,
            "device_id": None,
            "sw_version": None,
        }

        if device_info:
            result["name"] = device_info.get("tv_name", DEFAULT_NAME)
            result["model"] = device_info.get("model_name")
            result["device_id"] = device_info.get("network_type")
            result["sw_version"] = device_info.get("tv_version")

        if tv_info:
            result["device_id"] = result["device_id"] or tv_info.get("deviceid")

        return result

    except Exception as err:
        _LOGGER.error("Error validating connection: %s", err)
        try:
            await tv.async_disconnect()
        except Exception:
            pass
        raise CannotConnect(str(err)) from err


class HisenseTVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hisense TV."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._port: int = DEFAULT_PORT
        self._name: str = DEFAULT_NAME
        self._device_id: str | None = None
        self._model: str | None = None
        self._sw_version: str | None = None
        self._discovery_info: ssdp.SsdpServiceInfo | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step (manual IP entry)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input.get(CONF_PORT, DEFAULT_PORT)

            try:
                info = await validate_connection(self.hass, self._host, self._port)
                self._name = info.get("name", DEFAULT_NAME)
                self._device_id = info.get("device_id")
                self._model = info.get("model")
                self._sw_version = info.get("sw_version")

                # Set unique ID if we got device_id
                if self._device_id:
                    await self.async_set_unique_id(self._device_id)
                    self._abort_if_unique_id_configured(
                        updates={CONF_HOST: self._host, CONF_PORT: self._port}
                    )

                # Check if pairing is needed
                return await self.async_step_pair()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )

    async def async_step_ssdp(
        self, discovery_info: ssdp.SsdpServiceInfo
    ) -> FlowResult:
        """Handle SSDP discovery."""
        _LOGGER.debug("SSDP discovery: %s", discovery_info)

        # Extract host from discovery
        self._host = discovery_info.ssdp_headers.get("_host") or discovery_info.ssdp_location
        if self._host and "://" in self._host:
            # Extract host from URL
            from urllib.parse import urlparse
            parsed = urlparse(self._host)
            self._host = parsed.hostname

        if not self._host:
            return self.async_abort(reason="no_host")

        self._discovery_info = discovery_info
        self._name = discovery_info.upnp.get(ssdp.ATTR_UPNP_FRIENDLY_NAME, DEFAULT_NAME)

        # Try to get unique ID from USN
        usn = discovery_info.ssdp_usn
        if usn:
            # USN format: uuid:XXXX::urn:schemas-upnp-org:...
            if "::" in usn:
                unique_id = usn.split("::")[0].replace("uuid:", "")
            else:
                unique_id = usn.replace("uuid:", "")
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured(updates={CONF_HOST: self._host})

        # Validate connection and get device info
        try:
            info = await validate_connection(self.hass, self._host, self._port)
            self._name = info.get("name", self._name)
            self._device_id = info.get("device_id")
            self._model = info.get("model")
            self._sw_version = info.get("sw_version")

            if self._device_id:
                await self.async_set_unique_id(self._device_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: self._host})

        except CannotConnect:
            return self.async_abort(reason="cannot_connect")

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm the discovered device."""
        if user_input is not None:
            return await self.async_step_pair()

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._name,
                "host": self._host,
            },
        )

    async def async_step_pair(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle pairing step (PIN entry)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            pin = user_input.get("pin", "")

            # Create TV client for pairing
            tv = AsyncHisenseTV(
                host=self._host,
                port=self._port,
                use_dynamic_auth=True,
                mac_address=self._device_id,
                enable_persistence=True,
            )

            try:
                connected = await tv.async_connect(timeout=TIMEOUT_CONNECT)
                if not connected:
                    errors["base"] = "cannot_connect"
                else:
                    # Authenticate with PIN
                    success = await tv.async_authenticate(pin, timeout=10)
                    await tv.async_disconnect()

                    if success:
                        # Create the config entry
                        return self.async_create_entry(
                            title=self._name,
                            data={
                                CONF_HOST: self._host,
                                CONF_PORT: self._port,
                                CONF_NAME: self._name,
                                CONF_DEVICE_ID: self._device_id,
                                CONF_MAC: self._device_id,  # device_id is the MAC without colons
                                CONF_MODEL: self._model,
                                CONF_SW_VERSION: self._sw_version,
                            },
                        )
                    else:
                        errors["base"] = "invalid_pin"

            except Exception as err:
                _LOGGER.exception("Error during pairing: %s", err)
                errors["base"] = "pairing_failed"
                try:
                    await tv.async_disconnect()
                except Exception:
                    pass

        # Show PIN dialog on TV
        tv = AsyncHisenseTV(
            host=self._host,
            port=self._port,
            use_dynamic_auth=True,
            mac_address=self._device_id,
            enable_persistence=False,
        )

        try:
            connected = await tv.async_connect(timeout=TIMEOUT_CONNECT)
            if connected:
                await tv.async_start_pairing()
                # Keep connection open briefly for PIN to appear
                import asyncio
                await asyncio.sleep(1)
                await tv.async_disconnect()
        except Exception as err:
            _LOGGER.warning("Could not trigger PIN dialog: %s", err)

        return self.async_show_form(
            step_id="pair",
            data_schema=vol.Schema(
                {
                    vol.Required("pin"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "name": self._name,
                "host": self._host,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return HisenseTVOptionsFlow(config_entry)


class HisenseTVOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Hisense TV."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
