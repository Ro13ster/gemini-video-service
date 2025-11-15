# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env.example .env

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for API
EXPOSE 8000

# Start Ray Serve API (default)
CMD ["serve", "run", "src.api:deployment", "--host", "0.0.0.0", "--port", "8000"]