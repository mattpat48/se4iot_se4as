import time
import os
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime

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
    data = {
        "sensorid": "sensor_01",
        "value": random.uniform(10.0, 30.0),
        "timestamp": datetime.now().isoformat()
    }
    
    payload = json.dumps(data)
    client.publish("sensors/data", payload)
    print(f"Published: {payload}", flush=True)
    
    time.sleep(5)