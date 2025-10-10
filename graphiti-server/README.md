# Graphiti REST API Documentation

This is a feature-complete REST API implementation of Graphiti with the same capabilities as the MCP server.

## Quick Start

### Using Python directly

```bash
cd rest_server

# Start the server
uv run graphiti_rest_server.py --use-custom-entities --group-id my-kb

# Or with custom settings
uv run graphiti_rest_server.py \
  --model gpt-4o-mini \
  --temperature 0.7 \
  --use-custom-entities \
  --group-id my-personal-kb \
  --port 8080
```

### Using Docker

```bash
# Build the Docker image
docker build -t graphiti-rest:latest .

# Run with Docker Compose (includes Neo4j)
docker compose up
```

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### 1. Add Memory (Episode)

**Endpoint:** `POST /api/v1/memory`

**Description:** Add an episode to the knowledge graph. Returns immediately and processes in the background.

**Request Body:**
```json
{
  "name": "Meeting Notes",
  "episode_body": "Had a meeting with Sarah about the GraphDB project...",
  "source": "text",
  "source_description": "meeting notes",
  "group_id": "my-kb"
}
```

**Parameters:**
- `name` (string, required): Episode name (max 200 chars)
- `episode_body` (string, required): Content of the episode
- `source` (enum, optional): "text" | "json" | "message" (default: "text")
- `source_description` (string, optional): Description of the source
- `group_id` (string, optional): Group ID for namespace isolation
- `uuid` (string, optional): Custom UUID for the episode

**Response:** `202 Accepted`
```json
{
  "message": "Episode 'Meeting Notes' queued for processing (position: 1)",
  "success": true
}
```

**Examples:**

```bash
# Plain text note
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Update",
    "episode_body": "Team decided to use Neo4j instead of PostgreSQL for the graph database.",
    "source": "text",
    "group_id": "project-alpha"
  }'

# JSON structured data
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Profile",
    "episode_body": "{\"company\": {\"name\": \"Acme Corp\"}, \"products\": [{\"id\": \"P001\", \"name\": \"Widget\"}]}",
    "source": "json",
    "source_description": "CRM export",
    "group_id": "customers"
  }'

# Message/conversation
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Support Chat",
    "episode_body": "user: How do I reset my password?\nassistant: You can reset it at /reset-password",
    "source": "message",
    "group_id": "support-tickets"
  }'
```

---

### 2. Search Nodes

**Endpoint:** `GET /api/v1/search/nodes`

**Description:** Search for entity nodes with their summaries.

**Query Parameters:**
- `query` (string, required): Search query
- `group_ids` (array[string], optional): Filter by group IDs
- `max_nodes` (integer, optional): Max results (1-100, default: 10)
- `center_node_uuid` (string, optional): Center search around a specific node
- `entity` (string, optional): Filter by entity type ("Preference" | "Procedure" | "Requirement")

**Response:** `200 OK`
```json
{
  "message": "Nodes retrieved successfully",
  "nodes": [
    {
      "uuid": "abc123",
      "name": "Sarah",
      "summary": "Backend developer who prefers Python...",
      "labels": ["Person", "Preference"],
      "group_id": "my-kb",
      "created_at": "2025-03-09T10:00:00Z",
      "attributes": {}
    }
  ],
  "success": true
}
```

**Examples:**

```bash
# Basic search
curl "http://localhost:8000/api/v1/search/nodes?query=Sarah&max_nodes=5"

# Search with entity filter (only Preferences)
curl "http://localhost:8000/api/v1/search/nodes?query=Python&entity=Preference"

# Search specific group
curl "http://localhost:8000/api/v1/search/nodes?query=database&group_ids=project-alpha"

# Search around a center node
curl "http://localhost:8000/api/v1/search/nodes?query=related&center_node_uuid=abc123"
```

---

### 3. Search Facts

**Endpoint:** `GET /api/v1/search/facts`

**Description:** Search for facts (relationships between entities).

**Query Parameters:**
- `query` (string, required): Search query
- `group_ids` (array[string], optional): Filter by group IDs
- `max_facts` (integer, optional): Max results (1-100, default: 10)
- `center_node_uuid` (string, optional): Center search around a specific node

**Response:** `200 OK`
```json
{
  "message": "Facts retrieved successfully",
  "facts": [
    {
      "uuid": "fact123",
      "name": "Sarah prefers Python",
      "fact": "Sarah prefers Python for backend development",
      "valid_at": "2025-03-09T10:00:00Z",
      "invalid_at": null,
      "created_at": "2025-03-09T10:00:00Z",
      "expired_at": null,
      "source_node_uuid": "node1",
      "target_node_uuid": "node2"
    }
  ],
  "success": true
}
```

**Examples:**

```bash
# Basic fact search
curl "http://localhost:8000/api/v1/search/facts?query=Sarah+preferences"

# Search with limit
curl "http://localhost:8000/api/v1/search/facts?query=technology+choices&max_facts=20"

# Search specific groups
curl "http://localhost:8000/api/v1/search/facts?query=database&group_ids=project-alpha&group_ids=project-beta"
```

---

### 4. Get Entity Edge by UUID

**Endpoint:** `GET /api/v1/entity-edge/{uuid}`

**Description:** Retrieve a specific entity edge (fact) by UUID.

**Response:** `200 OK`
```json
{
  "uuid": "fact123",
  "name": "Sarah prefers Python",
  "fact": "Sarah prefers Python for backend development",
  "valid_at": "2025-03-09T10:00:00Z",
  "invalid_at": null,
  "created_at": "2025-03-09T10:00:00Z",
  "expired_at": null,
  "source_node_uuid": "node1",
  "target_node_uuid": "node2"
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/entity-edge/fact123"
```

---

### 5. Get Episodes

**Endpoint:** `GET /api/v1/episodes/{group_id}`

**Description:** Get the most recent episodes for a group.

**Query Parameters:**
- `last_n` (integer, optional): Number of episodes to retrieve (1-100, default: 10)

**Response:** `200 OK`
```json
[
  {
    "uuid": "ep123",
    "name": "Meeting Notes",
    "content": "Had a meeting...",
    "source": "text",
    "group_id": "my-kb",
    "created_at": "2025-03-09T10:00:00Z"
  }
]
```

**Examples:**

```bash
# Get last 10 episodes
curl "http://localhost:8000/api/v1/episodes/my-kb"

# Get last 50 episodes
curl "http://localhost:8000/api/v1/episodes/my-kb?last_n=50"
```

---

### 6. Delete Entity Edge

**Endpoint:** `DELETE /api/v1/entity-edge/{uuid}`

**Description:** Delete a specific entity edge (fact).

**Response:** `200 OK`
```json
{
  "message": "Entity edge with UUID fact123 deleted successfully",
  "success": true
}
```

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/entity-edge/fact123"
```

---

### 7. Delete Episode

**Endpoint:** `DELETE /api/v1/episode/{uuid}`

**Description:** Delete a specific episode.

**Response:** `200 OK`
```json
{
  "message": "Episode with UUID ep123 deleted successfully",
  "success": true
}
```

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/episode/ep123"
```

---

### 8. Clear Graph

**Endpoint:** `POST /api/v1/clear`

**Description:** Clear all data from the graph and rebuild indices.

**Response:** `200 OK`
```json
{
  "message": "Graph cleared successfully and indices rebuilt",
  "success": true
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/clear"
```

---

### 9. Server Status

**Endpoint:** `GET /api/v1/status`

**Description:** Get server status and configuration.

**Response:** `200 OK`
```json
{
  "status": "ok",
  "message": "Graphiti REST server is running and connected to Neo4j",
  "config": {
    "model": "gpt-4o-mini",
    "small_model": "gpt-4.1-nano",
    "temperature": 0.7,
    "default_group_id": "default",
    "custom_entities_enabled": true,
    "semaphore_limit": 10,
    "azure_openai_enabled": false
  }
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/status"
```

---

### 10. Healthcheck

**Endpoint:** `GET /healthcheck`

**Description:** Simple healthcheck for load balancers.

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

**Example:**

```bash
curl "http://localhost:8000/healthcheck"
```

---

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
MODEL_NAME=gpt-4o-mini  # Default: gpt-5-mini
SMALL_MODEL_NAME=gpt-4.1-nano  # Default: gpt-5-nano
LLM_TEMPERATURE=0.7  # Default: 1.0 (automatically set to None for gpt-5 models)
EMBEDDER_MODEL_NAME=text-embedding-3-small

# Azure OpenAI Configuration (Optional)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_USE_MANAGED_IDENTITY=false  # Set to true for managed identity

# Azure Embedding Configuration (Optional)
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small
AZURE_OPENAI_EMBEDDING_API_VERSION=2024-02-15-preview
AZURE_OPENAI_EMBEDDING_API_KEY=...  # Optional, falls back to OPENAI_API_KEY

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Performance Configuration
SEMAPHORE_LIMIT=10  # Concurrent operations (decrease if hitting rate limits)
```

### CLI Arguments

All environment variables can be overridden via CLI arguments:

```bash
uv run graphiti_rest_server.py \
  --model gpt-4o \
  --small-model gpt-4o-mini \
  --temperature 0.5 \
  --base-url https://api.openai.com/v1 \
  --group-id my-knowledge-base \
  --use-custom-entities \
  --host 0.0.0.0 \
  --port 8080
```

Available arguments:
- `--group-id`: Default group ID for episodes (default: "default")
- `--model`: LLM model name
- `--small-model`: Small LLM model name for cheaper operations
- `--temperature`: LLM temperature (0.0-2.0)
- `--base-url`: OpenAI API base URL
- `--use-custom-entities`: Enable custom entity types (Requirement, Preference, Procedure)
- `--destroy-graph`: Clear graph on startup
- `--host`: Server host (default: 0.0.0.0)
- `--port`: Server port (default: 8000)

### Automatic Temperature Configuration

**Important:** The server automatically sets `temperature` to `None` when using GPT-5 models.

GPT-5 models (e.g., `gpt-5-mini`, `gpt-5-nano`) have a different parameter structure than GPT-4 models. The server detects if the model name contains "gpt-5" (case-insensitive) and automatically sets `temperature` to `None` to ensure compatibility.

**Behavior:**
- **GPT-5 models** (`gpt-5-mini`, `gpt-5-nano`, etc.): `temperature = None` (ignores `LLM_TEMPERATURE` env var)
- **Other models** (`gpt-4o`, `gpt-4o-mini`, etc.): `temperature = 1.0` (or value from `LLM_TEMPERATURE`)

**Example:**
```bash
# Using GPT-5 (temperature will be None automatically)
export MODEL_NAME=gpt-5-mini
uv run graphiti_rest_server.py

# Using GPT-4 (temperature will be 0.7)
export MODEL_NAME=gpt-4o-mini
export LLM_TEMPERATURE=0.7
uv run graphiti_rest_server.py
```

---

## Custom Entity Types

When `--use-custom-entities` is enabled, Graphiti will automatically extract three special entity types:

### 1. Preference
User preferences, likes, and dislikes.

**Example:**
```json
{
  "name": "Sarah's Tech Stack",
  "episode_body": "Sarah mentioned she prefers Python over JavaScript for backend work.",
  "source": "text"
}
```

**Extracted Preference:**
- Category: "Programming Languages"
- Description: "Prefers Python over JavaScript for backend development"

### 2. Procedure
Step-by-step procedures and workflows.

**Example:**
```json
{
  "name": "Deployment Process",
  "episode_body": "To deploy: 1) Run tests, 2) Build Docker image, 3) Push to registry, 4) Update k8s manifest",
  "source": "text"
}
```

**Extracted Procedure:**
- Description: "Deployment process: run tests, build Docker image, push to registry, update Kubernetes manifest"

### 3. Requirement
Project requirements and specifications.

**Example:**
```json
{
  "name": "API Requirements",
  "episode_body": "The GraphDB project must support at least 1000 concurrent users with sub-second response times.",
  "source": "text"
}
```

**Extracted Requirement:**
- Project: "GraphDB"
- Description: "Must support at least 1000 concurrent users with sub-second response times"

---

## Python Client Example

```python
import requests
from typing import Literal

class GraphitiClient:
    def __init__(self, base_url: str = "http://localhost:8000", group_id: str = "default"):
        self.base_url = base_url
        self.group_id = group_id

    def add_memory(
        self,
        name: str,
        episode_body: str,
        source: Literal["text", "json", "message"] = "text",
        source_description: str = ""
    ):
        """Add an episode to memory"""
        response = requests.post(
            f"{self.base_url}/api/v1/memory",
            json={
                "name": name,
                "episode_body": episode_body,
                "source": source,
                "source_description": source_description,
                "group_id": self.group_id
            }
        )
        return response.json()

    def search_facts(self, query: str, max_facts: int = 10):
        """Search for facts"""
        response = requests.get(
            f"{self.base_url}/api/v1/search/facts",
            params={
                "query": query,
                "group_ids": [self.group_id],
                "max_facts": max_facts
            }
        )
        return response.json()

    def search_nodes(self, query: str, max_nodes: int = 10, entity: str = ""):
        """Search for nodes"""
        response = requests.get(
            f"{self.base_url}/api/v1/search/nodes",
            params={
                "query": query,
                "group_ids": [self.group_id],
                "max_nodes": max_nodes,
                "entity": entity
            }
        )
        return response.json()

    def get_episodes(self, last_n: int = 10):
        """Get recent episodes"""
        response = requests.get(
            f"{self.base_url}/api/v1/episodes/{self.group_id}",
            params={"last_n": last_n}
        )
        return response.json()

# Usage
client = GraphitiClient(group_id="my-personal-kb")

# Add a note
result = client.add_memory(
    name="Meeting with Sarah",
    episode_body="Sarah prefers Python. We decided to use Neo4j for the project.",
    source="text"
)
print(result)

# Search for facts
facts = client.search_facts("Sarah preferences")
print(facts)

# Search for preference entities
preferences = client.search_nodes("Python", entity="Preference")
print(preferences)
```

---

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These provide interactive documentation where you can test all endpoints directly in your browser.

---

## Comparison with MCP Server

| Feature | REST API | MCP Server |
|---------|----------|------------|
| Protocol | HTTP/REST | MCP (stdio/SSE) |
| Use Case | Direct API calls | AI assistant integration |
| Interactive Docs | ✅ Swagger/ReDoc | ❌ |
| Custom Entities | ✅ | ✅ |
| Azure OpenAI | ✅ | ✅ |
| Queue System | ✅ Per-group | ✅ Per-group |
| Configuration | ✅ Same | ✅ Same |

**When to use REST API:**
- Building web applications
- Direct programmatic access
- Custom integrations
- Testing and debugging
- No LLM tool-call overhead

**When to use MCP Server:**
- Integration with Claude Desktop, Cursor, etc.
- AI assistant workflows
- Tool-call based interactions

---

## Performance Tuning

### Rate Limit Errors (429)

If you're hitting LLM provider rate limits:

```bash
# Decrease concurrency
export SEMAPHORE_LIMIT=5
uv run graphiti_rest_server.py
```

### Increase Performance

If you have high rate limits:

```bash
# Increase concurrency
export SEMAPHORE_LIMIT=20
uv run graphiti_rest_server.py
```

### Episode Queue Management

Episodes are processed sequentially per `group_id` to prevent race conditions. You can have multiple groups processing in parallel.

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error description here",
  "success": false
}
```

HTTP Status Codes:
- `200 OK` - Success
- `202 Accepted` - Queued for processing
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Server not ready

---

## License

Same as parent Graphiti project.
