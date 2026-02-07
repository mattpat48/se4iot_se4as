import time
import os
import paho.mqtt.client as mqtt
from datastructure import SensorData

# Load environment variables
mqtt_broker = os.getenv("MQTT_BROKER", "mosquitto")
influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
influx_org = os.getenv("INFLUXDB_ORG", "iot_org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "iot_bucket")

print(f"Analyzer container started. Connecting to {mqtt_broker}...", flush=True)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}", flush=True)
    client.subscribe("sensors/data")

def on_message(client, userdata, msg):
    try:
        # Decoding using pre-defined structure
        payload_str = msg.payload.decode()
        data = SensorData.from_json(payload_str)
        
        print(f"Analyzing: {data.sensorid} -> {data.value:.2f}", flush=True)

        # Alert logic based on value thresholds
        ALERT_THRESHOLD = 25.0
        
        if data.value > ALERT_THRESHOLD:
            alert_msg = f"⚠️ ALERT: {data.sensorid} detected value {data.value:.2f} (Threshold: {ALERT_THRESHOLD})"
            # Post alert to MQTT topic for Node-RED to pick up
            client.publish("analyzer/alerts", alert_msg)
            print(f"!!! ALERT SENT: {alert_msg}", flush=True)
            
    except Exception as e:
        print(f"Error processing message: {e}", flush=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)

client.loop_forever()