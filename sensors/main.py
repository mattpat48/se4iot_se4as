import time
import os
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime
from datastructure import SensorData

# Load environment variables
mqtt_broker = os.getenv("MQTT_BROKER", "mosquitto")
influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
influx_org = os.getenv("INFLUXDB_ORG", "iot_org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "iot_bucket")

print(f"Analyzer container started. Connecting to {mqtt_broker}...", flush=True)

client = mqtt.Client()
client.connect(mqtt_broker, 1883, 60)

while True:
    # Generazione dati usando la struttura condivisa
    sensor_data = SensorData(
        sensorid="sensor_01",
        value=random.uniform(10.0, 35.0), # Aumentato range per testare alert
        timestamp=datetime.now().isoformat()
    )
    
    payload = sensor_data.to_json()
    client.publish("sensors/data", payload)
    print(f"Published: {payload}", flush=True)
    
    time.sleep(5)