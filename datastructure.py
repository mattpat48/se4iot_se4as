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
    lat: float = 45.4642  # Esempio: Latitudine (Milano)
    lon: float = 9.1900   # Esempio: Longitudine

    def to_json(self):
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)

# Data structures for specific sensor types
@dataclass
class AirQualityData(SensorData):
    type: str = "co2"
    unit: str = "ppm"

@dataclass
class AirHumidityData(SensorData):
    type: str = "humidity"
    unit: str = "%"

@dataclass
class TrafficSpeedData(SensorData):
    type: str = "traffic_speed"
    unit: str = "km/h"

@dataclass
class NoiseLevelData(SensorData):
    type: str = "noise_level"
    unit: str = "dB"

# Configuration Lists
LOCATIONS = ["Road", "Square", "Park"]

SENSOR_PARAMS = [
    {"data_cls": SensorData, "min_v": 15.0, "max_v": 35.0, "volatility": 0.5},
    {"data_cls": AirHumidityData, "min_v": 30.0, "max_v": 90.0, "volatility": 1.0},
    {"data_cls": AirQualityData, "min_v": 400.0, "max_v": 1200.0, "volatility": 10.0},
    {"data_cls": TrafficSpeedData, "min_v": 0.0, "max_v": 100.0, "volatility": 5.0},
    {"data_cls": NoiseLevelData, "min_v": 40.0, "max_v": 95.0, "volatility": 2.0},
]