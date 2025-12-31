# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2024-12-30

### Added

- **Network Discovery Module** (`hisense_tv.discovery`)
  - SSDP M-SEARCH active discovery
  - SSDP NOTIFY passive listener
  - UDP broadcast discovery on port 36671
  - Direct IP probe functionality
  - `DiscoveredTV` dataclass for structured results

- **Protocol Auto-Detection**
  - Automatic detection of transport protocol version from TV's UPnP descriptor
  - Three authentication methods: LEGACY (< 3000), MIDDLE (3000-3285), MODERN (>= 3290)
  - Automatic fallback through authentication methods if detection fails

- **Token Persistence**
  - Save and restore authentication tokens
  - Automatic token refresh when access token expires
  - Support for storing multiple device credentials

### Changed

- Replaced `print()` statements with proper `logging` in library code
- Improved type hints for Python 3.8 compatibility
- Updated configuration to use empty defaults (user must configure)

### Fixed

- Protocol detection now correctly parses `transport_protocol` from XML text content
- Type hints now compatible with Python 3.8+

## [1.2.0] - 2024-12-28

### Added

- Dynamic credential generation based on protocol analysis
- XOR-based username obfuscation for modern protocol
- MD5 password hashing with protocol-specific suffixes
- Wake-on-LAN support

### Changed

- Improved MQTT connection handling
- Better error messages for authentication failures

## [1.1.0] - 2024-12-27

### Added

- Home Assistant MQTT auto-discovery
- Source selection (HDMI, TV, AV inputs)
- App launching functionality
- Volume control with get/set

### Changed

- Improved SSL/TLS handling for self-signed certificates

## [1.0.0] - 2024-12-26

### Added

- Initial release
- MQTT client for Hisense/Vidaa TV control
- Remote key sending (50+ keys)
- Power control
- Basic authentication flow
- CLI interface
- Docker support
