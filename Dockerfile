FROM python:3.11-slim

LABEL maintainer="wrees"
LABEL description="MQTT bridge for Hisense/Vidaa TV control"

WORKDIR /app

# Install system dependencies (procps for pgrep health check)
RUN apt-get update && apt-get install -y --no-install-recommends procps \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY hisense_tv/ ./hisense_tv/
COPY hisense2mqtt/ ./hisense2mqtt/
COPY certs/ ./certs/

# Default config location
ENV CONFIG_PATH=/app/config.yaml

# Health check - verify Python process is running
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*hisense2mqtt" || exit 1

# Run the bridge
CMD ["python", "-m", "hisense2mqtt"]
