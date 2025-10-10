# Architecture Documentation

## Overview

The Graphiti REST Server is a professionally structured FastAPI application that provides a REST API interface to Graphiti's temporal knowledge graph capabilities.

## Project Structure

```
rest_server/
├── graphiti_server/              # Main application package
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── models.py                 # Pydantic models (requests/responses)
│   ├── main.py                   # FastAPI app + lifespan
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── client.py             # Graphiti client wrapper
│   │   └── queue.py              # Episode queue management
│   └── api/                      # API layer
│       ├── __init__.py
│       ├── deps.py               # FastAPI dependencies
│       └── routes/               # API endpoints
│           ├── __init__.py
│           ├── memory.py         # Memory/episode endpoints
│           ├── search.py         # Search endpoints
│           └── admin.py          # Admin endpoints
├── run.py                        # CLI entry point
├── pyproject.toml                # Project dependencies
├── Dockerfile                    # Docker build
├── docker-compose.yml            # Docker Compose setup
└── example_rest_client.py        # Python client example
```

## Design Principles

### 1. **Separation of Concerns**

Each module has a single, well-defined responsibility:

- **config.py**: Configuration management (env vars, CLI args)
- **models.py**: Data validation and serialization (Pydantic)
- **core/**: Business logic (Graphiti operations, queuing)
- **api/**: HTTP layer (routes, request handling)

### 2. **Dependency Injection**

FastAPI dependencies are used for:
- Graphiti client access
- Configuration access
- Clean testability

### 3. **Layered Architecture**

```
┌─────────────────────────────────┐
│   API Layer (routes/)           │  ← HTTP endpoints
├─────────────────────────────────┤
│   Core Layer (core/)            │  ← Business logic
├─────────────────────────────────┤
│   Graphiti Core (PyPI)          │  ← Graph operations
├─────────────────────────────────┤
│   Neo4j Database                │  ← Data storage
└─────────────────────────────────┘
```

### 4. **Clean Imports**

- No circular dependencies
- Clear module boundaries
- Type hints throughout

## Key Components

### Configuration Management (`config.py`)

Hierarchical configuration system:

```python
ServerConfig
├── LLMConfig           # OpenAI settings
├── EmbedderConfig      # Embedding settings
├── Neo4jConfig         # Database settings
└── Settings            # App settings
```

Environment variables override defaults:
```bash
OPENAI_API_KEY=...
MODEL_NAME=gpt-4o-mini
NEO4J_URI=bolt://localhost:7687
```

### Client Wrapper (`core/client.py`)

Wraps Graphiti core functionality:

```python
class GraphitiClient:
    - initialize()           # Setup
    - close()               # Cleanup
    - client                # Access to Graphiti
    - format_fact_result()  # Serialization
```

Benefits:
- Single initialization point
- Consistent error handling
- Easy mocking for tests

### Episode Queue (`core/queue.py`)

Per-group-id sequential processing:

```python
class EpisodeQueue:
    - add_episode()         # Queue episode
    - start_worker()        # Start processing
    - stop()                # Graceful shutdown
```

Why per-group?
- Prevents race conditions
- Maintains consistency
- Parallel processing across groups

### API Routes

Three route modules:

1. **memory.py** - Episode CRUD
   - POST /api/v1/memory
   - GET /api/v1/episodes/{group_id}
   - DELETE /api/v1/episode/{uuid}
   - DELETE /api/v1/entity-edge/{uuid}
   - GET /api/v1/entity-edge/{uuid}

2. **search.py** - Search operations
   - GET /api/v1/search/nodes
   - GET /api/v1/search/facts

3. **admin.py** - Admin/health
   - GET /healthcheck
   - GET /api/v1/status
   - POST /api/v1/clear

### Lifespan Management (`main.py`)

FastAPI lifespan handles:

```python
@asynccontextmanager
async def lifespan(app):
    # Startup
    - Initialize config
    - Create Graphiti client
    - Build DB indices

    yield

    # Shutdown
    - Stop all queues
    - Close client
    - Cleanup resources
```

## Data Flow

### Adding an Episode

```
1. Client → POST /api/v1/memory
2. Validate request (Pydantic)
3. Get/create queue for group_id
4. Add episode to queue
5. Return 202 Accepted
6. Background: Process episode
   - Call Graphiti.add_episode()
   - Extract entities
   - Build graph
```

### Searching

```
1. Client → GET /api/v1/search/facts
2. Validate params
3. Call Graphiti.search()
4. Format results
5. Return 200 OK
```

## Error Handling

Consistent error responses:

```python
# Success
{
    "message": "...",
    "success": true
}

# Error
{
    "error": "...",
    "success": false
}
```

HTTP status codes:
- 200: Success
- 202: Accepted (queued)
- 400: Bad request
- 404: Not found
- 500: Internal error

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
MODEL_NAME=gpt-4o-mini
SMALL_MODEL_NAME=gpt-4o-mini
LLM_TEMPERATURE=1.0
EMBEDDER_MODEL_NAME=text-embedding-3-small

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SEMAPHORE_LIMIT=10
```

### CLI Arguments

```bash
uv run python run.py \
  --host 0.0.0.0 \
  --port 8000 \
  --group-id my-kb \
  --use-custom-entities \
  --reload
```

## Testing Strategy

### Unit Tests

Test individual components:

```python
# Test config loading
def test_llm_config_from_env():
    config = LLMConfig.from_env()
    assert config.model == "gpt-4o-mini"

# Test queue
async def test_episode_queue():
    queue = EpisodeQueue("test")
    # ...
```

### Integration Tests

Test API endpoints:

```python
from fastapi.testclient import TestClient
from graphiti_server.main import app

def test_add_memory():
    client = TestClient(app)
    response = client.post("/api/v1/memory", json={...})
    assert response.status_code == 202
```

## Deployment

### Docker

```bash
# Build
docker build -t graphiti-rest:latest .

# Run
docker compose up
```

### Local Development

```bash
# Install dependencies
uv sync

# Run with auto-reload
uv run python run.py --reload

# Or use uvicorn directly
uv run uvicorn graphiti_server.main:app --reload
```

## Extensibility

### Adding New Endpoints

1. Create route in `api/routes/`
2. Add to router in `api/routes/__init__.py`
3. Include router in `main.py`

Example:

```python
# api/routes/analytics.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/stats")
async def get_stats():
    # Implementation
    pass
```

### Adding New Entity Types

Edit `models.py`:

```python
class Task(BaseModel):
    """A task to be completed."""
    title: str
    due_date: datetime

ENTITY_TYPES["Task"] = Task
```

### Custom Middleware

Add to `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)
```

## Performance Considerations

### Concurrency

- Episodes processed sequentially per group_id
- Different groups process in parallel
- Configurable via `SEMAPHORE_LIMIT`

### Caching

Currently no caching implemented. Consider:
- Redis for search results
- In-memory cache for config
- Database query caching

### Monitoring

Add metrics:
- Queue sizes
- Processing times
- Error rates
- API latency

## Security Considerations

### Current State

- No authentication/authorization
- No rate limiting
- No input sanitization beyond Pydantic

### Recommendations

1. **Add API Key Auth**
2. **Implement rate limiting**
3. **Add CORS middleware**
4. **Validate graph data**
5. **Audit logging**

## Future Improvements

1. **Batch Operations**: Add bulk episode endpoints
2. **Webhooks**: Notify on episode completion
3. **Streaming**: SSE for real-time updates
4. **GraphQL**: Alternative API interface
5. **Metrics**: Prometheus integration
6. **Caching**: Redis integration
7. **Auth**: JWT/OAuth2 support

## Migration from Old Structure

Old (monolithic):
```
graphiti_rest_server.py  (1,200+ lines)
```

New (modular):
```
graphiti_server/
├── config.py      (~150 lines)
├── models.py      (~150 lines)
├── core/
│   ├── client.py  (~100 lines)
│   └── queue.py   (~100 lines)
└── api/
    └── routes/
        ├── memory.py  (~150 lines)
        ├── search.py  (~100 lines)
        └── admin.py   (~70 lines)
```

Benefits:
- **Easier to navigate** - Find code quickly
- **Better testing** - Test components in isolation
- **Clearer ownership** - Each file has one purpose
- **Simpler maintenance** - Change one file at a time
- **No Azure code** - Removed unnecessary dependencies

## Conclusion

The refactored architecture follows Python best practices:

✅ **Single Responsibility Principle** - Each module has one job
✅ **Dependency Inversion** - Depends on abstractions
✅ **Clean Code** - Readable, maintainable
✅ **Type Safety** - Full type hints
✅ **Testability** - Easy to mock and test
✅ **Scalability** - Easy to extend

The result is a professional, production-ready codebase that's easy to understand, maintain, and extend.
