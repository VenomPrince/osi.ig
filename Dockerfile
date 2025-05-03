FROM python:3.9-slim

# Install system dependencies for DNS resolver
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tor \
    gcc \
    libffi-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py /app/
COPY .lib /app/.lib/

# Create a non-root user and switch to it
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Start Tor service in background on container start
CMD service tor start && python main.py