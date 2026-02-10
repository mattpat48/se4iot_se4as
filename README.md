# IoT Project Setup

## Prerequisites
- Docker
- Docker Compose

## Installation & Setup

### Set Permissions
Docker volumes on Linux map to the host filesystem. We need to set the correct ownership for the containers to write to these folders.

Run these commands in the project root directory:

```bash
# Grafana runs as user 472
sudo chown -R 472:472 grafana/data

# Node-RED runs as user 1000
sudo chown -R 1000:1000 nodered/data

# Mosquitto runs as user 1883
sudo chown -R 1883:1883 mosquitto/

# InfluxDB runs as user 1000
sudo chown -R 1000:1000 influxdb/
```

## Launch Project

To start the stack:
```bash
sudo docker-compose up -d --remove-orphans
```

## Monitorate logs

To watch the logs of the singles containers, simply type:
```bash
sudo docker-compose logs -f [name]
```
where name corresponds to the name listed in the `docker-compose.yml` file.

## Monitorate Alerts

To follow the alerts of the system, simply join the Telegram channel [@mpga_alert_channel](https://t.me/mpga_alert_channel).

## Manipulate Sensors and Locations

To add/remove sensors and locations from the code, simply edit the `datastructure.py`:
- to add locations, simply insert a new entry to the `LOCATIONS` array
```python
LOCATIONS = ["Road", "Square", "Park"] # Default locations
```
- to add sensors, create a new `@dataclass` and add the default parameters, then configure the threshold (note that minVal, maxVal vold and threshold should be float values)
```python
@dataclass
class NewSensorData(SensorData):
    type: str = "sensor_data_name"
    unit: str = "sensor_unit"

SENSOR_PARAMS = [
	...
	{"data_cls": NewSensorData, "min_v": minVal, "max_v": maxVal, "volatility": vol, "topic_type": "type"},
]

THRESHOLDS = [
	...
	"type": threshold
]
```
- to add more sensors per location, simply edit the SENSOR_PER_TYPE value
```python
SENSOR_PER_TYPE = 1 # Default number is 1, so each location has only one sensor per parameter to measure
```