from kafka import KafkaConsumer
import json
import time
import os
from zeep import Client
from zeep.transports import Transport

from requests import Session as RequestsSession
from requests.auth import HTTPBasicAuth

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = os.getenv("TOPIC", "sensor_data_clean")

# SOAP Service Configuration
SOAP_URL = os.getenv("SOAP_WSDL_URL")
SOAP_USER = os.getenv("SOAP_USERNAME")
SOAP_PASS = os.getenv("SOAP_PASSWORD")

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

# Initialize SOAP Client
session = RequestsSession()
session.auth = HTTPBasicAuth(SOAP_USER, SOAP_PASS)
transport = Transport(session=session)
soap_client = Client(SOAP_URL)

user_mapping = {
    '1234': 'Albert',
    '1235': 'Tommy',
    '1236': 'Dakota',
    '1237': 'Tiffany',
}

processed_users = set()  # Track processed users to avoid duplicates
expected_users = set(user_mapping.keys())  # Expected user IDs based on known user mapping


def add_home_to_soap(user_id, owner_name, address):
    """
    Add a home to the SOAP service.
    """
    try:
        print(f"Adding home for user: {owner_name}, Address: {address}")
        soap_client.service.add_home(owner_name, address)
        print(f"Successfully added home: {address} for {owner_name}")
    except Exception as e:
        print(f"Error adding home to SOAP service: {e}")


def list_all_homes():
    """
    Retrieve and print all homes from the SOAP service.
    """
    try:
        print("\nListing all registered homes:")
        homes = soap_client.service.list_homes()
        print(homes)
    except Exception as e:
        print(f"Error retrieving homes: {e}")


def process_message(data):
    """
    Process Kafka message to extract user and home information.
    """
    try:
        topic_parts = data.get("topic").split("/")
        user_id = int(topic_parts[0])  # Extract user ID
        owner_name = user_mapping.get(str(user_id), f"User_{user_id}")
        address = f"Home_{user_id}"

        if str(user_id) in processed_users:
            print(f"User {owner_name} already processed, skipping...")
            return

        # Add home to SOAP service
        add_home_to_soap(user_id, owner_name, address)
        processed_users.add(str(user_id))

    except Exception as e:
        print(f"Error processing message: {e}")


def main():
    print(f"Integration Service started. Listening to topic: {TOPIC}")
    while True:
        try:
            for message in consumer:
                print(f"Received message: {message.value}")
                process_message(message.value)

                # Check if all expected users are processed
                if processed_users == expected_users:
                    print("\nAll users processed. Exiting...")
                    list_all_homes()
                    return  # Exit the loop and terminate the script

        except Exception as e:
            print(f"Error consuming messages: {e}")
            time.sleep(5)  # Retry after a delay


if __name__ == "__main__":
    main()
