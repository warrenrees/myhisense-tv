# Configuration Reference

Complete reference for hisense2mqtt configuration.

## Configuration File

The configuration file is YAML format. Default search locations (in order):

1. Path specified with `--config` argument
2. `./config.yaml` (current directory)
3. `/app/config.yaml` (Docker container)
4. `~/.config/hisense2mqtt/config.yaml`
5. `/etc/hisense2mqtt/config.yaml`

## Full Configuration Example

```yaml
# MQTT Broker Connection
mqtt:
  host: "192.168.1.100"
  port: 1883
  username: "mqtt_user"
  password: "mqtt_pass"
  discovery_prefix: "homeassistant"
  client_id: "hisense2mqtt"

# Hisense TV Connection
tv:
  host: "10.0.0.194"
  port: 36669
  mac: "84:C8:A0:C0:CE:8F"
  uuid: "b5:50:f8:3b:d3:5f"
  name: "Living Room TV"
  brand: "his"

# Bridge Options
options:
  poll_interval: 30
  wake_on_lan: true
  discovery: true
  reconnect_interval: 30
  log_level: "INFO"
```

## MQTT Section

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | `localhost` | MQTT broker hostname or IP |
| `port` | int | `1883` | MQTT broker port |
| `username` | string | `null` | MQTT username (optional) |
| `password` | string | `null` | MQTT password (optional) |
| `discovery_prefix` | string | `homeassistant` | Home Assistant discovery prefix |
| `client_id` | string | `hisense2mqtt` | MQTT client identifier |

### MQTT Authentication

For brokers requiring authentication:

```yaml
mqtt:
  host: "192.168.1.100"
  username: "hisense"
  password: "secretpassword"
```

### MQTT TLS/SSL

TLS support for the broker connection is not yet implemented. For secure connections, use a VPN or ensure your broker is on a trusted network.

## TV Section

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `host` | string | - | **Yes** | TV IP address |
| `port` | int | `36669` | No | TV MQTT port |
| `mac` | string | `null` | No | TV MAC address for WoL |
| `uuid` | string | - | **Yes** | Paired device UUID |
| `name` | string | `Hisense TV` | No | Display name in HA |
| `brand` | string | `his` | No | Brand identifier |

### Finding Your TV's IP

1. Check your router's DHCP lease table
2. Use the Vidaa app to see the TV's IP
3. Use network scanning: `nmap -sn 192.168.1.0/24`

**Recommendation**: Set a static IP for your TV in your router's settings.

### Getting the UUID

The UUID is from a device paired with the TV:

1. Install the official **Vidaa** app
2. Connect to your TV and enter the PIN
3. Find your phone's MAC address in settings
4. Use that MAC as the UUID

Or capture it from logcat:
```bash
adb logcat | grep -i uuid
```

### MAC Address for Wake-on-LAN

Find the TV's MAC address:

1. TV Settings > Network > Network Status
2. Router's connected devices list
3. `arp -a` command when TV is on

## Options Section

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `poll_interval` | int | `30` | State polling interval (seconds) |
| `wake_on_lan` | bool | `true` | Enable Wake-on-LAN |
| `discovery` | bool | `true` | Publish HA MQTT discovery |
| `reconnect_interval` | int | `30` | Reconnection attempt interval |
| `log_level` | string | `INFO` | Logging level |

### Log Levels

- `DEBUG` - Verbose logging (MQTT messages, state changes)
- `INFO` - Normal operation logging
- `WARNING` - Warnings only
- `ERROR` - Errors only

## Environment Variables

All configuration can be overridden via environment variables:

| Variable | Config Path | Example |
|----------|-------------|---------|
| `MQTT_HOST` | `mqtt.host` | `192.168.1.100` |
| `MQTT_PORT` | `mqtt.port` | `1883` |
| `MQTT_USERNAME` | `mqtt.username` | `user` |
| `MQTT_PASSWORD` | `mqtt.password` | `pass` |
| `TV_HOST` | `tv.host` | `10.0.0.194` |
| `TV_PORT` | `tv.port` | `36669` |
| `TV_MAC` | `tv.mac` | `84:C8:A0:C0:CE:8F` |
| `TV_UUID` | `tv.uuid` | `b5:50:f8:3b:d3:5f` |
| `TV_NAME` | `tv.name` | `Living Room TV` |
| `POLL_INTERVAL` | `options.poll_interval` | `30` |
| `LOG_LEVEL` | `options.log_level` | `DEBUG` |

### Docker Environment Example

```yaml
# docker-compose.yaml
services:
  hisense2mqtt:
    environment:
      - MQTT_HOST=192.168.1.100
      - MQTT_USERNAME=mqtt_user
      - MQTT_PASSWORD=mqtt_pass
      - TV_HOST=10.0.0.194
      - TV_UUID=b5:50:f8:3b:d3:5f
      - LOG_LEVEL=DEBUG
```

## Validation

Validate your configuration:

```bash
python -m hisense2mqtt --validate --config config.yaml
```

Output:
```
Configuration is valid
  MQTT Broker: 192.168.1.100:1883
  TV Host: 10.0.0.194:36669
  TV Name: Living Room TV
  TV UUID: b5:50:f8:3b:d3:5f
  TV MAC: 84:C8:A0:C0:CE:8F
  Poll Interval: 30s
  Discovery: True
  Wake-on-LAN: True
```

## Multiple TVs

To control multiple TVs, run multiple instances with different configs:

```bash
# TV 1
docker compose -f docker-compose.tv1.yaml up -d

# TV 2
docker compose -f docker-compose.tv2.yaml up -d
```

Each instance needs:
- Unique `mqtt.client_id`
- Different `tv.host` and `tv.uuid`
- Separate config file
