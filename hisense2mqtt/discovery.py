"""Home Assistant MQTT Discovery for hisense2mqtt."""

import json
from typing import Any, Optional

from . import __version__


def get_device_info(config: dict, device_id: str) -> dict:
    """Generate Home Assistant device info from config."""
    tv_config = config.get("tv", {})

    return {
        "identifiers": [f"hisense_{device_id}"],
        "name": tv_config.get("name", "Hisense TV"),
        "manufacturer": "Hisense",
        "model": tv_config.get("model", "Vidaa Smart TV"),
        "sw_version": tv_config.get("sw_version", __version__),
    }


def get_availability(device_id: str) -> list[dict]:
    """Generate availability config."""
    return [
        {
            "topic": f"hisense2mqtt/{device_id}/state/available",
            "payload_available": "online",
            "payload_not_available": "offline",
        }
    ]


def generate_media_player_discovery(config: dict, device_id: str, discovery_prefix: str) -> tuple[str, dict]:
    """Generate media player discovery payload.

    Returns:
        Tuple of (topic, payload)
    """
    topic = f"{discovery_prefix}/media_player/hisense_{device_id}/config"

    sources = ["TV", "HDMI1", "HDMI2", "HDMI3", "HDMI4", "AV", "Component"]

    payload = {
        "name": None,  # Use device name
        "unique_id": f"hisense_{device_id}_media_player",
        "object_id": f"hisense_{device_id}",
        "device": get_device_info(config, device_id),
        "availability": get_availability(device_id),
        # State - use "on"/"off" for proper logbook events
        "state_topic": f"hisense2mqtt/{device_id}/state/power",
        "state_value_template": "{{ 'on' if value == 'ON' else 'off' }}",
        # Commands
        "command_topic": f"hisense2mqtt/{device_id}/set/power",
        "payload_on": "ON",
        "payload_off": "OFF",
        # Volume
        "volume_level_topic": f"hisense2mqtt/{device_id}/state/volume",
        "volume_level_template": "{{ value | float / 100 }}",
        "set_volume_topic": f"hisense2mqtt/{device_id}/set/volume",
        # Mute
        "mute_state_topic": f"hisense2mqtt/{device_id}/state/mute",
        "mute_command_topic": f"hisense2mqtt/{device_id}/set/mute",
        "payload_mute_on": "ON",
        "payload_mute_off": "OFF",
        # Source / Current App
        "source_list": sources,
        "source_topic": f"hisense2mqtt/{device_id}/state/source",
        "source_command_topic": f"hisense2mqtt/{device_id}/set/source",
        # Media info - shows current app
        "media_title_topic": f"hisense2mqtt/{device_id}/state/app",
        "media_title_template": "{{ value }}",
        # Icon
        "icon": "mdi:television",
    }

    return topic, payload


def generate_power_switch_discovery(config: dict, device_id: str, discovery_prefix: str) -> tuple[str, dict]:
    """Generate switch for power control."""
    topic = f"{discovery_prefix}/switch/hisense_{device_id}_power/config"

    payload = {
        "name": "Power",
        "unique_id": f"hisense_{device_id}_power",
        "object_id": f"hisense_{device_id}_power",
        "device": get_device_info(config, device_id),
        "availability": get_availability(device_id),
        "state_topic": f"hisense2mqtt/{device_id}/state/power",
        "command_topic": f"hisense2mqtt/{device_id}/set/power",
        "payload_on": "ON",
        "payload_off": "OFF",
        "state_on": "ON",
        "state_off": "OFF",
        "icon": "mdi:power",
    }

    return topic, payload


def generate_app_sensor_discovery(config: dict, device_id: str, discovery_prefix: str) -> tuple[str, dict]:
    """Generate sensor for current app."""
    topic = f"{discovery_prefix}/sensor/hisense_{device_id}_app/config"

    payload = {
        "name": "Current App",
        "unique_id": f"hisense_{device_id}_current_app",
        "object_id": f"hisense_{device_id}_current_app",
        "device": get_device_info(config, device_id),
        "availability": get_availability(device_id),
        "state_topic": f"hisense2mqtt/{device_id}/state/app",
        "icon": "mdi:application",
    }

    return topic, payload


def generate_volume_discovery(config: dict, device_id: str, discovery_prefix: str) -> tuple[str, dict]:
    """Generate number entity for volume control."""
    topic = f"{discovery_prefix}/number/hisense_{device_id}_volume/config"

    payload = {
        "name": "Volume",
        "unique_id": f"hisense_{device_id}_volume",
        "object_id": f"hisense_{device_id}_volume",
        "device": get_device_info(config, device_id),
        "availability": get_availability(device_id),
        "state_topic": f"hisense2mqtt/{device_id}/state/volume",
        "command_topic": f"hisense2mqtt/{device_id}/set/volume",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit_of_measurement": "%",
        "icon": "mdi:volume-high",
    }

    return topic, payload


def generate_mute_switch_discovery(config: dict, device_id: str, discovery_prefix: str) -> tuple[str, dict]:
    """Generate switch for mute control."""
    topic = f"{discovery_prefix}/switch/hisense_{device_id}_mute/config"

    payload = {
        "name": "Mute",
        "unique_id": f"hisense_{device_id}_mute",
        "object_id": f"hisense_{device_id}_mute",
        "device": get_device_info(config, device_id),
        "availability": get_availability(device_id),
        "state_topic": f"hisense2mqtt/{device_id}/state/mute",
        "command_topic": f"hisense2mqtt/{device_id}/set/mute",
        "payload_on": "ON",
        "payload_off": "OFF",
        "state_on": "ON",
        "state_off": "OFF",
        "icon": "mdi:volume-off",
    }

    return topic, payload


def generate_button_discovery(
    config: dict, device_id: str, discovery_prefix: str, button_id: str, name: str, icon: str
) -> tuple[str, dict]:
    """Generate button discovery payload for remote keys."""
    topic = f"{discovery_prefix}/button/hisense_{device_id}_{button_id}/config"

    payload = {
        "name": name,
        "unique_id": f"hisense_{device_id}_{button_id}",
        "object_id": f"hisense_{device_id}_{button_id}",
        "device": get_device_info(config, device_id),
        "availability": get_availability(device_id),
        "command_topic": f"hisense2mqtt/{device_id}/set/key",
        "payload_press": button_id.upper(),
        "icon": icon,
    }

    return topic, payload


def generate_select_discovery(
    config: dict, device_id: str, discovery_prefix: str, apps: list[str]
) -> tuple[str, dict]:
    """Generate select discovery for app launcher."""
    topic = f"{discovery_prefix}/select/hisense_{device_id}_app/config"

    payload = {
        "name": "Launch App",
        "unique_id": f"hisense_{device_id}_app",
        "object_id": f"hisense_{device_id}_app",
        "device": get_device_info(config, device_id),
        "availability": get_availability(device_id),
        "command_topic": f"hisense2mqtt/{device_id}/set/app",
        "options": apps,
        "icon": "mdi:apps",
    }

    return topic, payload


def generate_all_discoveries(
    config: dict, device_id: str, apps: Optional[list[str]] = None
) -> list[tuple[str, dict]]:
    """Generate all discovery payloads.

    Args:
        config: Configuration dictionary
        device_id: Unique device identifier
        apps: List of app names from TV (optional, uses defaults if not provided)

    Returns:
        List of (topic, payload) tuples
    """
    discovery_prefix = config.get("mqtt", {}).get("discovery_prefix", "homeassistant")
    discoveries = []

    # Media player (main entity)
    discoveries.append(generate_media_player_discovery(config, device_id, discovery_prefix))

    # Power switch (controllable)
    discoveries.append(generate_power_switch_discovery(config, device_id, discovery_prefix))

    # Volume control
    discoveries.append(generate_volume_discovery(config, device_id, discovery_prefix))

    # Mute switch
    discoveries.append(generate_mute_switch_discovery(config, device_id, discovery_prefix))

    # Current app sensor
    discoveries.append(generate_app_sensor_discovery(config, device_id, discovery_prefix))

    # Navigation buttons
    nav_buttons = [
        ("up", "Up", "mdi:chevron-up"),
        ("down", "Down", "mdi:chevron-down"),
        ("left", "Left", "mdi:chevron-left"),
        ("right", "Right", "mdi:chevron-right"),
        ("ok", "OK", "mdi:checkbox-marked-circle"),
        ("back", "Back", "mdi:arrow-left"),
        ("home", "Home", "mdi:home"),
        ("menu", "Menu", "mdi:menu"),
    ]

    for button_id, name, icon in nav_buttons:
        discoveries.append(
            generate_button_discovery(config, device_id, discovery_prefix, button_id, name, icon)
        )

    # App launcher - use provided apps or defaults
    if apps is None:
        apps = ["Netflix", "YouTube", "Amazon", "Disney+", "Hulu", "Tubi"]
    discoveries.append(generate_select_discovery(config, device_id, discovery_prefix, apps))

    return discoveries


def remove_all_discoveries(config: dict, device_id: str) -> list[str]:
    """Generate list of discovery topics to clear (for removal).

    Returns:
        List of topics to publish empty payload to
    """
    discovery_prefix = config.get("mqtt", {}).get("discovery_prefix", "homeassistant")

    topics = [
        f"{discovery_prefix}/media_player/hisense_{device_id}/config",
        f"{discovery_prefix}/switch/hisense_{device_id}_power/config",
        f"{discovery_prefix}/number/hisense_{device_id}_volume/config",
        f"{discovery_prefix}/switch/hisense_{device_id}_mute/config",
        f"{discovery_prefix}/sensor/hisense_{device_id}_app/config",
        f"{discovery_prefix}/select/hisense_{device_id}_app/config",
        # Legacy binary_sensor (in case upgrading from old version)
        f"{discovery_prefix}/binary_sensor/hisense_{device_id}_power/config",
    ]

    nav_buttons = ["up", "down", "left", "right", "ok", "back", "home", "menu"]
    for button_id in nav_buttons:
        topics.append(f"{discovery_prefix}/button/hisense_{device_id}_{button_id}/config")

    return topics
