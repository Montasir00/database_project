# Database Project

This project aims to create an IoT simulation using Docker with MongoDB, MySQL, phpMyAdmin, Neo4j, and Eclipse MQTT. The simulation will generate and manage data related to various environmental parameters, with each type of data being stored in the appropriate database management system (DBMS) via an MQTT server.

## Simulated Data and Storage

1. **Soil Moisture**: Stored in an SQL database (MySQL).
2. **Temperature**: Stored in MongoDB.
3. **Light**: Stored in Neo4j.
4. **Humidity**: Stored in MongoDB.
5. **pH**: Stored in an SQL database (MySQL).
6. **Nutrient Levels**: Stored in Neo4j.

The data will be generated and transmitted to the respective databases using an MQTT server.
