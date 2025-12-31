"""Configuration loading with YAML support, env overrides, and migration."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from .schema import (
    DEFAULT_CONFIG,
    DEFAULT_TV_CONFIG,
    deep_merge,
    get_tv_by_id_or_alias,
    get_device_id_by_alias,
)

_LOGGER = logging.getLogger(__name__)

# Config search paths (in priority order)
CONFIG_SEARCH_PATHS = [
    Path("config.yaml"),                              # Current directory (primary)
    Path("/app/config.yaml"),                         # Docker
    Path.home() / ".config" / "hisense_tv" / "config.yaml",  # User home
    Path("/etc/hisense_tv/config.yaml"),             # System-wide
]

# Legacy config paths for migration
LEGACY_CLI_CONFIG = Path.home() / ".config" / "hisense_tv" / "config.json"
LEGACY_BRIDGE_CONFIGS = [
    Path.home() / ".config" / "hisense2mqtt" / "config.yaml",
    Path("/etc/hisense2mqtt/config.yaml"),
]

# Environment variable mappings
# Format: "ENV_VAR": ("section", "key", optional_converter)
ENV_MAPPINGS = {
    # TV settings (applied to default TV)
    "TV_HOST": ("_default_tv", "host"),
    "TV_PORT": ("_default_tv", "port", int),
    "TV_MAC": ("_default_tv", "mac"),
    "TV_UUID": ("_default_tv", "uuid"),
    "TV_NAME": ("_default_tv", "name"),
    "TV_BRAND": ("_default_tv", "brand"),
    # MQTT settings
    "MQTT_HOST": ("mqtt", "host"),
    "MQTT_PORT": ("mqtt", "port", int),
    "MQTT_USERNAME": ("mqtt", "username"),
    "MQTT_PASSWORD": ("mqtt", "password"),
    # Options
    "POLL_INTERVAL": ("options", "poll_interval", int),
    "LOG_LEVEL": ("options", "log_level"),
    "RECONNECT_INTERVAL": ("options", "reconnect_interval", int),
}

# Module-level cached config
_cached_config: Optional[Dict] = None
_cached_path: Optional[Path] = None


def load_config(config_path: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
    """Load configuration from YAML file with environment overrides.

    Args:
        config_path: Explicit path to config file, or None to search
        use_cache: Use cached config if available

    Returns:
        Merged configuration dictionary
    """
    global _cached_config, _cached_path

    if use_cache and _cached_config is not None:
        return _cached_config

    config = _deep_copy_config(DEFAULT_CONFIG)
    loaded_path = None

    # Build search paths
    search_paths: List[Path] = []
    if config_path:
        search_paths.append(Path(config_path))
    search_paths.extend(CONFIG_SEARCH_PATHS)

    # Try YAML files first
    if HAS_YAML:
        for path in search_paths:
            if path.suffix in ('.yaml', '.yml') and path.exists():
                try:
                    with open(path) as f:
                        user_config = yaml.safe_load(f) or {}
                    config = deep_merge(config, user_config)
                    loaded_path = path
                    _LOGGER.info("Loaded config from %s", path)
                    break
                except Exception as e:
                    _LOGGER.warning("Failed to load %s: %s", path, e)

    # If no config found, check for legacy configs and migrate
    if loaded_path is None:
        config = _migrate_legacy_config(config)

    # Apply environment variable overrides
    config = _apply_env_overrides(config)

    # Store metadata
    config["_loaded_from"] = str(loaded_path) if loaded_path else None

    # Cache the config
    _cached_config = config
    _cached_path = loaded_path

    return config


def _deep_copy_config(config: Dict) -> Dict:
    """Create a deep copy of the config dict."""
    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = _deep_copy_config(value)
        elif isinstance(value, list):
            result[key] = value.copy()
        else:
            result[key] = value
    return result


def _migrate_legacy_config(config: Dict) -> Dict:
    """Migrate from legacy JSON or old YAML config format."""
    # Try CLI JSON config
    if LEGACY_CLI_CONFIG.exists():
        try:
            with open(LEGACY_CLI_CONFIG) as f:
                legacy = json.load(f)

            # Create a TV entry using IP as temp key
            tv_ip = legacy.get("tv_ip")
            if tv_ip:
                config["tvs"][tv_ip] = {
                    "host": tv_ip,
                    "port": legacy.get("tv_port", 36669),
                    "brand": legacy.get("brand", "his"),
                }
                if legacy.get("default_uuid"):
                    config["tvs"][tv_ip]["uuid"] = legacy["default_uuid"]
                if legacy.get("tv_mac"):
                    config["tvs"][tv_ip]["mac"] = legacy["tv_mac"]

                config["default_tv"] = tv_ip

            _LOGGER.info("Migrated legacy CLI config from %s", LEGACY_CLI_CONFIG)

        except Exception as e:
            _LOGGER.warning("Failed to migrate legacy CLI config: %s", e)

    # Try legacy bridge YAML configs
    if HAS_YAML:
        for legacy_path in LEGACY_BRIDGE_CONFIGS:
            if legacy_path.exists():
                try:
                    with open(legacy_path) as f:
                        legacy = yaml.safe_load(f) or {}

                    # Migrate old single-TV format to new multi-TV format
                    if "tv" in legacy and "tvs" not in legacy:
                        tv_config = legacy.pop("tv")
                        tv_host = tv_config.get("host")
                        if tv_host:
                            config["tvs"][tv_host] = tv_config
                            config["default_tv"] = tv_host

                    # Merge other sections
                    config = deep_merge(config, legacy)

                    _LOGGER.info("Migrated legacy bridge config from %s", legacy_path)
                    break

                except Exception as e:
                    _LOGGER.warning("Failed to migrate %s: %s", legacy_path, e)

    return config


def _apply_env_overrides(config: Dict) -> Dict:
    """Apply environment variable overrides to config."""
    default_tv_overrides = {}

    for env_var, mapping in ENV_MAPPINGS.items():
        value = os.environ.get(env_var)
        if value is None:
            continue

        section = mapping[0]
        key = mapping[1]
        converter = mapping[2] if len(mapping) > 2 else str

        try:
            converted_value = converter(value)

            if section == "_default_tv":
                default_tv_overrides[key] = converted_value
            elif section in config:
                config[section][key] = converted_value
            else:
                _LOGGER.warning("Unknown config section: %s", section)

        except (ValueError, KeyError) as e:
            _LOGGER.warning("Invalid env var %s=%s: %s", env_var, value, e)

    # Apply default TV overrides
    if default_tv_overrides:
        default_tv = config.get("default_tv")
        if default_tv and default_tv in config.get("tvs", {}):
            config["tvs"][default_tv].update(default_tv_overrides)
        elif default_tv_overrides.get("host"):
            # Create a new TV entry from env vars
            host = default_tv_overrides["host"]
            config["tvs"][host] = deep_merge(
                _deep_copy_config(DEFAULT_TV_CONFIG),
                default_tv_overrides
            )
            config["default_tv"] = host

    return config


def save_config(config: Dict, path: Optional[Path] = None) -> bool:
    """Save configuration to YAML file.

    Args:
        config: Configuration dictionary to save
        path: Destination path, or None for current directory

    Returns:
        True if saved successfully
    """
    if not HAS_YAML:
        _LOGGER.error("PyYAML not installed. Cannot save YAML config.")
        return False

    if path is None:
        path = Path("config.yaml")

    # Remove internal metadata before saving
    save_data = {k: v for k, v in config.items() if not k.startswith("_")}

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.safe_dump(save_data, f, default_flow_style=False, sort_keys=False)
        _LOGGER.info("Saved config to %s", path)
        return True
    except Exception as e:
        _LOGGER.error("Failed to save config: %s", e)
        return False


def get_config(use_cache: bool = True) -> Dict:
    """Get current configuration (cached)."""
    return load_config(use_cache=use_cache)


def reload_config() -> Dict:
    """Force reload configuration from disk."""
    global _cached_config, _cached_path
    _cached_config = None
    _cached_path = None
    return load_config(use_cache=False)


def get_config_path() -> Optional[Path]:
    """Get path of currently loaded config file."""
    load_config(use_cache=True)  # Ensure loaded
    return _cached_path


def get_tv_config(tv_id: Optional[str] = None) -> Optional[Dict]:
    """Get configuration for a specific TV.

    Args:
        tv_id: Device ID or alias. If None, returns default TV.

    Returns:
        TV config dict if found, None otherwise
    """
    config = get_config()
    tvs = config.get("tvs", {})

    if not tvs:
        return None

    if tv_id is None:
        # Return default TV
        default = config.get("default_tv")
        if default:
            return get_tv_by_id_or_alias(config, default)
        # Fall back to first TV
        return next(iter(tvs.values()), None)

    return get_tv_by_id_or_alias(config, tv_id)


def get_default_tv() -> Optional[Dict]:
    """Get the default TV configuration."""
    return get_tv_config(None)


def list_tvs() -> List[Dict]:
    """List all configured TVs.

    Returns:
        List of dicts with device_id and tv config
    """
    config = get_config()
    tvs = config.get("tvs", {})
    default_tv = config.get("default_tv")

    result = []
    for device_id, tv_config in tvs.items():
        entry = {
            "device_id": device_id,
            "is_default": device_id == default_tv or tv_config.get("alias") == default_tv,
            **tv_config,
        }
        result.append(entry)

    return result


def resolve_tv_id(id_or_alias: str) -> Optional[str]:
    """Resolve an alias to device_id.

    Args:
        id_or_alias: Device ID or alias

    Returns:
        Device ID if found, None otherwise
    """
    config = get_config()
    tvs = config.get("tvs", {})

    # Direct match
    if id_or_alias in tvs:
        return id_or_alias

    # Search by alias
    return get_device_id_by_alias(config, id_or_alias)


def update_tv_config(device_id: str, updates: Dict) -> bool:
    """Update configuration for a TV.

    Args:
        device_id: Device ID to update
        updates: Dict of fields to update

    Returns:
        True if updated successfully
    """
    config = get_config()
    tvs = config.get("tvs", {})

    if device_id not in tvs:
        # Create new TV entry
        tvs[device_id] = _deep_copy_config(DEFAULT_TV_CONFIG)

    tvs[device_id].update(updates)

    return save_config(config)


def add_tv(device_id: str, host: str, alias: Optional[str] = None, **kwargs) -> bool:
    """Add a new TV to the configuration.

    Args:
        device_id: Device ID (network_type from TV)
        host: TV IP address
        alias: Friendly name for CLI
        **kwargs: Additional TV config fields

    Returns:
        True if added successfully
    """
    config = get_config()

    tv_config = _deep_copy_config(DEFAULT_TV_CONFIG)
    tv_config["host"] = host
    if alias:
        tv_config["alias"] = alias
    tv_config.update(kwargs)

    config["tvs"][device_id] = tv_config

    # Set as default if first TV
    if len(config["tvs"]) == 1:
        config["default_tv"] = alias or device_id

    return save_config(config)


def set_default_tv(id_or_alias: str) -> bool:
    """Set the default TV.

    Args:
        id_or_alias: Device ID or alias

    Returns:
        True if set successfully
    """
    config = get_config()

    # Verify TV exists
    if get_tv_by_id_or_alias(config, id_or_alias) is None:
        _LOGGER.error("TV not found: %s", id_or_alias)
        return False

    config["default_tv"] = id_or_alias
    return save_config(config)


# Backwards compatibility - convenience functions
def get_tv_ip() -> Optional[str]:
    """Get configured TV IP address (default TV)."""
    tv = get_default_tv()
    return tv.get("host") if tv else None


def get_tv_port() -> int:
    """Get configured TV port (default TV)."""
    tv = get_default_tv()
    return tv.get("port", 36669) if tv else 36669


def get_tv_mac() -> Optional[str]:
    """Get configured TV MAC address (default TV)."""
    tv = get_default_tv()
    return tv.get("mac") if tv else None


def set_tv_ip(ip: str) -> bool:
    """Set TV IP address (default TV)."""
    tv = get_default_tv()
    if tv:
        tv["host"] = ip
        return save_config(get_config())
    return False


def set_tv_mac(mac: str) -> bool:
    """Set TV MAC address (default TV)."""
    tv = get_default_tv()
    if tv:
        tv["mac"] = mac.upper().replace("-", ":")
        return save_config(get_config())
    return False
