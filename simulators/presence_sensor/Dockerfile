# Dockerfile for Presence Sensor
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy presence sensor script and timeseries_get.py
COPY ./simulators/presence_sensor/presence_sensor.py /app/presence_sensor.py
COPY ./timeseries_get.py /app/timeseries_get.py

# Install necessary Python packages
RUN pip install paho-mqtt==1.6.1
RUN pip show paho-mqtt

# Set default command to run the presence sensor script
CMD ["python", "presence_sensor.py"]
