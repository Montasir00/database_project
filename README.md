# IoT Sensor Data Collection System

A distributed system for collecting and storing IoT sensor data across multiple databases using MQTT protocol. The system simulates various environmental sensors and stores their data in different database systems for optimized data handling and analysis.

## Features

- Real-time sensor data simulation for:
  - Soil Moisture
  - pH Levels
  - Temperature
  - Humidity
  - Light Levels
  - Nutrient Levels
- MQTT-based publish/subscribe architecture
- Multi-database storage strategy:
  - MySQL for soil moisture and pH data
  - MongoDB for temperature and humidity data
  - Neo4j for light and nutrient levels

## Prerequisites

- Docker
- Python 3.x (for local development)

## Installation

1. Clone the repository:
```bash
https://github.com/Montasir00/database_project.git
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Container Setup

### MySQL Container
```bash
# Create and run MySQL container
docker run -d \
  --name iot_mysql \
  -e MYSQL_ROOT_PASSWORD=your_mysql_password \
  -e MYSQL_DATABASE=sensors_data \
  -p 3306:3306 \
  mysql:8.0

# Verify MySQL container is running
docker ps | grep iot_mysql
```

### MongoDB Container
```bash
# Create and run MongoDB container
docker run -d \
  --name iot_mongodb \
  -p 27017:27017 \
  mongo:latest

# Verify MongoDB container is running
docker ps | grep iot_mongodb
```

### Neo4j Container
```bash
# Create and run Neo4j container
docker run -d \
  --name iot_neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_neo4j_password \
  neo4j:latest

# Verify Neo4j container is running
docker ps | grep iot_neo4j
```

### HiveMQ MQTT Broker Setup

This project uses the free HiveMQ Cloud service for MQTT communication. Follow these steps to set up your MQTT broker:

1. **Create an Account on HiveMQ Cloud**:
   - Visit [HiveMQ Cloud](https://www.hivemq.com/mqtt-cloud-broker/) and sign up for a free account.
   - Log in to your HiveMQ dashboard and create a new MQTT broker instance.

2. **Obtain Connection Details**:
   - After creating the broker instance, note down the following details from your HiveMQ dashboard:
     - **Broker URL**
     - **Port** (Use `8883` for secure communication)
     - **Username** and **Password**

3. **Configure the `.env` File**:
   - Update the `.env` file in the project root with your HiveMQ credentials:
     ```env
     MQTT_BROKER_URL=<your_broker_url>
     MQTT_PORT=8883
     MQTT_USERNAME=<your_username>
     MQTT_PASSWORD=<your_password>
     ```

4. **Test the Connection**:
   - Use the `publisher.py` and `subscriber.py` scripts in this project to publish and subscribe to topics to ensure your HiveMQ broker is working correctly.

### Container Management
```bash
# Start containers
docker start iot_mysql iot_mongodb iot_neo4j iot_mqtt

# Stop containers
docker stop iot_mysql iot_mongodb iot_neo4j iot_mqtt

# Remove containers
docker rm iot_mysql iot_mongodb iot_neo4j iot_mqtt

# View container logs
docker logs iot_mysql
docker logs iot_mongodb
docker logs iot_neo4j
docker logs iot_mqtt
```

## Accessing Databases

### MySQL
```bash
# Connect to MySQL container
docker exec -it iot_mysql mysql -u root -p

# Inside MySQL
USE sensors_data;

# View soil moisture data
SELECT * FROM soil_moisture ORDER BY timestamp DESC LIMIT 10;

# View pH level data
SELECT * FROM ph_level ORDER BY timestamp DESC LIMIT 10;

# Calculate average readings by day
SELECT DATE(timestamp) as date, 
       AVG(moisture_level) as avg_moisture 
FROM soil_moisture 
GROUP BY DATE(timestamp);
```

### MongoDB
```bash
# Connect to MongoDB container
docker exec -it iot_mongodb mongosh

# Inside MongoDB
use environment_data

# View temperature data
db.temperature.find().sort({timestamp: -1}).limit(10)

# View humidity data
db.humidity.find().sort({timestamp: -1}).limit(10)

# Calculate average temperature by day
db.temperature.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: { $dateFromString: { dateString: "$timestamp" } } } },
      avgTemperature: { $avg: "$temperature" }
    }
  }
])
```

### Neo4j
1. Access Neo4j Browser:
   - Open `http://localhost:7474` in your web browser
   - Login with credentials (default: neo4j/your_neo4j_password)

2. Example Cypher queries:
```cypher
// View recent light readings
MATCH (l:Light)
RETURN l
ORDER BY l.timestamp DESC
LIMIT 10;

// View recent nutrient readings
MATCH (n:Nutrient)
RETURN n
ORDER BY n.timestamp DESC
LIMIT 10;

// Calculate average light levels
MATCH (l:Light)
WITH date(l.timestamp) as day, l.level as level
RETURN day, avg(level) as avgLight
ORDER BY day DESC;
```

## Environment Configuration

Create a `.env` file in the project root:
```env
# MQTT Configuration
MQTT_BROKER_URL=localhost
MQTT_PORT=8883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password

# Database Configuration
MONGO_URL=mongodb://localhost:27017/
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=sensors_data
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Data Generation Settings
DATA_GENERATION_INTERVAL=5
```

## Usage

1. Start the subscriber to listen for sensor data:
```bash
python subscriber.py
```

2. In a separate terminal, start the publisher to generate sensor data:
```bash
python publisher.py
```

3. Publisher Controls:
   - Press 'g' to start data generation
   - Press 's' to stop data generation
   - Press 'q' to quit the application

## Troubleshooting

1. Container Issues:
   - Check if container is running: `docker ps`
   - View container logs: `docker logs <container_name>`
   - Restart container: `docker restart <container_name>`
   - Check container network: `docker network inspect bridge`

2. Database Connection Issues:
   - Verify port mappings: `docker port <container_name>`
   - Check container IP: `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_name>`
   - Test connection from host machine:
     - MySQL: `mysql -h localhost -P 3306 -u root -p`
     - MongoDB: `mongosh --host localhost --port 27017`
     - Neo4j: Visit `http://localhost:7474`

3. Data Verification:
   - Check data is being generated: Monitor publisher output
   - Verify data storage: Run example queries in each database
   - Check MQTT messages: Use MQTT client tools like mosquitto_sub
