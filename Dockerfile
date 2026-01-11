# ============================================
# Development Stage (with debugpy for VS Code debugging)
# ============================================
FROM python:3.12-slim AS development

# Set working directory
WORKDIR /app

# Set environment variables for development
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies including debugpy for remote debugging
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir debugpy watchfiles

# Copy application code (will be overridden by volume mount in dev)
COPY . .

# Expose API port and debugpy port
EXPOSE 8000 5678

# Default command for development with debugpy
# debugpy listens on 5678, uvicorn runs with reload on 8000
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Builder Stage (for production dependencies)
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Production Stage (minimal, secure)
# ============================================
FROM python:3.12-slim AS production

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/v1/status/ || exit 1

# Run the application with uvicorn (production mode, no reload)
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================
# Worker Stage (for TaskIQ worker - development)
# ============================================
FROM python:3.12-slim AS worker-development

WORKDIR /app

# Set environment variables for development
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies including debugpy
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir debugpy

# Copy application code
COPY . .

# Expose debugpy port for worker
EXPOSE 5679

# Default command for worker development with debugpy
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5679", "-m", "taskiq", "worker", "server.pg_broker:broker"]

# ============================================
# Worker Stage (for TaskIQ worker - production)
# ============================================
FROM python:3.12-slim AS worker-production

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Run the TaskIQ worker
CMD ["taskiq", "worker", "server.pg_broker:broker"]
