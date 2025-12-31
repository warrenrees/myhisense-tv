#!/usr/bin/env python3
"""Entry point for hisense2mqtt."""

import argparse
import logging
import sys

from . import __version__
from .bridge import HisenseMQTTBridge
from .config import load_config, validate_config


def setup_logging(level: str = "INFO"):
    """Set up logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from paho-mqtt
    logging.getLogger("paho").setLevel(logging.WARNING)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="hisense2mqtt",
        description="MQTT bridge for Hisense/Vidaa TV control",
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"hisense2mqtt {__version__}",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate config and exit",
    )

    args = parser.parse_args()

    # Load config
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    # Set up logging
    log_level = "DEBUG" if args.debug else config.get("options", {}).get("log_level", "INFO")
    setup_logging(log_level)

    logger = logging.getLogger(__name__)

    # Log config location
    config_path = config.get("_config_path", "defaults")
    logger.info(f"Loaded config from: {config_path}")

    # Validate config
    errors = validate_config(config)
    if errors:
        for error in errors:
            logger.error(f"Config error: {error}")
        if args.validate:
            print("Configuration is INVALID")
        sys.exit(1)

    if args.validate:
        print("Configuration is valid")
        print(f"  MQTT Broker: {config['mqtt']['host']}:{config['mqtt']['port']}")
        print(f"  TV Host: {config['tv']['host']}:{config['tv']['port']}")
        print(f"  TV Name: {config['tv']['name']}")
        print(f"  TV UUID: {config['tv']['uuid']}")
        print(f"  TV MAC: {config['tv'].get('mac', 'not set')}")
        print(f"  Poll Interval: {config['options']['poll_interval']}s")
        print(f"  Discovery: {config['options']['discovery']}")
        print(f"  Wake-on-LAN: {config['options']['wake_on_lan']}")
        sys.exit(0)

    # Start bridge
    logger.info(f"hisense2mqtt v{__version__} starting...")

    bridge = HisenseMQTTBridge(config)

    try:
        bridge.run_forever()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
