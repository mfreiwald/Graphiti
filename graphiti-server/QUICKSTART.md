# Graphiti REST API - Quick Start Guide

## 🚀 5-Minute Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# 2. Start everything (Neo4j + REST server)
cd rest_server
docker compose up

# 3. Server is ready at http://localhost:8000
```

### Option 2: Local Python

```bash
# 1. Install dependencies
cd rest_server
uv sync

# 2. Start server
uv run graphiti_rest_server.py --use-custom-entities --group-id my-kb

# 3. Server is ready at http://localhost:8000
```

---

## ✅ Verify Installation

```bash
# Check server status
curl http://localhost:8000/api/v1/status

# Should return:
# {
#   "status": "ok",
#   "message": "Graphiti REST server is running and connected to Neo4j",
#   "config": { ... }
# }
```

---

## 📝 First Steps

### 1. Add Your First Note

```bash
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Note",
    "episode_body": "I prefer Python for backend development. FastAPI is great for building REST APIs.",
    "source": "text",
    "group_id": "my-kb"
  }'
```

**Response:**
```json
{
  "message": "Episode 'My First Note' queued for processing (position: 1)",
  "success": true
}
```

### 2. Search for Facts

Wait ~5 seconds for processing, then:

```bash
curl "http://localhost:8000/api/v1/search/facts?query=Python&max_facts=5"
```

**Response:**
```json
{
  "message": "Facts retrieved successfully",
  "facts": [
    {
      "uuid": "...",
      "fact": "User prefers Python for backend development",
      "name": "Python preference",
      ...
    }
  ],
  "success": true
}
```

### 3. Search for Nodes

```bash
curl "http://localhost:8000/api/v1/search/nodes?query=Python&entity=Preference"
```

**Response:**
```json
{
  "message": "Nodes retrieved successfully",
  "nodes": [
    {
      "uuid": "...",
      "name": "Python",
      "summary": "Programming language preferred by user for backend development",
      "labels": ["Preference"],
      ...
    }
  ],
  "success": true
}
```

---

## 🐍 Using Python Client

### Install requests

```bash
pip install requests
```

### Simple Example

```python
import requests

# Add a note
response = requests.post(
    "http://localhost:8000/api/v1/memory",
    json={
        "name": "Meeting Notes",
        "episode_body": "Sarah prefers Neo4j for graph storage. We decided to use Python.",
        "source": "text",
        "group_id": "work-notes"
    }
)
print(response.json())

# Search
import time
time.sleep(3)  # Wait for processing

facts = requests.get(
    "http://localhost:8000/api/v1/search/facts",
    params={"query": "Sarah", "max_facts": 5}
).json()

for fact in facts['facts']:
    print(f"- {fact['fact']}")
```

### Using the Example Client

```bash
# Run the example client
python example_rest_client.py
```

This demonstrates:
- Adding text notes
- Adding JSON data
- Searching facts and nodes
- Getting recent episodes
- Filtering by entity types

---

## 🎯 Common Use Cases

### Personal Knowledge Base

```python
from example_rest_client import GraphitiRestClient

client = GraphitiRestClient(
    base_url="http://localhost:8000",
    group_id="michael-kb"
)

# Daily notes
client.add_memory(
    name="Daily Learning",
    episode_body="""
    Today I learned about temporal knowledge graphs.
    Graphiti uses bi-temporal modeling which tracks both:
    - When an event occurred (valid_at)
    - When we learned about it (created_at)
    """,
    source="text"
)

# Search what you've learned
results = client.search_facts("temporal graphs")
```

### Meeting Notes

```python
# Add meeting notes
client.add_memory(
    name="Team Standup - 2025-03-09",
    episode_body="""
    Attendees: Sarah (Backend), Michael (Full-stack)

    Decisions:
    - Using Neo4j for graph database
    - FastAPI for REST endpoints
    - Deploy to Docker

    Sarah's Preferences:
    - Prefers Python over Node.js
    - Likes type hints and Pydantic

    Action Items:
    - [ ] Set up Neo4j cluster (Sarah)
    - [ ] Create API endpoints (Michael)
    - [ ] Write tests (Both)
    """,
    source="text",
    source_description="standup meeting"
)

# Later, search for action items
actions = client.search_facts("action items Michael")

# Or search for preferences
prefs = client.search_nodes("Sarah", entity="Preference")
```

### Project Requirements

```python
# Add requirements (automatically extracted with --use-custom-entities)
client.add_memory(
    name="GraphDB API Requirements",
    episode_body="""
    The GraphDB API must meet the following requirements:

    1. Performance: Support 1000+ concurrent users
    2. Response time: < 100ms for graph queries
    3. Security: API key authentication required
    4. Availability: 99.9% uptime SLA
    5. Scalability: Horizontal scaling via load balancer

    Project: GraphDB API v2
    """,
    source="text"
)

# Search requirements
reqs = client.search_nodes("performance", entity="Requirement")
```

### Code Snippets & Procedures

```python
# Add a procedure (automatically extracted)
client.add_memory(
    name="Deployment Procedure",
    episode_body="""
    To deploy the GraphDB API to production:

    1. Run tests: `pytest tests/ -v`
    2. Build Docker image: `docker build -t api:latest .`
    3. Push to registry: `docker push registry.io/api:latest`
    4. Update k8s manifest: `kubectl apply -f deploy.yaml`
    5. Verify deployment: `kubectl rollout status deployment/api`
    6. Run smoke tests: `pytest tests/smoke/ --env=prod`

    Always check logs after deployment!
    """,
    source="text"
)

# Later, retrieve the procedure
procedure = client.search_nodes("deployment", entity="Procedure")
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini
LLM_TEMPERATURE=0.7

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Performance
SEMAPHORE_LIMIT=10
```

### CLI Arguments

```bash
uv run graphiti_rest_server.py \
  --model gpt-4o-mini \
  --temperature 0.5 \
  --use-custom-entities \
  --group-id my-kb \
  --port 8080
```

---

## 📊 Interactive Documentation

Visit these URLs once the server is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Both provide interactive API documentation where you can test endpoints directly.

---

## 🐛 Troubleshooting

### Server won't start

```bash
# Check if Neo4j is running
curl http://localhost:7474

# Check logs
docker compose logs graphiti-rest

# Verify environment variables
curl http://localhost:8000/api/v1/status
```

### 429 Rate Limit Errors

```bash
# Decrease concurrency
export SEMAPHORE_LIMIT=5
uv run graphiti_rest_server.py
```

### Episodes not being processed

```bash
# Check queue status
curl http://localhost:8000/api/v1/status

# Episodes are processed per group_id sequentially
# Wait a few seconds and try searching again
```

### Connection refused

```bash
# Make sure server is running
curl http://localhost:8000/healthcheck

# If using Docker, check network
docker compose ps
```

---

## 📚 Next Steps

1. **Read the full API documentation:** [REST_API.md](REST_API.md)
2. **Explore custom entities:** Run with `--use-custom-entities`
3. **Browse your graph:** http://localhost:7474 (Neo4j Browser)
4. **Build a client:** Use `example_rest_client.py` as a template
5. **Integrate with your app:** See Python client examples

---

## 🆚 REST API vs MCP Server

| Feature | REST API | MCP Server |
|---------|----------|------------|
| **Use Case** | Direct API integration | AI assistant integration |
| **Pros** | No LLM overhead, full control | Natural language interface |
| **Cons** | Manual API calls | LLM tool-call errors |
| **Best For** | Production apps, testing | Claude Desktop, Cursor |

**Recommendation for personal KB:** Use REST API for predictable, fast, cost-effective operations.

---

## 💡 Tips

1. **Use group_id for namespaces:** Separate work, personal, projects
2. **Enable custom entities:** Get automatic Preference/Procedure/Requirement extraction
3. **Wait for processing:** Episodes are queued (~2-5 seconds processing time)
4. **Use structured notes:** Markdown/JSON helps entity extraction
5. **Monitor rate limits:** Adjust `SEMAPHORE_LIMIT` as needed

---

## 🤝 Need Help?

- **Issues:** https://github.com/getzep/graphiti/issues
- **Documentation:** [REST_API.md](REST_API.md)
- **Example Client:** [example_rest_client.py](example_rest_client.py)

Happy graph building! 🚀
