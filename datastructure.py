import json
from dataclasses import dataclass, asdict

@dataclass
class SensorData:
    sensorid: str
    value: float
    timestamp: str
    # Additional metadata for Smart City context
    type: str = "temperature"
    unit: str = "°C"
    lat: float = 0.0
    lon: float = 0.0

    def to_json(self):
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)

# Configuration Lists
LOCATIONS = ["Road", "Square", "Park"]

SENSOR_PARAMS = [
    {"type": "temperature", "unit": "°C", "min_v": 15.0, "max_v": 35.0, "volatility": 0.5},
    {"type": "humidity", "unit": "%", "min_v": 30.0, "max_v": 90.0, "volatility": 1.0},
    {"type": "co2", "unit": "ppm", "min_v": 400.0, "max_v": 1200.0, "volatility": 10.0},
    {"type": "traffic_speed", "unit": "km/h", "min_v": 0.0, "max_v": 100.0, "volatility": 5.0},
    {"type": "noise_level", "unit": "dB", "min_v": 40.0, "max_v": 95.0, "volatility": 2.0},
]

SENSORS_PER_TYPE = 1 # Number of sensors per type per location (can be adjusted)

THRESHOLDS = {
    "temperature": 30.0,
    "humidity": 80.0,
    "co2": 1000.0,
    "traffic_speed": 80.0,
    "noise_level": 85.0
}