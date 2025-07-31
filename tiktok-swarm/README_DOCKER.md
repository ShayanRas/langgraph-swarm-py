# Docker Setup for TikTok Swarm

This project uses Docker and UV package manager to ensure consistent environments and avoid dependency conflicts.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- `.env` file with required environment variables

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tiktok-swarm
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Build and run with Docker Compose**
   ```bash
   # Development mode (with hot reloading)
   docker-compose up --build

   # Or use development-specific config
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Adminer (DB UI): http://localhost:8080 (dev only)

## Development Workflow

### Running in Development Mode
```bash
# Start all services with hot reloading
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run in background
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f tiktok-swarm
```

### Adding Dependencies
```bash
# Add a new package using UV
docker-compose exec tiktok-swarm uv add langchain-community

# Sync dependencies
docker-compose exec tiktok-swarm uv sync
```

### Running Tests
```bash
# Run all tests
docker-compose exec tiktok-swarm uv run pytest

# Run with coverage
docker-compose exec tiktok-swarm uv run pytest --cov
```

### Linting and Formatting
```bash
# Run ruff linter
docker-compose exec tiktok-swarm uv run ruff check src/

# Format code
docker-compose exec tiktok-swarm uv run ruff format src/

# Type checking
docker-compose exec tiktok-swarm uv run mypy src/
```

## Production Deployment

### Build Production Image
```bash
# Build optimized production image
docker build -t tiktok-swarm:latest .

# Or with docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

### Run in Production
```bash
# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale the application
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale tiktok-swarm=3
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs tiktok-swarm

# Rebuild without cache
docker-compose build --no-cache
```

### Import errors
The Docker setup uses Python 3.11 and UV package manager to ensure compatibility. If you still see import errors:

1. Make sure you're using the official `langgraph-swarm` package (not local copy)
2. Delete any `src/langgraph_swarm` directory
3. Rebuild the container: `docker-compose build --no-cache`

### Database connection issues
```bash
# Check if postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Connect to postgres
docker-compose exec postgres psql -U postgres
```

## Docker Commands Reference

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec tiktok-swarm /bin/bash

# Build specific service
docker-compose build tiktok-swarm

# Remove dangling images
docker image prune
```

## Architecture

- **Python 3.11**: Stable version with good library support
- **UV Package Manager**: Fast, reliable dependency management
- **Multi-stage Dockerfile**: Optimized image size
- **Docker Compose**: Easy orchestration of services
- **Volume Mounts**: Hot reloading in development
- **Health Checks**: Automatic container monitoring

## Security Notes

- The container runs as non-root user `appuser`
- Secrets are passed via environment variables
- Production image doesn't include development dependencies
- Use Docker secrets for sensitive data in production