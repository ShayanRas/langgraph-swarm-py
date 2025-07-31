# Use Python 3.11 for better stability and compatibility
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies including Playwright requirements
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    wget \
    # Playwright dependencies for Chromium
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libxss1 libxtst6 libasound2 libpango-1.0-0 \
    libatspi2.0-0 libgtk-3-0 libxshmfence1 \
    # Xvfb for virtual display (headed browser support in container)
    xvfb \
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

# Install Playwright browsers as root with dependencies
# Install all browsers for stealth rotation
RUN uv run playwright install chromium firefox webkit --with-deps

# Create a non-root user to run the app
RUN useradd -m -u 1000 appuser

# Set up proper permissions for appuser
RUN chown -R appuser:appuser /app && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appuser /home/appuser/.cache

# Copy playwright browsers to appuser's cache
RUN cp -r /root/.cache/ms-playwright /home/appuser/.cache/ && \
    chown -R appuser:appuser /home/appuser/.cache/ms-playwright

# Switch to appuser
USER appuser

# Run smoke tests to verify all imports work
RUN uv run python smoke_test.py

# Switch back to root to install entrypoint
USER root

# Copy and setup entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch back to appuser for runtime
USER appuser

# Expose the FastAPI port
EXPOSE 8000

# Add health check using curl (already installed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Set entrypoint to handle Xvfb
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Run the application
CMD ["uv", "run", "python", "run_local.py"]