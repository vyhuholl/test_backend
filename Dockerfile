# Runtime stage
FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Disable development dependencies
ENV UV_NO_DEV=1

# Install dependencies
RUN uv sync --locked

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run --directory /app python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()"

# Run application
CMD ["uv", "run", "--directory", "/app", "python", "-m", "app.main"]
