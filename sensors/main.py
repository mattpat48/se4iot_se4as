import time
import os
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime
from datastructure import (
    SensorData, LOCATIONS, SENSOR_PARAMS, SENSORS_PER_TYPE, LOCATION_COORDS
)

# Load environment variables
mqtt_broker = os.getenv("MQTT_BROKER", "mosquitto")
mqtt_user = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
influx_org = os.getenv("INFLUXDB_ORG", "iot_org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "iot_bucket")
restore_session = os.getenv("RESTORE_SESSION", "true").lower() == "true"

print(f"Sensors container started. Connecting to {mqtt_broker}...", flush=True)

# Global variables for dynamic configuration
current_locations = list(LOCATIONS)
sensors = []
current_sensor_params = list(SENSOR_PARAMS)
current_sensors_per_type = SENSORS_PER_TYPE
current_location_coords = dict(LOCATION_COORDS)

# Emergency state
active_emergency = None  # {"type": ..., "location": ..., "effects": {...}, "active": True}

def generate_sensors():
    global sensors, current_locations
    new_sensors = []
    sensor_count = 1
    print(f"Regenerating sensors for locations: {current_locations}", flush=True)
    
    for loc in current_locations:
        for param in current_sensor_params:
            for _ in range(current_sensors_per_type):
                new_sensors.append(SimulatedSensor(
                    sensor_count,
                    loc,
                    param["type"],
                    param["unit"],
                    param["min_v"],
                    param["max_v"],
                    param["volatility"],
                ))
                sensor_count += 1
    sensors = new_sensors
    print(f"Total sensors active: {len(sensors)}", flush=True)
    active_types = set(s.type_name for s in sensors)
    print(f"Active Sensor Types: {active_types}", flush=True)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!", flush=True)
        client.subscribe([("City/update/locations", 1), ("City/update/config", 1), ("City/emergency", 1)])
    else:
        print(f"Failed to connect, return code {rc}", flush=True)

def on_message(client, userdata, msg):
    try:
        print(f"Received configuration update from {msg.topic} (Retained: {msg.retain})", flush=True)
        
        if not restore_session and msg.retain:
            print("Ignoring retained configuration as RESTORE_SESSION is false", flush=True)
            return
        
        if msg.topic == "City/emergency":
            global active_emergency
            payload = json.loads(msg.payload.decode())
            if payload.get("active", False):
                active_emergency = payload
                print(f"🚨 EMERGENCY ACTIVATED: {payload['type']} at {payload['location']}", flush=True)
            else:
                active_emergency = None
                print("✅ Emergency deactivated, returning to normal", flush=True)
            return
            
        if msg.topic == "City/update/locations":
            payload = json.loads(msg.payload.decode())
            if "locations" in payload:
                global current_locations
                current_locations = payload["locations"]
            if "location_coords" in payload:
                global current_location_coords
                current_location_coords = payload["location_coords"]
                print(f"Updated location coords: {current_location_coords}", flush=True)
            generate_sensors()
        elif msg.topic == "City/update/config":
            payload = json.loads(msg.payload.decode())
            global current_sensor_params, current_sensors_per_type
            if "sensor_params" in payload:
                current_sensor_params = payload["sensor_params"]
            if "sensors_per_type" in payload:
                current_sensors_per_type = int(payload["sensors_per_type"])
            generate_sensors()
    except Exception as e:
        print(f"Error processing config update: {e}", flush=True)

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

client.loop_start()

class SimulatedSensor:
    def __init__(self, id_num, location, type_name, unit, min_v, max_v, volatility):
        self.sensor_id = f"sensor_{id_num:02d}"
        self.location = location
        self.type_name = type_name
        self.unit = unit
        self.min_v = min_v
        self.max_v = max_v
        self.volatility = volatility
        # GPS coordinates from L'Aquila location mapping (dynamic)
        coords = current_location_coords.get(location, LOCATION_COORDS.get(location, {"lat": 42.35, "lon": 13.39}))
        self.lat = coords["lat"]
        self.lon = coords["lon"]
        # Starting value: sensors that naturally stay near zero (seismic, rain) start low
        if type_name in ("seismic", "rain_level"):
            self.value = random.uniform(min_v, min_v + volatility * 5)
        else:
            self.value = random.uniform(min_v, min_v + (max_v - min_v) * 0.5)

    def tick(self):
        # Seismic sensor: realistic micro-tremor model
        if self.type_name == "seismic":
            roll = random.random()
            if roll < 0.005:  # 0.5% chance — strong earthquake (4.0-7.0 Mw)
                self.value = random.uniform(4.0, 7.0)
            elif roll < 0.02:  # 1.5% chance — moderate event (2.0-4.0 Mw)
                self.value = random.uniform(2.0, 4.0)
            elif roll < 0.08:  # 6% chance — minor tremor (0.5-2.0 Mw)
                self.value = random.uniform(0.5, 2.0)
            else:  # 92% — background noise (0.0-0.5 Mw)
                self.value = random.uniform(0.0, 0.5)
        else:
            # More realistic generation: lower volatility usually, with occasional peaks
            if random.random() < 0.10:  # 10% chance of anomaly/peak
                # Peak event: significantly larger change
                change = random.uniform(-self.volatility * 3, self.volatility * 3)
            else:
                # Normal fluctuation: reduced volatility for smoother curves
                change = random.uniform(-self.volatility * 0.2, self.volatility * 0.2)

            # Mean reversion for sensors that naturally stay near minimum (rain)
            if self.type_name == "rain_level":
                change += (self.min_v - self.value) * 0.3

            self.value += change
            # Keep value within bounds
            self.value = max(self.min_v, min(self.value, self.max_v))
        
        # Emergency override: force extreme values if emergency is active at this location
        actual_value = self.value
        is_emergency = False
        if active_emergency and active_emergency.get("active", False):
            if active_emergency.get("location") == self.location:
                effects = active_emergency.get("effects", {})
                if self.type_name in effects:
                    # Gradually approach emergency value for realism
                    target = effects[self.type_name]
                    actual_value = target + random.uniform(-2.0, 2.0)
                    actual_value = max(self.min_v, actual_value)  # Clamp to min
                    is_emergency = True
        
        # Create data object
        data_obj = SensorData(
            sensorid=self.sensor_id,
            value=actual_value,
            timestamp=datetime.now().isoformat(),
            type=self.type_name,
            unit=self.unit,
            lat=self.lat,
            lon=self.lon
        )
        
        # Topic Logic: City/data/Location/DataType
        topic = f"City/data/{self.location}/{self.type_name}"
        return topic, data_obj.to_json()

# Initial generation
generate_sensors()

while True:
    try:
        for sensor in sensors:
            topic, payload = sensor.tick()
            client.publish(topic, payload, qos=1)
            print(f"[{topic}] {payload}", flush=True)
    except Exception as e:
        print(f"Error in generation loop: {e}", flush=True)
        
    time.sleep(10)