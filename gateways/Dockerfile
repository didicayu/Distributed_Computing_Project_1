# Dockerfile for Gateway
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy gateway script
COPY user_gateway.py /app/user_gateway.py

# Install necessary Python packages
RUN pip install paho-mqtt==1.6.1 kafka-python

# Set default command to run the gateway script
CMD ["python", "user_gateway.py"]
