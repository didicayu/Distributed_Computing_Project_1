# Dockerfile for Gateway
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy gateway script
COPY user_gateway.py /app/user_gateway.py
COPY ../../timeseries_get.py /app/timeseries_get.py

# Install necessary Python packages
RUN pip install paho-mqtt kafka-python

# Set default command to run the gateway script
CMD ["python", "user_gateway.py"]
