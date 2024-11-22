from kafka import KafkaConsumer
import os
import json
from datetime import datetime
import paho.mqtt.client as mqtt_client

# Kafka Configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
clean_kafka_topic = os.getenv('CLEAN_KAFKA_TOPIC', 'sensor_data_clean')

cloud_broker = os.getenv('CLOUD_MQTT_BROKER', 'cloud_mosquitto')
cloud_port = 1883

# Create Kafka Consumer to consume cleaned data
consumer = KafkaConsumer(
    clean_kafka_topic,
    bootstrap_servers=[kafka_broker],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

actuate = True
def temperature_actuation(data):
    global actuate
    json_data = json.loads(data.get("message", "{}"))
    message = json_data['message']
    timestamp = datetime.strptime(json_data['timestamp'], "%Y-%m-%d %H:%M:%S.%f")

    sensor_type = data.get("topic").split('/')[2]
    if sensor_type == "temperature":
        temperature = message

        if float(temperature) <= 20.0:
            actuate = True  # Start climate
        elif float(temperature) >= 24.0:
            actuate = False  # Stop climate

        send_to_mosquitto(data, sensor_type, actuate)

    elif sensor_type == "presence":
        presence = message
        eight_pm = timestamp.replace(hour=20, minute=0, second=0, microsecond=0)
        send_to_mosquitto(data, sensor_type, (timestamp > eight_pm) and bool(presence)) # If less than 20:00h, actuate



client = mqtt_client.Client()
def send_to_mosquitto(data, device_type, actuation):
    user_id = data.get("topic").split('/')[0]
    topic = f"{user_id}/actuation/{device_type}"
    print(f"Sending actuation command to {topic}: {actuation}")

    client.publish(topic, actuation)
    client.connect(cloud_broker, cloud_port)

# Consume and process messages
for message in consumer:
    data = message.value
    print(f"Received data to evaluate: {data}")
    temperature_actuation(data)

