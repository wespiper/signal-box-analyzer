# Signal Box Analyzer Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies (including git for GitHub dependencies)
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Verify git is installed
RUN git --version

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel setuptools

# Install Python dependencies (excluding signal-box which is vendored)
COPY requirements.txt requirements-no-signalbox.txt
RUN grep -v "signal-box" requirements.txt > requirements-no-signalbox.txt || cp requirements.txt requirements-no-signalbox.txt
RUN pip install --no-cache-dir -r requirements-no-signalbox.txt

# Copy application code (including vendored dependencies)
COPY . .

# Add vendor directory to Python path
ENV PYTHONPATH=/app/vendor:$PYTHONPATH

# Create reports directory
RUN mkdir -p reports

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run the application
CMD python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}