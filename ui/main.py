import streamlit as st
import paho.mqtt.client as mqtt
import json
import os
import time
import datastructure as ds

# Environment Variables
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USERNAME", "admin")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "adminpassword123")
RESTORE_SESSION = os.getenv("RESTORE_SESSION", "true").lower() == "true"

st.set_page_config(page_title="IoT Control Panel", layout="wide")
st.title("🎛️ IoT System Control Panel")

# --- MQTT Connection ---
@st.cache_resource
def get_mqtt_client():
    client = mqtt.Client()
    # Storage for incoming retained configs
    client.external_config = {}

    def on_message(c, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic == "City/update/locations":
                c.external_config["locations"] = payload.get("locations")
            elif msg.topic == "City/update/config":
                if "sensor_params" in payload:
                    c.external_config["sensor_params"] = payload["sensor_params"]
                if "sensors_per_type" in payload:
                    c.external_config["sensors_per_type"] = payload["sensors_per_type"]
            elif msg.topic == "City/update/thresholds":
                c.external_config["thresholds"] = payload.get("thresholds")
        except Exception:
            pass
    
    client.on_message = on_message

    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe("City/update/#")
        client.loop_start()
        if RESTORE_SESSION:
            time.sleep(0.5) # Wait for retained messages
        return client
    except Exception as e:
        st.error(f"Could not connect to MQTT Broker: {e}")
        return None

client = get_mqtt_client()

def get_initial_config(key, default_val):
    if RESTORE_SESSION and client and hasattr(client, 'external_config'):
        val = client.external_config.get(key)
        if val is not None:
            return val
    return default_val

# --- Session State Initialization ---
if 'sensor_params' not in st.session_state:
    st.session_state.sensor_params = get_initial_config('sensor_params', list(ds.SENSOR_PARAMS))
if 'sensors_per_type' not in st.session_state:
    st.session_state.sensors_per_type = get_initial_config('sensors_per_type', ds.SENSORS_PER_TYPE)
if 'thresholds' not in st.session_state:
    st.session_state.thresholds = get_initial_config('thresholds', dict(ds.THRESHOLDS))
if 'locations_list' not in st.session_state:
    st.session_state.locations_list = get_initial_config('locations', list(ds.LOCATIONS))

# --- UI Layout ---

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📍 Location Management")
    st.info("Edit the list of locations where sensors are deployed.")
    
    # Locations from session state
    default_locs = ", ".join(st.session_state.locations_list)
    locations_input = st.text_area("Locations (comma separated)", value=default_locs)
    
    if st.button("Update Locations"):
        loc_list = [x.strip() for x in locations_input.split(',') if x.strip()]
        st.session_state.locations_list = loc_list
        payload = {"locations": loc_list}
        if client:
            client.publish("City/update/locations", json.dumps(payload), retain=True, qos=1)
            st.success(f"Sent update for {len(loc_list)} locations!")

with col2:
    st.subheader("⚠️ Threshold Configuration")
    st.info("Adjust the alert thresholds for the Analyzer.")

    new_thresholds = {}

    # Dynamically generate sliders for each sensor type
    for param in st.session_state.sensor_params:
        t_type = param["type"]
        t_unit = param["unit"]
        
        # Get current value or default to 80% of max value
        current_val = st.session_state.thresholds.get(t_type, param["max_v"] * 0.8)
        
        # Create slider
        val = st.slider(
            f"{t_type} ({t_unit})", 
            min_value=0.0, 
            max_value=float(param["max_v"]) * 1.5, 
            value=float(current_val),
            key=f"thresh_{t_type}"
        )
        new_thresholds[t_type] = val

    if st.button("Update Thresholds"):
        st.session_state.thresholds.update(new_thresholds)
        payload = {
            "thresholds": new_thresholds
        }
        if client:
            client.publish("City/update/thresholds", json.dumps(payload), retain=True, qos=1)
            st.success("Thresholds updated successfully!")

with col3:
    st.subheader("⚙️ Sensor Configuration")
    st.info("Add new sensor types and configure density.")

    # Sensors per Type
    st.session_state.sensors_per_type = st.number_input("Sensors per Type per Location", min_value=1, value=st.session_state.sensors_per_type)

    # Add New Sensor Type
    with st.expander("Add New Sensor Type"):
        new_type = st.text_input("Type Name (e.g., pressure)")
        new_unit = st.text_input("Unit (e.g., hPa)")
        new_min = st.number_input("Min Value", value=0.0)
        new_max = st.number_input("Max Value", value=100.0)
        new_vol = st.number_input("Volatility", value=1.0)
        
        if st.button("Add Sensor Type"):
            if new_type and new_unit:
                new_param = {
                    "type": new_type, "unit": new_unit, 
                    "min_v": new_min, "max_v": new_max, "volatility": new_vol
                }
                st.session_state.sensor_params.append(new_param)
                st.success(f"Added {new_type}!")

    # Display current types
    st.write("Current Types:", [p['type'] for p in st.session_state.sensor_params])

    if st.button("Update Sensor Config"):
        payload = {
            "sensor_params": st.session_state.sensor_params,
            "sensors_per_type": st.session_state.sensors_per_type
        }
        if client:
            client.publish("City/update/config", json.dumps(payload), retain=True, qos=1)
            st.success("Sensor configuration updated!")

# --- System Status ---
st.divider()
st.subheader("System Status")
if client:
    st.success(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
else:
    st.error("Disconnected from MQTT Broker")

st.caption("Changes sent via MQTT topic 'City/update'. Ensure Sensors and Analyzer containers are running.")