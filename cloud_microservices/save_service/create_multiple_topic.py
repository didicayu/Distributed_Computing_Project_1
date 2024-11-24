from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaConsumer



def create_kafka_topic(kafka_server, topic_name, partitions, replicas):
    """Create a new Kafka topic with a specific number of partitions."""
    try:
        # Initialize the KafkaAdminClient
        client = KafkaAdminClient(
            bootstrap_servers=kafka_server,
            client_id='actuate_service_group'
        )

        # Create the new topic configuration
        new_topic = NewTopic(
            name=topic_name,
            num_partitions=partitions,
            replication_factor=replicas
        )

        # Create the topic
        client.create_topics(new_topics=[new_topic], validate_only=False)
        print(f"Topic '{topic_name}' created with {partitions} partitions.", flush=True)

    except Exception as e:
        print(f"Error creating topic: {e}", flush=True)

    finally:
        # Close the admin client
        client.close()


def main():
    # Kafka server address
    kafka_server = 'kafka:9092'

    # Topic details
    topic_name = 'sensor_data_clean'
    partitions = 6
    replicas = 1

    # Create the topic
    create_kafka_topic(kafka_server, topic_name, partitions, replicas)


if __name__ == "__main__":
    main()