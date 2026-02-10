import time
import os
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime
from datastructure import (
    SensorData, AirQualityData, AirHumidityData, TrafficSpeedData, NoiseLevelData,
    LOCATIONS, SENSOR_PARAMS, SENSORS_PER_TYPE
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
    def __init__(self, id_num, location, data_cls, min_v, max_v, volatility, topic_type):
        self.sensor_id = f"sensor_{id_num:02d}"
        self.location = location
        self.data_cls = data_cls
        self.min_v = min_v
        self.max_v = max_v
        self.volatility = volatility
        self.value = random.uniform(min_v, max_v)
        self.topic_type = topic_type

    def tick(self):
        # Random walk with volatility
        change = random.uniform(-self.volatility, self.volatility)
        self.value += change
        # Keep value within bounds
        self.value = max(self.min_v, min(self.value, self.max_v))
        
        # Create data object
        data_obj = self.data_cls(
            sensorid=self.sensor_id,
            value=self.value,
            timestamp=datetime.now().isoformat()
        )
        
        # Topic Logic: City/data/Location/DataType
        topic = f"City/data/{self.location}/{self.topic_type}"
        return topic, data_obj.to_json()

# Sensor Generation Logic
sensors = []
sensor_count = 1

for loc in LOCATIONS:
    for param in SENSOR_PARAMS:
        for _ in range(SENSORS_PER_TYPE):
            sensors.append(SimulatedSensor(
                sensor_count,
                loc,
                param["data_cls"],
                param["min_v"],
                param["max_v"],
                param["volatility"],
                param["topic_type"]
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