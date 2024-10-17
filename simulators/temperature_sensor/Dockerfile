FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy presence sensor script
COPY presence_sensor.py /app/presence_sensor.py
COPY ../timeseries_get.py /app/timeseries_get.py

# Install necessary Python packages
RUN pip install paho-mqtt

# Set default command to run the temperature sensor script
CMD ["python", "temperature_sensor.py"]
