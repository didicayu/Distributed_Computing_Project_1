# Dockerfile for Clean Service
FROM python:3.9-slim

WORKDIR /app

# Install required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY actuate_service.py .

# Set entry point to run the clean service script
CMD ["python", "actuate_service.py"]
