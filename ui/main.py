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

st.set_page_config(page_title="IoT Control Panel", layout="wide")
st.title("🎛️ IoT System Control Panel")

# --- MQTT Connection ---
@st.cache_resource
def get_mqtt_client():
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        return client
    except Exception as e:
        st.error(f"Could not connect to MQTT Broker: {e}")
        return None

client = get_mqtt_client()

# --- UI Layout ---

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📍 Location Management")
    st.info("Edit the list of locations where sensors are deployed.")
    
    # Default locations
    default_locs = "Road, Square, Park"
    locations_input = st.text_area("Locations (comma separated)", value=default_locs)
    
    if st.button("Update Locations"):
        loc_list = [x.strip() for x in locations_input.split(',') if x.strip()]
        payload = {"locations": loc_list}
        if client:
            client.publish("City/update/locations", json.dumps(payload), retain=True, qos=1)
            st.success(f"Sent update for {len(loc_list)} locations!")

with col2:
    st.subheader("⚠️ Threshold Configuration")
    st.info("Adjust the alert thresholds for the Analyzer.")

    # Threshold Inputs
    t_temp = st.slider("Temperature Threshold (°C)", 0.0, 50.0, 30.0)
    t_hum = st.slider("Humidity Threshold (%)", 0.0, 100.0, 80.0)
    t_air = st.slider("Air Quality Threshold (AQI)", 0.0, 500.0, 150.0)
    t_speed = st.slider("Traffic Speed Threshold (km/h)", 0.0, 150.0, 90.0)
    t_noise = st.slider("Noise Level Threshold (dB)", 0.0, 120.0, 85.0)

    if st.button("Update Thresholds"):
        payload = {
            "thresholds": {
                "temperature": t_temp,
                "humidity": t_hum,
                "co2": t_air,
                "traffic_speed": t_speed,
                "noise_level": t_noise
            }
        }
        if client:
            client.publish("City/update/thresholds", json.dumps(payload), retain=True, qos=1)
            st.success("Thresholds updated successfully!")

with col3:
    st.subheader("⚙️ Sensor Configuration")
    st.info("Add new sensor types and configure density.")

    # Initialize session state with defaults from datastructure.py
    if 'sensor_params' not in st.session_state:
        st.session_state.sensor_params = list(ds.SENSOR_PARAMS)
    if 'sensors_per_type' not in st.session_state:
        st.session_state.sensors_per_type = ds.SENSORS_PER_TYPE

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