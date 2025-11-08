# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 and Pillow
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static/uploads static/images/products

# Set environment variables
ENV FLASK_APP=app:create_app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Cloud Run uses PORT environment variable
EXPOSE 8080

# Run migrations, seed data, and start server
CMD python -c "from app import create_app; from models import db; app = create_app('production'); app.app_context().push(); db.create_all()" && \
    python seed_data.py && \
    exec gunicorn -b 0.0.0.0:$PORT -w 4 --timeout 120 --access-logfile - --error-logfile - "app:create_app('production')"
