from paho.mqtt import client as mqtt_client
from timeseries_get import TemperatureSimulator
import time
from datetime import datetime, timedelta
import os
import socket

# MQTT Configuration
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
user_id = os.getenv('USER_ID', 'default_user')
topic = f'home/{user_id}/temperature'

# MQTT client ID
client_id = f'temperature_sensor_{user_id}'

# Initialize MQTT client
client = mqtt_client.Client(client_id)

connected = False
max_attempts = 10
attempts = 0
retry_delay = 5

while not connected and attempts < max_attempts:
    try:
        client = mqtt_client.Client(client_id)
        connected = True

    except (socket.error, ConnectionRefusedError):
        attempts += 1
        print(f"Connection attempt {attempts} failed. Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)

if not connected:
    print("Could not connect to MQTT Broker after several attempts. Exiting.")
    exit(1)



client = mqtt_client.Client(client_id)
client.connect(broker, port)

# Initialize the temperature simulator with the current timestamp
start_time = datetime.now().isoformat()
ts = TemperatureSimulator(start_time)

# Main loop for publishing temperature data
simulated_time = start_time  # Start simulated time at the real current time
while True:
    # Advance simulated time by 1 minute for every real second
    simulated_time += timedelta(minutes=1)

    # Get temperature reading from the simulator
    temperature = ts.get_temperature(simulated_time, 1)  # Assuming heat pump is on

    # Publish the temperature reading
    message = f"{simulated_time}, {temperature:.2f}"
    client.publish(topic, message)
    print(f"Published to {topic}: {message}")

    # Wait for 1 second of real time (simulating 1 minute in the simulation)
    time.sleep(1)
