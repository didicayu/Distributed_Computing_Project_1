# Dockerfile for Temperature Sensor
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy temperature sensor script and timeseries_get.py
COPY ./simulators/temperature_sensor/temperature_sensor.py /app/temperature_sensor.py
COPY ./timeseries_get.py /app/timeseries_get.py

# Install necessary Python packages
RUN pip install paho-mqtt==1.6.1
RUN pip show paho-mqtt

# Set default command to run the temperature sensor script
CMD ["python", "temperature_sensor.py"]
