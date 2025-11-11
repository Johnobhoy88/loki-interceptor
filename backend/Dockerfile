# Multi-stage Dockerfile for LOKI Backend
# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt backend-requirements.txt
COPY enterprise/requirements.txt enterprise-requirements.txt

# Combine all requirements
RUN cat backend-requirements.txt enterprise-requirements.txt > /tmp/all-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --user -r /tmp/all-requirements.txt

# Add Prometheus monitoring
RUN pip install --no-cache-dir --user prometheus-client gunicorn

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim

# Set labels for container metadata
LABEL maintainer="LOKI DevOps Team"
LABEL app="loki-backend"
LABEL version="1.0.0"

# Create non-root user for security
RUN groupadd -r loki && useradd -r -g loki loki

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/loki/.local

# Copy application code
COPY --chown=loki:loki . .

# Ensure Python can find user-installed packages
ENV PATH=/home/loki/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER loki

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5002}/health || exit 1

# Expose port
EXPOSE 5002

# Use gunicorn for production with multiple workers
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5002", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "server:app"]
