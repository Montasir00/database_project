import os
import paho.mqtt.client as mqtt
import json
import time
import random
import keyboard
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MQTT Broker credentials
broker = os.getenv('MQTT_BROKER_URL')
port = int(os.getenv('MQTT_PORT', 8883))  # Default to 8883 if not set
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

# Data generation interval
DATA_GENERATION_INTERVAL = float(os.getenv('DATA_GENERATION_INTERVAL', 5))

# MQTT topics
TOPIC_SOIL_MOISTURE = 'sensors/soil_moisture'
TOPIC_PH = 'sensors/ph'
TOPIC_TEMPERATURE = 'sensors/temperature'
TOPIC_HUMIDITY = 'sensors/humidity'
TOPIC_LIGHT = 'sensors/light'
TOPIC_NUTRIENT = 'sensors/nutrient'

# Function to get the current time
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

# Sensor data generation functions
def generate_soil_moisture_data():
    return {"timestamp": get_time(), "moisture_level": round(random.uniform(0, 100), 2)}

def generate_ph_data():
    return {"timestamp": get_time(), "ph_level": round(random.uniform(4, 8), 2)}

def generate_temperature_data():
    return {"timestamp": get_time(), "temperature": round(random.uniform(-10, 50), 2)}

def generate_humidity_data():
    return {"timestamp": get_time(), "humidity": round(random.uniform(0, 100), 2)}

def generate_light_data():
    return {"timestamp": get_time(), "light_level": round(random.uniform(0, 100), 2)}

def generate_nutrient_data():
    return {"timestamp": get_time(), "nutrient_level": round(random.uniform(0, 100), 2)}

# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print(f"Connection failed with code {rc}")

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(username, password)
client.tls_set()  # Enable TLS for secure connection
client.connect(broker, port, 60)
client.loop_start()

# Data generation control
generating_data = False

# Function to toggle data generation
def toggle_data_generation():
    global generating_data
    generating_data = not generating_data
    if generating_data:
        print("Data generation started. Press 's' to stop.")
    else:
        print("Data generation stopped. Press 'g' to start.")


keyboard.on_press_key('g', lambda _: toggle_data_generation() if not generating_data else None)
keyboard.on_press_key('s', lambda _: toggle_data_generation() if generating_data else None)

print("Press 'g' to start data generation, 's' to stop, and 'q' to quit.")

# Main loop for generating and publishing data
try:
    while True:
        if generating_data:
            soil_moisture_data = generate_soil_moisture_data()
            client.publish(TOPIC_SOIL_MOISTURE, json.dumps(soil_moisture_data))
            print(f"Published to {TOPIC_SOIL_MOISTURE}: {soil_moisture_data}")
            
            ph_data = generate_ph_data()
            client.publish(TOPIC_PH, json.dumps(ph_data))
            print(f"Published to {TOPIC_PH}: {ph_data}")
            
            temperature_data = generate_temperature_data()
            client.publish(TOPIC_TEMPERATURE, json.dumps(temperature_data))
            print(f"Published to {TOPIC_TEMPERATURE}: {temperature_data}")
            
            humidity_data = generate_humidity_data()
            client.publish(TOPIC_HUMIDITY, json.dumps(humidity_data))
            print(f"Published to {TOPIC_HUMIDITY}: {humidity_data}")
            
            light_data = generate_light_data()
            client.publish(TOPIC_LIGHT, json.dumps(light_data))
            print(f"Published to {TOPIC_LIGHT}: {light_data}")
            
            nutrient_data = generate_nutrient_data()
            client.publish(TOPIC_NUTRIENT, json.dumps(nutrient_data))
            print(f"Published to {TOPIC_NUTRIENT}: {nutrient_data}")
            
            time.sleep(DATA_GENERATION_INTERVAL)  
        else:
            time.sleep(0.1)

        # Check for quit key
        if keyboard.is_pressed('q'):
            print("Quitting...")
            break

except KeyboardInterrupt:
    print("Publisher stopped")

finally:
    client.loop_stop()
    client.disconnect()