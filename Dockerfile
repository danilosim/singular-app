# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml for dependencies
COPY pyproject.toml .

# Install Python dependencies using uv
RUN pip install uv
RUN uv venv
RUN uv sync

# Copy the application code
COPY api ./api
COPY weather_app ./weather_app
COPY data ./data

# Expose port for API
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app

# Run the API server
CMD ["./.venv/bin/uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]
