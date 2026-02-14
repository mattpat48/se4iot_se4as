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

# Real GPS coordinates for L'Aquila, Italy
LOCATION_COORDS = {
    "Road": {"lat": 42.3498, "lon": 13.3995},      # Corso Vittorio Emanuele II
    "Square": {"lat": 42.3506, "lon": 13.3964},     # Piazza del Duomo
    "Park": {"lat": 42.3538, "lon": 13.3917},       # Parco del Castello
}

# Famous L'Aquila locations presets (selectable from UI)
LAQUILA_PRESETS = {
    "Parco del Castello":          {"lat": 42.3538, "lon": 13.3917},
    "Piazza del Duomo":            {"lat": 42.3506, "lon": 13.3964},
    "Fontana delle 99 Cannelle":   {"lat": 42.3472, "lon": 13.3988},
    "Basilica di Collemaggio":     {"lat": 42.3453, "lon": 13.4010},
    "Corso Vittorio Emanuele II":  {"lat": 42.3498, "lon": 13.3995},
    "Piazza del Palazzo":          {"lat": 42.3512, "lon": 13.3952},
    "Villa Comunale":              {"lat": 42.3525, "lon": 13.3942},
    "Forte Spagnolo":              {"lat": 42.3545, "lon": 13.3908},
    "Porta Napoli":                {"lat": 42.3462, "lon": 13.4002},
    "Piazza Santa Maria Paganica": {"lat": 42.3491, "lon": 13.3969},
    "Stazione FS L'Aquila":        {"lat": 42.3558, "lon": 13.3728},
    "Ospedale San Salvatore":      {"lat": 42.3672, "lon": 13.3563},
    "Università L'Aquila (Coppito)": {"lat": 42.3681, "lon": 13.3491},
}

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