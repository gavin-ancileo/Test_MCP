# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY mcp/ ./mcp/
COPY connectors/ ./connectors/
COPY admin/ ./admin/
COPY run.py .

# Copy existing database
COPY data/prompts.db /app/data/prompts.db

# Create data directory (if not exists)
RUN mkdir -p /app/data

# Expose port 8000 for API
EXPOSE 8000

# Default command - will be overridden by docker-compose
CMD ["python", "run.py"]