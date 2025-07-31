# Use Python 3.11 for better stability and compatibility
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for better Docker layer caching)
COPY pyproject.toml uv.lock* ./

# Install Python dependencies with UV (non-editable mode)
RUN uv sync --no-dev --no-editable

# Copy the rest of the application
COPY . .

# Run smoke tests to verify all imports work
RUN /app/.venv/bin/python smoke_test.py

# Create a non-root user to run the app
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose the FastAPI port
EXPOSE 8000

# Add health check using curl (already installed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["uv", "run", "python", "run_local.py"]