FROM python:3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create DB directory
RUN mkdir -p src/backend/app/db

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8114 3000

# Run backend and frontend
CMD bash -c "python src/backend/app/db/init_all.py && \
             python src/backend/app/main.py & \
             python -m http.server 3000 --directory src/frontend"
