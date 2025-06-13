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

# Configure git to use token for private repos (if provided)
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=$GITHUB_TOKEN

# Install Python dependencies
RUN if [ -n "$GITHUB_TOKEN" ]; then \
      echo "Installing with private repo access..." && \
      pip install --no-cache-dir git+https://${GITHUB_TOKEN}@github.com/wespiper/signal-box.git@main && \
      grep -v "signal-box" requirements.txt > requirements-filtered.txt && \
      pip install --no-cache-dir -r requirements-filtered.txt; \
    else \
      echo "Installing without private repo access..." && \
      pip install --no-cache-dir -r requirements.txt; \
    fi

# Copy application code
COPY . .

# Create reports directory
RUN mkdir -p reports

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run the application
CMD python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}