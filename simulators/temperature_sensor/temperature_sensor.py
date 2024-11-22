from paho.mqtt import client as mqtt_client

from timeseries_get import TemperatureSimulator
import time
from datetime import datetime, timedelta
import os
import socket
import json

# MQTT Configuration
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
user_id = os.getenv('USER_ID', 'default_user')
topic = f'home/temperature'
cloud_topic = f"{user_id}/actuation/temperature"

# MQTT client ID
client_id = f'temperature_sensor_{user_id}'

# Initialize MQTT client
client = mqtt_client.Client(client_id)

actuate_status = 1

def on_message(client, userdata, msg):
    global actuate_status
    print(f"Received message: {str(msg.payload.decode())} at topic: {msg.topic}", flush=True)
    if msg.topic == cloud_topic:
        try:
            actuate_status = int(json.loads(msg.payload.decode()) == 'True')
            # actuate_status = payload.get('actuate', actuate_status)
            print(f"Received actuation command: {actuate_status}", flush=True)
        except json.JSONDecodeError:
            print(f"Received invalid JSON message: {msg.payload.decode()}", flush=True)

connected = False
max_attempts = 10
attempts = 0
retry_delay = 5

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

# Initialize the temperature simulator with the current timestamp
start_time = datetime.now()
ts = TemperatureSimulator(start_time)

# Main loop for publishing temperature data
simulated_time = start_time  # Start simulated time at the real current time
while True:
    # Advance simulated time by 1 minute for every real second
    simulated_time += timedelta(minutes=1)

    # Get temperature reading from the simulator
    print(f"Actuate status: {actuate_status}")
    temperature = ts.get_temperature(simulated_time, actuate_status)[1]  # Assuming heat pump is on

    # Publish the temperature reading
    message = f"{simulated_time}, {temperature:.2f}"
    client.publish(topic, message)
    print(f"Published to {topic}: {message}", flush=True)

    # Wait for 1 second of real time (simulating 1 minute in the simulation)
    time.sleep(1)
