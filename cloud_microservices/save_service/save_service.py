from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
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

kafka_topics = os.getenv('KAFKA_TOPICS', 'sensor_data_clean,sensor_data').split(',')

# Create Kafka Consumer to consume cleaned data
consumer = KafkaConsumer(
    *kafka_topics,
    bootstrap_servers=[kafka_broker],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize InfluxDB client
influxdb_url = f"http://{influxdb_host}:{influxdb_port}"
influxdb_token = os.getenv('INFLUXDB_TOKEN', 'your-token')
influxdb_org = os.getenv('INFLUXDB_ORG', 'your-org')
influxdb_bucket = os.getenv('INFLUXDB_BUCKET', 'sensor_data')

# Create the InfluxDBClient instance
influxdb_client = InfluxDBClient(
    url=influxdb_url,
    token=influxdb_token,
    org=influxdb_org
)

write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

print("Save Service is running and listening to topic:", clean_kafka_topic)

# Function to save data to InfluxDB
def save_to_influxdb(data, data_type):
    try:
        # Extract timestamp and other fields
        json_data = json.loads(data.get("message", "{}"))
        message = json_data['message']
        timestamp = datetime.fromisoformat(json_data['timestamp']).isoformat() + "Z"

        # Create a Point object for InfluxDB
        point = (
            Point("sensor_data")
            .tag("type_of_data", data_type) # filtered / unfiltered
            .tag("user_id", int(data.get("topic").split('/')[0]))  # Extract user_id from topic
            .tag("sensor_type", data.get("topic").split('/')[2])  # Extract sensor_type from topic
            .field("message", float(message))
            .time(timestamp)
        )

        # Check if 'light' key exists in json_data and add it as a field
        if 'light' in json_data:
            light_status = int(json_data['light'])  # Ensure the light status is an integer (0 or 1)
            point = point.field("light_status", light_status)

        # Write the point to InfluxDB
        write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)
        print(f"Saved data to InfluxDB: {point}")
    except Exception as e:
        print(f"Error saving to InfluxDB: {e}")

# Consume and process messages
for message in consumer:
    data = message.value
    print(f"Received cleaned data to save: {data}")

    data_type = message.topic
    # Save to InfluxDB
    save_to_influxdb(data, data_type)
    print(f"Saved to InfluxDB: {data}")
