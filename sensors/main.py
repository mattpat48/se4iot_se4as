import time
import os
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime
from datastructure import (
    SensorData, AirQualityData, AirHumidityData, TrafficSpeedData, NoiseLevelData,
    LOCATIONS, SENSOR_PARAMS
)

# Load environment variables
mqtt_broker = os.getenv("MQTT_BROKER", "mosquitto")
mqtt_user = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
influx_org = os.getenv("INFLUXDB_ORG", "iot_org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "iot_bucket")

print(f"Sensors container started. Connecting to {mqtt_broker}...", flush=True)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!", flush=True)
    else:
        print(f"Failed to connect, return code {rc}", flush=True)

client = mqtt.Client()
client.on_connect = on_connect

if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)

while True:
    try:
        client.connect(mqtt_broker, 1883, 60)
        break
    except Exception as e:
        print(f"Connection failed: {e}. Retrying in 5s...", flush=True)
        time.sleep(5)

client.loop_start()

class SimulatedSensor:
    def __init__(self, id_num, location, data_cls, min_v, max_v, volatility):
        self.sensor_id = f"sensor_{id_num:02d}"
        self.location = location
        self.data_cls = data_cls
        self.min_v = min_v
        self.max_v = max_v
        self.volatility = volatility
        self.value = random.uniform(min_v, max_v)
        
        # Determina il tipo per il topic basandosi sulla classe
        if data_cls == SensorData: self.topic_type = "temperature"
        elif data_cls == AirHumidityData: self.topic_type = "humidity"
        elif data_cls == AirQualityData: self.topic_type = "co2"
        elif data_cls == TrafficSpeedData: self.topic_type = "traffic"
        elif data_cls == NoiseLevelData: self.topic_type = "noise"

    def tick(self):
        # Logica Random Walk: varia il valore gradualmente
        change = random.uniform(-self.volatility, self.volatility)
        self.value += change
        # Mantiene il valore entro i limiti realistici
        self.value = max(self.min_v, min(self.value, self.max_v))
        
        # Crea l'oggetto dati
        data_obj = self.data_cls(
            sensorid=self.sensor_id,
            value=self.value,
            timestamp=datetime.now().isoformat()
        )
        
        # Topic gerarchico: City/Location/DataType
        topic = f"City/data/{self.location}/{self.topic_type}"
        return topic, data_obj.to_json()

# Inizializzazione Sensori per ogni Location
sensors = []
sensor_count = 1

for loc in LOCATIONS:
    for param in SENSOR_PARAMS:
        sensors.append(SimulatedSensor(
            sensor_count,
            loc,
            param["data_cls"],
            param["min_v"],
            param["max_v"],
            param["volatility"]
        ))
        sensor_count += 1

while True:
    try:
        for sensor in sensors:
            topic, payload = sensor.tick()
            client.publish(topic, payload, qos=1)
            print(f"[{topic}] {payload}", flush=True)
    except Exception as e:
        print(f"Error in generation loop: {e}", flush=True)
        
    time.sleep(5)