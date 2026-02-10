import time
import os
import paho.mqtt.client as mqtt
from datastructure import SensorData

# Load environment variables
mqtt_broker = os.getenv("MQTT_BROKER", "mosquitto")
mqtt_user = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
influx_org = os.getenv("INFLUXDB_ORG", "iot_org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "iot_bucket")

print(f"Analyzer container started. Connecting to {mqtt_broker}...", flush=True)

# Define thresholds for each sensor type
THRESHOLDS = {
    "temperature": 30.0,
    "humidity": 80.0,
    "co2": 1000.0,
    "traffic_speed": 80.0,
    "noise_level": 85.0
}

# Dictionary to track the alert state of each sensor: {sensor_id: bool}
active_alerts = {}

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}", flush=True)
    client.subscribe("City/#")

def on_message(client, userdata, msg):
    try:
        # Extract location from topic (City/Location/Type)
        topic_parts = msg.topic.split("/")
        location = topic_parts[2] if len(topic_parts) > 1 else "Unknown"

        # Decoding using pre-defined structure
        payload_str = msg.payload.decode()
        data = SensorData.from_json(payload_str)
        
        print(f"Analyzing: {data.sensorid} ({data.type}) -> {data.value:.2f}", flush=True)

        # Check threshold based on data type
        threshold = THRESHOLDS.get(data.type)
        
        if threshold is not None:
            is_alerting = active_alerts.get(data.sensorid, False)
            
            if data.value > threshold:
                if not is_alerting:
                    alert_msg = f"⚠️ ALERT: {data.sensorid} ({data.type}) at {location} detected {data.value:.2f} {data.unit} (Threshold: {threshold})"
                    client.publish(f"City/alerts/{location}/{data.type}", alert_msg, qos=1)
                    print(f"!!! ALERT SENT: {alert_msg}", flush=True)
                    active_alerts[data.sensorid] = True
            elif is_alerting:
                alert_msg = f"✅ RECOVERY: {data.sensorid} ({data.type}) at {location} returned to normal {data.value:.2f} {data.unit}"
                client.publish(f"City/alerts/{location}/{data.type}", alert_msg, qos=1)
                print(f"!!! RECOVERY SENT: {alert_msg}", flush=True)
                active_alerts[data.sensorid] = False
            
    except Exception as e:
        print(f"Error processing message: {e}", flush=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)

while True:
    try:
        client.connect(mqtt_broker, 1883, 60)
        break
    except Exception as e:
        print(f"Connection failed: {e}. Retrying in 5s...", flush=True)
        time.sleep(5)

client.loop_forever()