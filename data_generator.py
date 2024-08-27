import time
import random
import os
import paho.mqtt.client as mqtt
import mysql.connector
from pymongo import MongoClient
from py2neo import Graph

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.connect("mqtt", 1883, 60) 

# MySQL setup
mysql_conn = mysql.connector.connect(
    host=os.environ.get('MYSQL_HOST', 'mysql'),
    user=os.environ.get('MYSQL_USER', 'root'),
    password=os.environ.get('MYSQL_PASSWORD', 'secret'),
    database=os.environ.get('MYSQL_DATABASE', 'test')
)
mysql_cursor = mysql_conn.cursor()

# MongoDB setup
mongo_client = MongoClient("mongodb://mongo:27017/")  
mongo_db = mongo_client["iot_data"]

# Neo4j setup
neo4j_graph = Graph("bolt://neo4j:7687", auth=("neo4j", "password"))  

def generate_data():
    soil_moisture = random.uniform(0, 100)
    temperature = random.uniform(0, 40)
    light = random.uniform(0, 1000)
    humidity = random.uniform(0, 100)
    ph = random.uniform(0, 14)
    nutrient_levels = random.uniform(0, 100)

    return soil_moisture, temperature, light, humidity, ph, nutrient_levels

def publish_data(topic, data):
    mqtt_client.publish(topic, str(data))

def store_mysql_data(data_type, value):
    query = f"INSERT INTO {data_type} (value, timestamp) VALUES (%s, NOW())"
    mysql_cursor.execute(query, (value,))
    mysql_conn.commit()

def store_mongodb_data(data_type, value):
    mongo_db[data_type].insert_one({"value": value, "timestamp": time.time()})

def store_neo4j_data(data_type, value):
    neo4j_graph.run(f"CREATE (d:{data_type} {{value: $value, timestamp: timestamp()}})", value=value)


mysql_cursor.execute("""
CREATE TABLE IF NOT EXISTS soil_moisture (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value FLOAT,
    timestamp DATETIME
)
""")
mysql_cursor.execute("""
CREATE TABLE IF NOT EXISTS ph (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value FLOAT,
    timestamp DATETIME
)
""")
mysql_conn.commit()

while True:
    soil_moisture, temperature, light, humidity, ph, nutrient_levels = generate_data()

    # Publish to MQTT
    publish_data("soil_moisture", soil_moisture)
    publish_data("temperature", temperature)
    publish_data("light", light)
    publish_data("humidity", humidity)
    publish_data("ph", ph)
    publish_data("nutrient_levels", nutrient_levels)

    # Store in databases
    store_mysql_data("soil_moisture", soil_moisture)
    store_mysql_data("ph", ph)
    store_mongodb_data("temperature", temperature)
    store_mongodb_data("humidity", humidity)
    store_neo4j_data("light", light)
    store_neo4j_data("nutrient_levels", nutrient_levels)

    time.sleep(5)  # Generate data every 5 seconds
