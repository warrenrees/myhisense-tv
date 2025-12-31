"""Protocol detection and authentication method selection for Hisense TVs.

Detects the transport protocol version from the TV's UPnP XML descriptor
and selects the appropriate authentication method.
"""

import logging
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from enum import Enum
from typing import List, Optional

from .config import (
    PROTOCOL_MODERN_THRESHOLD,
    PROTOCOL_MIDDLE_THRESHOLD,
    UPNP_PORT,
)

_LOGGER = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication method based on transport protocol version."""
    LEGACY = "legacy"    # < 3000: no XOR username, old suffix
    MIDDLE = "middle"    # 3000-3285: XOR username, old suffix
    MODERN = "modern"    # >= 3290: XOR username, new suffix


def detect_protocol(host: str, port: int = UPNP_PORT, timeout: float = 5.0) -> Optional[int]:
    """Detect transport protocol version from TV's UPnP XML descriptor.

    Fetches http://{host}:{port}/MediaServer/rendererdevicedesc.xml and
    extracts the transport_protocol value.

    Args:
        host: TV IP address or hostname
        port: HTTP port (default 38400)
        timeout: Request timeout in seconds

    Returns:
        Transport protocol version as integer, or None if detection fails
    """
    url = f"http://{host}:{port}/MediaServer/rendererdevicedesc.xml"

    try:
        _LOGGER.debug("Fetching protocol info from %s", url)

        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            xml_content = response.read().decode('utf-8')

        # Parse XML and find transport_protocol
        root = ET.fromstring(xml_content)

        # Method 1: Look for transport_protocol as XML element
        for elem in root.iter():
            if 'transport_protocol' in elem.tag.lower() or elem.tag.endswith('transport_protocol'):
                try:
                    protocol_version = int(elem.text.strip())
                    _LOGGER.info("Detected transport protocol: %d", protocol_version)
                    return protocol_version
                except (ValueError, AttributeError):
                    pass

        # Method 2: Look for transport_protocol in element text content (key=value format)
        # This handles the case where transport_protocol=XXXX is in modelDescription text
        for elem in root.iter():
            if elem.text:
                match = re.search(r'transport_protocol[=:]\s*(\d+)', elem.text, re.IGNORECASE)
                if match:
                    protocol_version = int(match.group(1))
                    _LOGGER.info("Detected transport protocol: %d (from text)", protocol_version)
                    return protocol_version

        # Method 3: Search raw XML content as fallback
        match = re.search(r'transport_protocol[=:]\s*(\d+)', xml_content, re.IGNORECASE)
        if match:
            protocol_version = int(match.group(1))
            _LOGGER.info("Detected transport protocol: %d (from raw XML)", protocol_version)
            return protocol_version

        _LOGGER.warning("transport_protocol not found in XML response")
        return None

    except urllib.error.URLError as e:
        _LOGGER.warning("Failed to fetch protocol info: %s", e)
        return None
    except ET.ParseError as e:
        _LOGGER.warning("Failed to parse XML response: %s", e)
        return None
    except Exception as e:
        _LOGGER.warning("Unexpected error detecting protocol: %s", e)
        return None


def get_auth_method(protocol_version: Optional[int]) -> AuthMethod:
    """Determine authentication method based on protocol version.

    Args:
        protocol_version: Transport protocol version, or None if unknown

    Returns:
        AuthMethod enum value
    """
    if protocol_version is None:
        # Default to modern when unknown (will fallback if needed)
        return AuthMethod.MODERN

    if protocol_version >= PROTOCOL_MODERN_THRESHOLD:
        return AuthMethod.MODERN
    elif protocol_version >= PROTOCOL_MIDDLE_THRESHOLD:
        return AuthMethod.MIDDLE
    else:
        return AuthMethod.LEGACY


def get_auth_method_order() -> List[AuthMethod]:
    """Get the order of authentication methods to try during fallback.

    Returns:
        List of AuthMethod values in order: MODERN, MIDDLE, LEGACY
    """
    return [AuthMethod.MODERN, AuthMethod.MIDDLE, AuthMethod.LEGACY]
