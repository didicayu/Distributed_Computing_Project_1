# Project with Docker

This project uses **Docker** and **Docker Compose** for easy setup and execution.

## Prerequisites

Before you start, make sure you have the following installed:  

- [Docker](https://www.docker.com/get-started) (v20.10 or higher)  
- [Docker Compose](https://docs.docker.com/compose/install/)  

To verify your installations, run:  

```bash
docker --version
docker compose version
```

---

## Steps to Run the Project

### 1. Modify `docker-compose.yml` for the Actuate Delay Exercise  

To address the exercise **"How can we solve the problem when there is a delay in the Actuate?"**, you need to enable the `actuate_service_with_sleep` service:  

1. Open the `docker-compose.yml` file.  
2. Uncomment the following section:  

```yaml
actuate_service_with_sleep:
  build:
    context: ./cloud_microservices/actuate_service_with_sleep
  container_name: actuate_service_with_sleep
  environment:
    - KAFKA_BROKER=kafka:9092
    - CLEAN_KAFKA_TOPIC=sensor_data_clean
    - CLOUD_MQTT_BROKER=cloud_mosquitto
  depends_on:
    kafka:
      condition: service_healthy
  networks:
    - cloud_network
    - server_network
  deploy:
    replicas: 6
```

3. Save the changes to `docker-compose.yml`.

### 2. Adjust the Number of Partitions in `create_multiple_topic`  

It is worth noting that for normal execution (i.e **without** the Actuate Delay Exercise), the Kafka topic is created with **1 partition**. Else we want as much partitions as the number of replicas.

To configure the Kafka topic with **1 partition** instead of the default (e.g., 6):  

1. Open the script that contains the `create_multiple_topic` function.  
2. Locate the `partitions` parameter in the `main()` function.  
3. Update it as follows:  

```python
def main():
    # Kafka server address
    kafka_server = 'kafka:9092'

    # Topic details
    topic_name = 'sensor_data_clean'
    partitions = 1  # Set to 1 partition
    replicas = 1

    # Create the topic
    create_kafka_topic(kafka_server, topic_name, partitions, replicas)
```

4. Save the script.  

### 3. Restart the Services  

After making the above changes, restart the Docker services:

```bash
docker compose down
docker compose build
docker compose up
```

### 4. Access InfluxDB  

Once the services are running, you can access **InfluxDB** at:  

```
http://localhost:8086/
```