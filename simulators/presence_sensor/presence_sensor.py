from paho.mqtt import client as mqtt_client

from timeseries_get import PresenceSimulator
import time
from datetime import datetime, timedelta
import os
import socket
import json

def debug_log(msg):
    print(f"[DEBUG]: {msg}")

# MQTT Configuration
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
user_id = os.getenv('USER_ID', 'default_user')
topic = f'home/presence'
cloud_topic = f"{user_id}/actuation/presence"

# MQTT client ID
client_id = f'presence_sensor_{user_id}'

# Initialize MQTT client
client = mqtt_client.Client(client_id)

connected = False
max_attempts = 10
attempts = 0
retry_delay = 5

def on_message(client, userdata, msg):
    global light_status
    debug_log(f"Received message: {str(msg.payload.decode())} at topic: {msg.topic}")
    if msg.topic == cloud_topic:
        try:
            light_status = int(json.loads(msg.payload.decode()) == 'True')
            debug_log(f"Received actuation command: {light_status}")
        except json.JSONDecodeError:
            debug_log(f"Received invalid JSON message: {msg.payload.decode()}")

while not connected and attempts < max_attempts:
    try:
        client.connect(broker, port)
        connected = True
        print("Connected to MQTT Broker!", flush=True)

        client.subscribe(cloud_topic)
        print(f"Subscribed to {cloud_topic}", flush=True)

    except (socket.error, ConnectionRefusedError):
        attempts += 1
        print(f"Connection attempt {attempts} failed. Retrying in {retry_delay} seconds...", flush=True)
        time.sleep(retry_delay)

if not connected:
    print("Could not connect to MQTT Broker after several attempts. Exiting.", flush=True)
    exit(1)

client.on_message = on_message
client.loop_start()

# Initialize the presence simulator with the current timestamp
start_time = datetime.now()
ps = PresenceSimulator(start_time)

light_status = 0

# Main loop for publishing presence data
simulated_time = start_time  # Start simulated time at the real current time
while True:
    # Advance simulated time by 1 minute for every real second
    simulated_time += timedelta(minutes=1)

    # Get presence reading from the simulator
    presence = ps.get_presence(simulated_time)[1]

    # Publish the presence reading
    message = f"{simulated_time}, {presence}, {light_status}"

    client.publish(topic, message)
    print(f"Published to {topic}: {message} (sim_time, presence, light_status)", flush=True)

    # Wait for 1 second of real time (simulating 1 minute in the simulation)
    time.sleep(1)



