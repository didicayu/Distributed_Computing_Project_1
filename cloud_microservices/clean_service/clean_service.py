from kafka import KafkaConsumer, KafkaProducer
import os
import json

# Kafka Configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
input_topic = os.getenv('KAFKA_TOPIC', 'sensor_data')
output_topic = os.getenv('CLEAN_KAFKA_TOPIC', 'sensor_data_clean')

# Create Kafka Consumer to consume raw sensor data
consumer = KafkaConsumer(
    input_topic,
    bootstrap_servers=[kafka_broker],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Create Kafka Producer to send cleaned data
producer = KafkaProducer(
    bootstrap_servers=[kafka_broker],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Clean Service is running and listening to topic:", input_topic)

def clean_data(raw_data):
    # Simple data cleaning logic - you can modify this based on requirements
    cleaned_data = {}
    cleaned_data['timestamp'] = raw_data.get('timestamp')
    cleaned_data['topic'] = raw_data.get('topic')
    cleaned_data['message'] = raw_data.get('message').strip()  # Example cleaning
    return cleaned_data

# Consume and process messages
for message in consumer:
    raw_data = message.value
    print(f"Received message to clean: {raw_data}", flush=True)

    # Clean the data
    cleaned_data = clean_data(raw_data)
    print(f"Cleaned data: {cleaned_data}", flush=True)

    # Send cleaned data to Kafka
    producer.send(output_topic, value=cleaned_data)
    print(f"Sent cleaned data to Kafka topic {output_topic}: {cleaned_data}", flush=True)
