# Dockerfile for Save Service
FROM python:3.9-slim

WORKDIR /app

# Install required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY save_service.py .
COPY create_multiple_topic.py .

# Set entry point to run the save service script
CMD ["sh", "-c", "python create_multiple_topic.py && python save_service.py"]

