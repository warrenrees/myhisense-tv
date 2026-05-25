"""Remote key constants for Hisense TV.

Keys discovered from Vidaa APK decompilation (libmqttcrypt.so, SdkMqttPublishManager).
"""

# Power
KEY_POWER = "KEY_POWER"

# Navigation
KEY_UP = "KEY_UP"
KEY_DOWN = "KEY_DOWN"
KEY_LEFT = "KEY_LEFT"
KEY_RIGHT = "KEY_RIGHT"
KEY_OK = "KEY_OK"
KEY_ENTER = "KEY_OK"  # Alias

# Long Press Navigation
KEY_OK_LONG_PRESS = "KEY_OK_LONG_PRESS"

# Menu/Back
KEY_MENU = "KEY_MENU"
KEY_BACK = "KEY_RETURNS"
KEY_RETURNS = "KEY_RETURNS"
KEY_EXIT = "KEY_EXIT"
KEY_HOME = "KEY_HOME"

# Volume
KEY_VOLUME_UP = "KEY_VOLUMEUP"
KEY_VOLUME_DOWN = "KEY_VOLUMEDOWN"
KEY_MUTE = "KEY_MUTE"
KEY_MUTE_LONG_PRESS = "KEY_MUTE_LONG_PRESS"

# Voice Control
KEY_VOICE_UP = "KEY_VOICEUP"
KEY_VOICE_DOWN = "KEY_VOICEDOWN"

# Playback
KEY_PLAY = "KEY_PLAY"
KEY_PAUSE = "KEY_PAUSE"
KEY_STOP = "KEY_STOP"
KEY_FAST_FORWARD = "KEY_FORWARDS"
KEY_FORWARDS = "KEY_FORWARDS"  # Alias for hisense.py compatibility
KEY_REWIND = "KEY_BACK"

# Numbers
KEY_0 = "KEY_0"
KEY_1 = "KEY_1"
KEY_2 = "KEY_2"
KEY_3 = "KEY_3"
KEY_4 = "KEY_4"
KEY_5 = "KEY_5"
KEY_6 = "KEY_6"
KEY_7 = "KEY_7"
KEY_8 = "KEY_8"
KEY_9 = "KEY_9"

# Channel
KEY_CHANNEL_UP = "KEY_CHANNELUP"
KEY_CHANNEL_DOWN = "KEY_CHANNELDOWN"
KEY_CHANNEL_DOT = "KEY_CHANNELDOT"

# Color Buttons
KEY_RED = "KEY_RED"
KEY_GREEN = "KEY_GREEN"
KEY_YELLOW = "KEY_YELLOW"
KEY_BLUE = "KEY_BLUE"

# Extras
KEY_SUBTITLE = "KEY_SUBTITLE"
KEY_INFO = "KEY_INFO"

# Mouse/Pointer Mode (from APK)
KEY_LEFT_MOUSE = "KEY_LEFTMOUSEKEYS"
KEY_UDD_LEFT_MOUSE = "KEY_UDDLEFTMOUSEKEYS"
KEY_UDU_LEFT_MOUSE = "KEY_UDULEFTMOUSEKEYS"
KEY_ZOOM_IN = "KEY_ZOOMIN"
KEY_ZOOM_OUT = "KEY_ZOOMOUT"

# All keys for reference
ALL_KEYS = [
    # Power
    KEY_POWER,
    # Navigation
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_OK_LONG_PRESS,
    # Menu/Back
    KEY_MENU, KEY_BACK, KEY_EXIT, KEY_HOME,
    # Volume
    KEY_VOLUME_UP, KEY_VOLUME_DOWN, KEY_MUTE, KEY_MUTE_LONG_PRESS,
    # Voice
    KEY_VOICE_UP, KEY_VOICE_DOWN,
    # Playback
    KEY_PLAY, KEY_PAUSE, KEY_STOP, KEY_FAST_FORWARD, KEY_REWIND,
    # Numbers
    KEY_0, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9,
    # Channel
    KEY_CHANNEL_UP, KEY_CHANNEL_DOWN, KEY_CHANNEL_DOT,
    # Color buttons
    KEY_RED, KEY_GREEN, KEY_YELLOW, KEY_BLUE,
    # Extras
    KEY_SUBTITLE, KEY_INFO,
    # Mouse/Pointer
    KEY_LEFT_MOUSE, KEY_UDD_LEFT_MOUSE, KEY_UDU_LEFT_MOUSE, KEY_ZOOM_IN, KEY_ZOOM_OUT,
]

# Key name mapping for CLI
KEY_NAME_MAP = {
    "power": KEY_POWER,
    "up": KEY_UP,
    "down": KEY_DOWN,
    "left": KEY_LEFT,
    "right": KEY_RIGHT,
    "ok": KEY_OK,
    "enter": KEY_OK,
    "select": KEY_OK,
    "ok_long": KEY_OK_LONG_PRESS,
    "menu": KEY_MENU,
    "back": KEY_BACK,
    "return": KEY_BACK,
    "exit": KEY_EXIT,
    "home": KEY_HOME,
    "volumeup": KEY_VOLUME_UP,
    "volup": KEY_VOLUME_UP,
    "vol+": KEY_VOLUME_UP,
    "volumedown": KEY_VOLUME_DOWN,
    "voldown": KEY_VOLUME_DOWN,
    "vol-": KEY_VOLUME_DOWN,
    "mute": KEY_MUTE,
    "mute_long": KEY_MUTE_LONG_PRESS,
    "voiceup": KEY_VOICE_UP,
    "voicedown": KEY_VOICE_DOWN,
    "play": KEY_PLAY,
    "pause": KEY_PAUSE,
    "stop": KEY_STOP,
    "forward": KEY_FAST_FORWARD,
    "ff": KEY_FAST_FORWARD,
    "rewind": KEY_REWIND,
    "rw": KEY_REWIND,
    "0": KEY_0,
    "1": KEY_1,
    "2": KEY_2,
    "3": KEY_3,
    "4": KEY_4,
    "5": KEY_5,
    "6": KEY_6,
    "7": KEY_7,
    "8": KEY_8,
    "9": KEY_9,
    "channelup": KEY_CHANNEL_UP,
    "chup": KEY_CHANNEL_UP,
    "ch+": KEY_CHANNEL_UP,
    "channeldown": KEY_CHANNEL_DOWN,
    "chdown": KEY_CHANNEL_DOWN,
    "ch-": KEY_CHANNEL_DOWN,
    "channeldot": KEY_CHANNEL_DOT,
    "dot": KEY_CHANNEL_DOT,
    "red": KEY_RED,
    "green": KEY_GREEN,
    "yellow": KEY_YELLOW,
    "blue": KEY_BLUE,
    "subtitle": KEY_SUBTITLE,
    "sub": KEY_SUBTITLE,
    "info": KEY_INFO,
    "zoomin": KEY_ZOOM_IN,
    "zoom+": KEY_ZOOM_IN,
    "zoomout": KEY_ZOOM_OUT,
    "zoom-": KEY_ZOOM_OUT,
    "mouse": KEY_LEFT_MOUSE,
}


def get_key(name: str) -> str:
    """Get key constant from friendly name.

    Args:
        name: Key name (e.g., 'up', 'volumeup', 'power')

    Returns:
        Key constant string (e.g., 'KEY_UP')
    """
    name_lower = name.lower().strip()

    # Check name map first
    if name_lower in KEY_NAME_MAP:
        return KEY_NAME_MAP[name_lower]

    # Try with KEY_ prefix
    key_name = f"KEY_{name.upper()}"
    if key_name in ALL_KEYS:
        return key_name

    # Return as-is if already a KEY_ constant
    if name.startswith("KEY_"):
        return name

    return key_name
