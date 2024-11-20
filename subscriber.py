import os
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import mysql.connector
from neo4j import GraphDatabase
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database credentials
mongo_url = os.getenv('MONGO_URL', "mongodb://localhost:27017/")
mysql_host = os.getenv('MYSQL_HOST', "localhost")
mysql_user = os.getenv('MYSQL_USER', "root")
mysql_password = os.getenv('MYSQL_PASSWORD', "123456")
mysql_db = os.getenv('MYSQL_DB', "sensors_data")
neo4j_url = os.getenv('NEO4J_URL', "bolt://localhost:7687")
neo4j_user = os.getenv('NEO4J_USER', "neo4j")
neo4j_password = os.getenv('NEO4J_PASSWORD', "12345678")

# MQTT Broker credentials
broker = os.getenv('MQTT_BROKER_URL')
port = int(os.getenv('MQTT_PORT', 8883))
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

# MQTT topics
TOPIC_SOIL_MOISTURE = 'sensors/soil_moisture'
TOPIC_PH = 'sensors/ph'
TOPIC_TEMPERATURE = 'sensors/temperature'
TOPIC_HUMIDITY = 'sensors/humidity'
TOPIC_LIGHT = 'sensors/light'
TOPIC_NUTRIENT = 'sensors/nutrient'

# Database connections
mongo_conn = MongoClient(mongo_url)
mysql_conn = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_db
)
neo4j_conn = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

cursor = mysql_conn.cursor()

# Insert functions for MySQL
def insert_soil_moisture(cursor, data):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soil_moisture (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp VARCHAR(50),
            moisture_level FLOAT
        )
    """)
    cursor.execute("INSERT INTO soil_moisture (timestamp, moisture_level) VALUES (%s, %s)", (data['timestamp'], data['moisture_level']))
    mysql_conn.commit()

def insert_ph(cursor, data):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ph_level (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp VARCHAR(50),
            ph_level FLOAT
        )
    """)
    cursor.execute("INSERT INTO ph_level (timestamp, ph_level) VALUES (%s, %s)", (data['timestamp'], data['ph_level']))
    mysql_conn.commit()

# Insert functions for MongoDB
def insert_temperature(data):
    mongo_conn['environment_data']['temperature'].insert_one(data)

def insert_humidity(data):
    mongo_conn['environment_data']['humidity'].insert_one(data)

# Insert functions for Neo4j
def insert_light_level(data):
    with neo4j_conn.session() as session:
        session.run(
            "MERGE (l:Light {timestamp: $timestamp}) SET l.level = $level",
            timestamp=data['timestamp'], level=data['light_level']
        )

def insert_nutrient_level(data):
    with neo4j_conn.session() as session:
        session.run(
            "MERGE (n:Nutrient {timestamp: $timestamp}) SET n.level = $level",
            timestamp=data['timestamp'], level=data['nutrient_level']
        )

# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe([
            (TOPIC_SOIL_MOISTURE, 0), (TOPIC_PH, 0), (TOPIC_TEMPERATURE, 0), 
            (TOPIC_HUMIDITY, 0), (TOPIC_LIGHT, 0), (TOPIC_NUTRIENT, 0)
        ])
    else:
        print("Connection failed")

# Handle incoming messages
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    if msg.topic == TOPIC_SOIL_MOISTURE:
        insert_soil_moisture(cursor, data)
    elif msg.topic == TOPIC_PH:
        insert_ph(cursor, data)
    elif msg.topic == TOPIC_TEMPERATURE:
        insert_temperature(data)
    elif msg.topic == TOPIC_HUMIDITY:
        insert_humidity(data)
    elif msg.topic == TOPIC_LIGHT:
        insert_light_level(data)
    elif msg.topic == TOPIC_NUTRIENT:
        insert_nutrient_level(data)
    print(f"Received and stored data for {msg.topic}")

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()

client.connect(broker, port, 60)

# Start MQTT client loop
try:
    print("Subscriber started. Press Ctrl+C to stop.")
    client.loop_forever()
except KeyboardInterrupt:
    print("Subscriber stopped")
finally:
    client.disconnect()
    cursor.close()
    mysql_conn.close()
    neo4j_conn.close()
    mongo_conn.close()
