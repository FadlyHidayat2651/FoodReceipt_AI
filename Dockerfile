FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Make sure DB directory exists inside container
RUN mkdir -p /app/src/backend/app/db

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose backend + frontend ports
EXPOSE 8114 3000

# Run backend then frontend (absolute paths)
CMD bash -c "python /app/src/backend/app/db/init_all.py && \
             python /app/src/backend/app/main.py & \
             python -m http.server 3000 --directory /app/src/frontend"
