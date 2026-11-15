FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY backend /app/backend
COPY data /app/data

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/uploads /app/data/qdrant_db && \
    chown -R appuser:appuser /app

USER appuser

# Set python path
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
