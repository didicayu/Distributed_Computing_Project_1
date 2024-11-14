from kafka import KafkaConsumer
from influxdb import InfluxDBClient
import os
import json
from datetime import datetime

# Kafka Configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
clean_kafka_topic = os.getenv('CLEAN_KAFKA_TOPIC', 'sensor_data_clean')

# InfluxDB Configuration
influxdb_host = os.getenv('INFLUXDB_HOST', 'influxdb')
influxdb_port = 8086
influxdb_database = os.getenv('INFLUXDB_DATABASE', 'sensor_data')

# Create Kafka Consumer to consume cleaned data
consumer = KafkaConsumer(
    clean_kafka_topic,
    bootstrap_servers=[kafka_broker],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize InfluxDB client
influxdb_client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
influxdb_client.create_database(influxdb_database)
influxdb_client.switch_database(influxdb_database)

print("Save Service is running and listening to topic:", clean_kafka_topic)

# Function to save data to InfluxDB
def save_to_influxdb(cleaned_data):
    json_body = [
        {
            "measurement": "sensor_data",
            "tags": {
                "topic": cleaned_data.get('topic'),
                "user_id": cleaned_data.get('topic').split('/')[1]  # Extract user_id from topic, e.g. 'home/1234/...'
            },
            "time": cleaned_data.get('timestamp'),
            "fields": {
                "message": cleaned_data.get('message')
            }
        }
    ]
    influxdb_client.write_points(json_body)

# Consume and process messages
for message in consumer:
    cleaned_data = message.value
    print(f"Received cleaned data to save: {cleaned_data}")

    # Save to InfluxDB
    save_to_influxdb(cleaned_data)
    print(f"Saved to InfluxDB: {cleaned_data}")
