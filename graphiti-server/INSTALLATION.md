# Installation Guide - Graphiti REST Server

## Prerequisites

- Python 3.10+ (3.12 recommended)
- Neo4j 5.26+ (included in Docker Compose)
- OpenAI API key
- `uv` package manager

## Quick Start

### 1. Docker Compose (Recommended)

```bash
cd rest_server

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...

# Start everything
docker compose up

# Server available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Neo4j: http://localhost:7474
```

### 2. Local Development

```bash
cd rest_server

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set environment variables
export OPENAI_API_KEY=sk-...
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password

# Start server
uv run graphiti_rest_server.py --use-custom-entities --group-id my-kb

# Server available at http://localhost:8000
```

## Verify Installation

```bash
# Check server status
curl http://localhost:8000/api/v1/status

# Should return:
# {
#   "status": "ok",
#   "message": "Graphiti REST server is running and connected to Neo4j",
#   "config": { ... }
# }

# View interactive docs
open http://localhost:8000/docs
```

## Configuration

### Environment Variables

See `.env.example` for all available options. Key variables:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
MODEL_NAME=gpt-4o-mini
SMALL_MODEL_NAME=gpt-4.1-nano
LLM_TEMPERATURE=1.0
SEMAPHORE_LIMIT=10

# Neo4j (Docker defaults)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=demodemo
```

### CLI Arguments

Override environment variables:

```bash
uv run graphiti_rest_server.py \
  --model gpt-4o-mini \
  --temperature 0.7 \
  --use-custom-entities \
  --group-id my-kb \
  --port 8000
```

## Dependency Management

This project uses `uv` for dependency management:

```bash
# Add a new dependency
uv add requests

# Update dependencies
uv lock --upgrade

# Sync dependencies
uv sync
```

## Docker Build

```bash
# Build image
docker build -t graphiti-rest:latest .

# Run standalone
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e NEO4J_URI=bolt://neo4j:7687 \
  graphiti-rest:latest

# Or use docker-compose
docker compose up
```

## Troubleshooting

### Port Already in Use

```bash
# Change port
uv run graphiti_rest_server.py --port 8080
```

### Neo4j Connection Failed

```bash
# Check Neo4j is running
curl http://localhost:7474

# Check credentials
docker compose logs neo4j
```

### Rate Limit Errors (429)

```bash
# Reduce concurrency
export SEMAPHORE_LIMIT=5
uv run graphiti_rest_server.py
```

## Next Steps

- Read [QUICKSTART.md](QUICKSTART.md) for usage examples
- Read [README.md](README.md) for full API documentation
- Try [example_rest_client.py](example_rest_client.py) for Python client examples

## Dependencies

All dependencies are managed via `pyproject.toml`:

- **FastAPI**: REST API framework
- **graphiti-core**: Graph operations (from PyPI)
- **OpenAI**: LLM client
- **Azure Identity**: Azure OpenAI support
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

Lock file: `uv.lock` (committed to repo)
