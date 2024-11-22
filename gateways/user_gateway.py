import json

from paho.mqtt import client as mqtt_client
import os
from datetime import datetime

# Local MQTT Configuration
local_broker = os.getenv('MQTT_BROKER', 'localhost')
local_port = 1883
user_id = os.getenv('USER_ID', 'default_user')
temperature_topic = f'home/temperature'
presence_topic = f'home/presence'

# Cloud MQTT Configuration
cloud_broker = os.getenv('CLOUD_MQTT_BROKER', 'cloud_mosquitto')
cloud_port = 1883
cloud_topic = f"{user_id}/actuation/#"

def on_connect_cloud(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to Cloud MQTT Broker!", flush=True)
        client.subscribe(cloud_topic)
    else:
        print(f"Failed to connect to cloud broker, return code {rc}\n", flush=True)

def on_message_cloud(client, userdata, msg):
    received_message = msg.payload.decode()
    topic = msg.topic

    device_type = topic.split('/')[2]

    # Forward the message as is
    message_json = json.dumps(received_message)

    if device_type == "temperature":
        local_client.publish(f'{user_id}/actuation/temperature', message_json)
    elif device_type == "presence":
        local_client.publish(f'{user_id}/actuation/presence', message_json)

    print(f"Forwarded to Local MQTT Broker {user_id}/actuation/{device_type}: {message_json}", flush=True)


# Initialize MQTT Client to Connect to Local Broker
def on_connect_local(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to Local MQTT Broker!", flush=True)
        client.subscribe(temperature_topic)
        client.subscribe(presence_topic)
    else:
        print(f"Failed to connect to local broker, return code {rc}\n", flush=True)


def on_message_local(client, userdata, msg):
    # Initialize MQTT Client to Connect to Cloud Broker
    received_message = msg.payload.decode()
    timestamp = received_message.split(', ')[0]
    message = received_message.split(', ')[1]
    topic = msg.topic

    device_type = topic.split('/')[1]

    forward_message = {
        'timestamp': str(timestamp),
        'message': message
    }

    if device_type == 'presence':
        forward_message['light'] = received_message.split(', ')[2]

    message_json = json.dumps(forward_message)

    cloud_client.publish(f'{user_id}/{topic}', message_json)
    print(f"Forwarded to Cloud MQTT Broker {topic}: {message_json}", flush=True)


# Connect to the Local MQTT Broker
local_client = mqtt_client.Client(f'gateway_{user_id}')
local_client.on_connect = on_connect_local
local_client.on_message = on_message_local
local_client.connect(local_broker, local_port)

# Connect to the Cloud MQTT Broker
cloud_client = mqtt_client.Client()
cloud_client.on_connect = on_connect_cloud
cloud_client.on_message = on_message_cloud
cloud_client.connect(cloud_broker, cloud_port)
cloud_client.loop_start()

# Start the MQTT client loop
local_client.loop_forever()
