"""Wake-on-LAN support for Hisense TV."""

import socket
import struct
from typing import Optional


def create_magic_packet(mac_address: str) -> bytes:
    """Create a Wake-on-LAN magic packet.

    The magic packet consists of:
    - 6 bytes of 0xFF
    - 16 repetitions of the target MAC address (6 bytes each)

    Args:
        mac_address: MAC address in format XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX

    Returns:
        Magic packet as bytes
    """
    # Normalize MAC address
    mac = mac_address.upper().replace(":", "").replace("-", "")
    if len(mac) != 12:
        raise ValueError(f"Invalid MAC address: {mac_address}")

    # Convert hex string to bytes
    mac_bytes = bytes.fromhex(mac)

    # Create magic packet: 6 x 0xFF + 16 x MAC
    return b"\xff" * 6 + mac_bytes * 16


def send_wol(mac_address: str, broadcast: str = "255.255.255.255", port: int = 9) -> bool:
    """Send a Wake-on-LAN magic packet.

    Args:
        mac_address: TV's MAC address
        broadcast: Broadcast address (default: 255.255.255.255)
        port: WoL port (default: 9, can also use 7)

    Returns:
        True if packet was sent successfully
    """
    try:
        packet = create_magic_packet(mac_address)

        # Create UDP socket with broadcast enabled
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Send to broadcast address
        sock.sendto(packet, (broadcast, port))
        sock.close()

        return True
    except Exception as e:
        print(f"WoL error: {e}")
        return False


def wake_tv(mac_address: str, subnet: Optional[str] = None) -> bool:
    """Wake up the TV using Wake-on-LAN.

    Sends magic packet to multiple broadcast addresses for reliability.

    Args:
        mac_address: TV's MAC address
        subnet: Optional subnet (e.g., "10.0.0" to use 10.0.0.255)

    Returns:
        True if packets were sent
    """
    broadcasts = ["255.255.255.255"]

    # Add subnet-specific broadcast if provided
    if subnet:
        broadcasts.append(f"{subnet}.255")

    success = False
    for bcast in broadcasts:
        # Try both common WoL ports
        for port in [9, 7]:
            if send_wol(mac_address, bcast, port):
                success = True

    return success


def get_mac_from_ip(ip: str) -> Optional[str]:
    """Try to get MAC address from IP using ARP table.

    Args:
        ip: IP address to look up

    Returns:
        MAC address if found, None otherwise
    """
    import subprocess
    import re

    try:
        # Ping first to populate ARP cache
        subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True,
            timeout=3
        )

        # Check ARP table
        result = subprocess.run(
            ["arp", "-n", ip],
            capture_output=True,
            text=True,
            timeout=3
        )

        # Parse MAC from output
        # Format: "10.0.0.125  ether  XX:XX:XX:XX:XX:XX  C  eth0"
        mac_pattern = r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}"
        match = re.search(mac_pattern, result.stdout)
        if match:
            return match.group(0).upper().replace("-", ":")

    except Exception:
        pass

    return None
