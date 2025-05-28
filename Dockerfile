# Use a small, official Python runtime
FROM python:3.10-slim

# Set a working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy our application code
COPY app/ ./app

# Expose the port Uvicorn will run on
EXPOSE 8000

# Start the API with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
