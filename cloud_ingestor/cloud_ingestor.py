import json
from paho.mqtt import client as mqtt_client
from kafka import KafkaProducer
import os
import logging

# Cloud MQTT Configuration
cloud_broker = os.getenv('CLOUD_MQTT_BROKER', 'cloud_mosquitto')
cloud_port = 1883
cloud_topic = '+/home/#'

# Kafka Configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
kafka_topic = os.getenv('KAFKA_TOPIC', 'sensor_data')

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=[kafka_broker],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Cloud Ingestor connected to Cloud MQTT Broker!", flush=True)
        # Subscribe to all topics from cloud mosquitto
        client.subscribe(cloud_topic)
    else:
        print(f"Failed to connect to cloud broker, return code {rc}\n", flush=True)

def on_message(client, userdata, msg):
    # Decode the MQTT message
    message = msg.payload.decode()
    topic = msg.topic

    print(f"Received from MQTT topic '{topic}': {message}", flush=True)
    logging.info(f"Received from MQTT topic '{topic}': {message}")

    # Prepare the message for Kafka
    kafka_message = {
        'topic': topic,
        'message': message
    }

    # Send to Kafka
    producer.send(kafka_topic, kafka_message)
    print(f"Forwarded to Kafka topic '{kafka_topic}': {kafka_message}", flush=True)

# Initialize MQTT Client
client = mqtt_client.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(cloud_broker, cloud_port)

# Start the MQTT client loop
client.loop_forever()
