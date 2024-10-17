from paho.mqtt import client as mqtt_client
from timeseries_get import PresenceSimulator
import time
from datetime import datetime, timedelta
import os


# MQTT Configuration
broker = os.getenv('MQTT_BROKER', 'localhost')
port = 1883
user_id = os.getenv('USER_ID', 'default_user')
topic = f'home/{user_id}/presence'

# MQTT client ID
client_id = f'presence_sensor_{user_id}'

# Initialize MQTT client
client = mqtt_client.Client(client_id)
client.connect(broker, port)

# Initialize the presence simulator with the current timestamp
start_time = datetime.now()
ps = PresenceSimulator(start_time)

# Main loop for publishing presence data
simulated_time = start_time  # Start simulated time at the real current time
while True:
    # Advance simulated time by 1 minute for every real second
    simulated_time += timedelta(minutes=1)

    # Get presence reading from the simulator
    presence = ps.get_presence(simulated_time)

    # Publish the presence reading
    message = f"{simulated_time}, {presence}"
    client.publish(topic, message)
    print(f"Published to {topic}: {message}")

    # Wait for 1 second of real time (simulating 1 minute in the simulation)
    time.sleep(1)  # Simulating 1 minute in real time