FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system utilities (curl for healthchecks, git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY src/ ./src/

# Create a local storage folder for SQLite
RUN mkdir -p /app/data

# Expose the port for healthcheck
EXPOSE 8000

# Define Python path
ENV PYTHONPATH=/app

# Run application
CMD ["python", "src/bot.py"]
