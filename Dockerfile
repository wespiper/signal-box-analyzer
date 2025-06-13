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

# Pass GitHub token as build arg
ARG GITHUB_TOKEN

# Debug: Check if token is being passed (v2)
RUN echo "GitHub Token status at $(date): $(if [ -z "$GITHUB_TOKEN" ]; then echo 'NOT SET'; else echo 'SET (hidden)'; fi)"

# Configure git to use the token for authentication
RUN if [ ! -z "$GITHUB_TOKEN" ]; then \
        echo "Configuring git with token..." && \
        git config --global url."https://oauth2:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/" && \
        echo "Git config set successfully"; \
    else \
        echo "No GitHub token provided, skipping git config"; \
    fi

# Debug: Show git config
RUN git config --global --list | grep url || echo "No URL replacements in git config"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Failed to install requirements. Error details:" && \
     pip install --no-cache-dir -r requirements.txt -v)

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