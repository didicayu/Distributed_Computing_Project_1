# mqtt_publisher.py
from timeseries_get import TemperatureSimulator, PresenceSimulator
import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json

# Load configuration from JSON file
def load_config():
    with open('config/mqtt_config.json', 'r') as config_file:
        return json.load(config_file)

# Load configuration
config = load_config()
mqtt_broker_address = config["broker_address"]
temperature_topic = config["temperature_topic"]
presence_topic = config["presence_topic"]

# Initialize MQTT client
client = mqtt.Client()
client.connect(mqtt_broker_address, 1883, 60)

# Initialize the simulators with the current timestamp
temp_simulator = TemperatureSimulator(datetime.now())
presence_simulator = PresenceSimulator(datetime.now())

# Main loop for publishing data
while True:
    current_time = datetime.now()

    # Get sensor readings
    sim_time, temperature = temp_simulator.get_temperature(current_time, dev_status=1)  # Assuming heat pump is on
    sim_time, presence = presence_simulator.get_presence(current_time)

    # Publish temperature and presence data to MQTT topics
    client.publish(temperature_topic, f"{sim_time}, {temperature}")
    client.publish(presence_topic, f"{sim_time}, {presence}")

    # Print for verification
    print(f"Published to {temperature_topic}: {sim_time}, {temperature}")
    print(f"Published to {presence_topic}: {sim_time}, {presence}")

    # Wait for 1 second (1 minute in simulation time)
    time.sleep(1)
