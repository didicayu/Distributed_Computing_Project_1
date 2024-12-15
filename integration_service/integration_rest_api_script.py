from kafka import KafkaConsumer
import requests
import json
import os
import time

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL")
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = os.getenv("TOPIC", "sensor_data_clean")

# User Mapping
user_mapping = {
    '1234': 'Albert',
    '1235': 'Tommy',
    '1236': 'Dakota',
    '1237': 'Tiffany',
}

# Local to API User ID Mapping
local_to_api_user_id = {}
processed_users = set()
processed_houses = set()




# Authenticate and Get Token
def get_access_token():
    url = f"{API_BASE_URL}/auth/token"
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to authenticate: {response.status_code} - {response.text}")


# Check if User Exists
def user_exists(username, access_token):
    url = f"{API_BASE_URL}/users/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        users = response.json()["message"]
        for user in users:
            if user["username"] == username:
                return user["id"]  # Return user ID if exists
        return None
    else:
        raise Exception(f"Failed to retrieve users: {response.status_code} - {response.text}")


# Create User
def create_user(username, password, role, access_token):
    if username in local_to_api_user_id:
        print(f"User '{username}' is already mapped to API ID: {local_to_api_user_id[username]}. Skipping creation.",
              flush=True)
        return local_to_api_user_id[username]

    existing_user_id = user_exists(username, access_token)
    if existing_user_id:
        print(f"User '{username}' already exists with ID: {existing_user_id}. Skipping creation.", flush=True)
        local_to_api_user_id[username] = existing_user_id
        return existing_user_id

    url = f"{API_BASE_URL}/users/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"username": username, "password": password, "role": role}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        user_data = response.json()
        print(f"User '{username}' created successfully with ID: {user_data['id']}.", flush=True)
        local_to_api_user_id[username] = user_data["id"]
        return user_data["id"]
    else:
        print(f"Error creating user '{username}': {response.status_code} - {response.text}", flush=True)
        return None


# Check if House Exists
def house_exists(owner_id, address, access_token):
    url = f"{API_BASE_URL}/users/{owner_id}/homes/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        houses = response.json()["message"]
        return any(house["address"] == address for house in houses)
    elif response.status_code == 404:
        return False
    else:
        raise Exception(f"Failed to retrieve houses: {response.status_code} - {response.text}")


# Create House
def create_house(owner_id, name, address, description, num_rooms, access_token):
    if (owner_id, address) in processed_houses:
        print(f"House '{address}' for user ID {owner_id} is already processed. Skipping creation.", flush=True)
        return None

    if house_exists(owner_id, address, access_token):
        print(f"House '{address}' already exists for user ID {owner_id}. Skipping creation.", flush=True)
        processed_houses.add((owner_id, address))
        return None

    url = f"{API_BASE_URL}/users/{owner_id}/homes/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "name": name,
        "address": address,
        "num_rooms": num_rooms,
        "description": description,
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"House '{address}' created successfully for user ID {owner_id}.", flush=True)
        processed_houses.add((owner_id, address))
        return True
    else:
        print(f"Error creating house '{address}': {response.status_code} - {response.text}", flush=True)
        return None


# Process Kafka Messages
def process_message(data, access_token):
    """
    Process Kafka message to extract user and home information.
    """
    try:
        topic_parts = data.get("topic").split("/")
        user_id = int(topic_parts[0])  # Extract user ID
        username = user_mapping.get(str(user_id), f"User_{user_id}")
        address = f"Home_{user_id}"

        if str(user_id) in processed_users:
            print(f"User '{username}' and their house are already processed. Skipping.", flush=True)
            return

        # Create User and House
        owner_id = create_user(username=username, password="default_password", role="owner", access_token=access_token)
        if owner_id:
            if create_house(
                    owner_id=owner_id,
                    name=f"{username}'s Home",
                    address=address,
                    description=f"Description for {username}'s home",
                    num_rooms=3,
                    access_token=access_token
            ):
                processed_users.add(str(user_id))  # Mark user and house as processed
    except Exception as e:
        print(f"Error processing message: {e}")


def main():
    access_token = get_access_token()

    print(f"Integration Service started. Listening to topic: {TOPIC}")
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    expected_users = set(user_mapping.keys())  # Expected user IDs

    for message in consumer:
        print(f"Received message: {message.value}")
        process_message(message.value, access_token)

        # Stop when all users and houses are processed
        print(f"Processed Users: {processed_users}")
        print(f"Expected Users: {expected_users}")
        if processed_users == expected_users:
            print("\nAll users and houses have been created successfully. Exiting...")
            break


if __name__ == "__main__":
    main()
