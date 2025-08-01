# Universal Consultant Intelligence Platform - Multi-Stage Docker Build
# Production-ready containerization with optimized layers

# =============================================================================
# Stage 1: Python Dependencies and Backend Build
# =============================================================================
FROM python:3.11-slim as backend-builder

# Set build arguments
ARG BUILDKIT_INLINE_CACHE=1

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Frontend Build with Node.js
# =============================================================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files (if they exist)
COPY frontend/package*.json ./

# Install dependencies if package.json exists, otherwise skip
RUN if [ -f package.json ]; then npm ci --only=production; fi

# Copy frontend source
COPY frontend/ ./

# Build frontend assets (if build script exists)
RUN if [ -f package.json ] && npm run build --if-present; then \
        echo "Frontend built successfully"; \
    else \
        echo "No build script found, using source files directly"; \
        mkdir -p dist && cp -r src/* dist/; \
    fi

# =============================================================================
# Stage 3: Production Runtime
# =============================================================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application
COPY backend/ ./backend/
COPY .env.example .env

# Copy frontend assets from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY --from=frontend-builder /app/frontend/src ./frontend/src

# Copy test files for validation
COPY tests/ ./tests/
COPY playwright.config.js ./

# Copy startup and health check scripts
COPY docker/ ./docker/

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/data /app/reports && \
    chown -R appuser:appuser /app && \
    chmod +x docker/*.sh

# Copy health check script
COPY <<EOF /app/healthcheck.py
#!/usr/bin/env python3
import asyncio
import aiohttp
import sys
import os

async def health_check():
    """Health check for Docker container"""
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'healthy':
                        print("Health check passed")
                        return 0
                
                print(f"Health check failed: HTTP {response.status}")
                return 1
                
    except Exception as e:
        print(f"Health check error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(health_check())
    sys.exit(exit_code)
EOF

RUN chmod +x /app/healthcheck.py

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python /app/healthcheck.py

# Default command
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]