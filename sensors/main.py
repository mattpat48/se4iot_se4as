import time
import os

# Load environment variables
mqtt_broker = os.getenv("MQTT_BROKER", "mosquitto")
influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
influx_org = os.getenv("INFLUXDB_ORG", "iot_org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "iot_bucket")

print(f"Sensor container started. Connecting to {mqtt_broker}...", flush=True)

while True:
    # Logic to generate data and publish to MQTT will go here
    # Example: client.publish("topic", payload)
    print("Simulating sensor data...", flush=True)
    time.sleep(5)