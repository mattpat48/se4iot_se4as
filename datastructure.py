import json
from dataclasses import dataclass, asdict

@dataclass
class SensorData:
    sensorid: str
    value: float
    timestamp: str

    def to_json(self):
        """Converte l'oggetto in una stringa JSON."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str):
        """Crea un oggetto SensorData da una stringa JSON."""
        data = json.loads(json_str)
        return cls(**data)