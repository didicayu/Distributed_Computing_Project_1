from paho.mqtt import client as mqtt_client
from kafka import KafkaProducer
import os
from datetime import datetime

# MQTT Configuration
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
user_id = os.getenv('USER_ID', 'default_user')
temperature_topic = f'home/{user_id}/temperature'
presence_topic = f'home/{user_id}/presence'

# Kafka Configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
kafka_topic = os.getenv('KAFKA_TOPIC', 'sensor_data')

# Initialize Kafka producer
# producer = KafkaProducer(bootstrap_servers=[kafka_broker], value_serializer=lambda v: v.encode('utf-8'))


# MQTT callbacks

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!", flush=True)
        client.subscribe(temperature_topic)
        client.subscribe(presence_topic)
    else:
        print("Failed to connect, return code %d\n", rc, flush=True)


# def on_message(client, userdata, msg):
#     message = msg.payload.decode()
#     topic = msg.topic
#     timestamp = datetime.now()
#     kafka_message = f"{timestamp}, {topic}, {message}"
#     producer.send(kafka_topic, kafka_message)
#     print(f"Forwarded to Kafka: {kafka_message}", flush=True)


# Initialize MQTT client
client = mqtt_client.Client(f'gateway_{user_id}')
client.on_connect = on_connect
# client.on_message = on_message
client.connect(broker, port)

# Start the MQTT client loop
client.loop_forever()
