# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir /tmp uv && \
    mv /tmp/uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install uv for runtime
RUN pip install --no-cache-dir /tmp uv && \
    mv /tmp/uv /usr/local/bin/uv

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uv \
    /usr/local/bin/uv

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run --directory /app python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()"

# Run the application
CMD ["uv", "run", "--directory", "/app", "python", "-m", "app.main"]
