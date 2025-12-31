# MQTT Topics Reference

Complete reference for all MQTT topics used by hisense2mqtt.

## Topic Structure

```
hisense2mqtt/{device_id}/{direction}/{entity}
```

- `device_id` - Derived from TV IP (e.g., `10_0_0_194`)
- `direction` - `set` for commands, `state` for status
- `entity` - The specific control (power, volume, etc.)

## Command Topics (Publish)

### Power Control

**Topic:** `hisense2mqtt/{device_id}/set/power`

| Payload | Action |
|---------|--------|
| `ON` | Turn TV on (uses Wake-on-LAN if configured) |
| `OFF` | Turn TV off |

**Examples:**
```bash
# Turn on
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/power" -m "ON"

# Turn off
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/power" -m "OFF"
```

### Volume Control

**Topic:** `hisense2mqtt/{device_id}/set/volume`

| Payload | Description |
|---------|-------------|
| `0-100` | Volume level (integer) |

**Examples:**
```bash
# Set volume to 30
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/volume" -m "30"

# Mute (set to 0)
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/volume" -m "0"
```

### Mute Control

**Topic:** `hisense2mqtt/{device_id}/set/mute`

| Payload | Action |
|---------|--------|
| `ON` | Toggle mute (mutes if unmuted) |
| `OFF` | Toggle mute (unmutes if muted) |

**Example:**
```bash
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/mute" -m "ON"
```

### Source/Input Control

**Topic:** `hisense2mqtt/{device_id}/set/source`

| Payload | Input |
|---------|-------|
| `tv` | TV Tuner |
| `hdmi1` | HDMI 1 |
| `hdmi2` | HDMI 2 |
| `hdmi3` | HDMI 3 |
| `hdmi4` | HDMI 4 |
| `av` | AV/Composite |
| `component` | Component |

**Examples:**
```bash
# Switch to HDMI 1
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/source" -m "hdmi1"

# Switch to TV tuner
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/source" -m "tv"
```

### Remote Key Control

**Topic:** `hisense2mqtt/{device_id}/set/key`

Accepts key names with or without `KEY_` prefix (case-insensitive).

| Key | Aliases |
|-----|---------|
| `KEY_POWER` | `power` |
| `KEY_UP` | `up` |
| `KEY_DOWN` | `down` |
| `KEY_LEFT` | `left` |
| `KEY_RIGHT` | `right` |
| `KEY_OK` | `ok`, `enter` |
| `KEY_BACK` | `back` |
| `KEY_RETURNS` | `returns` |
| `KEY_HOME` | `home` |
| `KEY_MENU` | `menu` |
| `KEY_EXIT` | `exit` |
| `KEY_VOLUMEUP` | `volumeup`, `vol_up` |
| `KEY_VOLUMEDOWN` | `volumedown`, `vol_down` |
| `KEY_MUTE` | `mute` |
| `KEY_CHANNELUP` | `channelup`, `ch_up` |
| `KEY_CHANNELDOWN` | `channeldown`, `ch_down` |
| `KEY_0` - `KEY_9` | `0` - `9` |
| `KEY_PLAY` | `play` |
| `KEY_PAUSE` | `pause` |
| `KEY_STOP` | `stop` |
| `KEY_FORWARDS` | `forwards`, `ff` |
| `KEY_BACK` | `rewind`, `rw` |
| `KEY_RED` | `red` |
| `KEY_GREEN` | `green` |
| `KEY_YELLOW` | `yellow` |
| `KEY_BLUE` | `blue` |
| `KEY_INFO` | `info` |
| `KEY_SUBTITLE` | `subtitle` |

**Examples:**
```bash
# Navigate up
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/key" -m "up"

# Press OK
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/key" -m "KEY_OK"

# Open info overlay
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/key" -m "info"
```

### App Launch

**Topic:** `hisense2mqtt/{device_id}/set/app`

| Payload | App |
|---------|-----|
| `netflix` | Netflix |
| `youtube` | YouTube |
| `amazon` / `prime` | Amazon Prime Video |
| `disney` | Disney+ |
| `hulu` | Hulu |

**Examples:**
```bash
# Launch Netflix
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/app" -m "netflix"

# Launch YouTube
mosquitto_pub -h localhost -t "hisense2mqtt/10_0_0_194/set/app" -m "youtube"
```

## State Topics (Subscribe)

### Power State

**Topic:** `hisense2mqtt/{device_id}/state/power`

| Value | Meaning |
|-------|---------|
| `ON` | TV is on |
| `OFF` | TV is off |

### Volume State

**Topic:** `hisense2mqtt/{device_id}/state/volume`

| Value | Meaning |
|-------|---------|
| `0-100` | Current volume level |

### Mute State

**Topic:** `hisense2mqtt/{device_id}/state/mute`

| Value | Meaning |
|-------|---------|
| `ON` | TV is muted |
| `OFF` | TV is not muted |

### Source State

**Topic:** `hisense2mqtt/{device_id}/state/source`

| Value | Meaning |
|-------|---------|
| Source name | Current input source |

### Availability

**Topic:** `hisense2mqtt/{device_id}/state/available`

| Value | Meaning |
|-------|---------|
| `online` | Bridge connected to TV |
| `offline` | Bridge disconnected from TV |

## Home Assistant Discovery Topics

Discovery messages are published to:

```
{discovery_prefix}/{component}/hisense_{device_id}/{entity}/config
```

Default prefix is `homeassistant`.

### Examples

Media Player:
```
homeassistant/media_player/hisense_10_0_0_194/config
```

Navigation Button:
```
homeassistant/button/hisense_10_0_0_194_up/config
```

App Selector:
```
homeassistant/select/hisense_10_0_0_194_app/config
```

## Testing with mosquitto_sub

Subscribe to all state topics:
```bash
mosquitto_sub -h localhost -t "hisense2mqtt/+/state/#" -v
```

Subscribe to all topics:
```bash
mosquitto_sub -h localhost -t "hisense2mqtt/#" -v
```

Watch discovery messages:
```bash
mosquitto_sub -h localhost -t "homeassistant/#" -v
```

## Retained Messages

The following topics use retained messages:
- All `state/*` topics
- All `*/config` discovery topics
- `state/available` (also used as Last Will)

This ensures Home Assistant gets the current state on startup.
