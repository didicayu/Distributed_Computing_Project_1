# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the script and requirements
COPY integration_script.py /app/integration_script.py
COPY integration_rest_api_script.py /app/integration_rest_api_script.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the integration script
CMD ["python", "integration_rest_api_script.py"]
