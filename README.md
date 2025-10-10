# Graphiti Client & Server

A monorepo containing a REST API server and Swift client SDK for [Graphiti](https://github.com/getzep/graphiti) - a temporally-aware knowledge graph framework.

## 📦 Packages

### [`graphiti-server/`](./graphiti-server) ![Server Version](https://img.shields.io/github/v/tag/mfreiwald/Graphiti?filter=server%2F*&label=version)
FastAPI-based REST server for Graphiti knowledge graphs.

**Features:**
- RESTful API for graph operations (add memory, search nodes/facts)
- Custom entity types (Preference, Procedure, Requirement)
- Per-group episode queuing to prevent race conditions
- Docker & Docker Compose support with Neo4j
- Auto-configures temperature for GPT-5 models

**Quick Start:**
```bash
# Using Docker
docker pull ghcr.io/mfreiwald/Graphiti/graphiti-server:latest
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... ghcr.io/mfreiwald/Graphiti/graphiti-server:latest

# Using Docker Compose
cd graphiti-server
docker compose up
```

**API Docs:** http://localhost:8000/docs

---

### [`graphiti-swift/`](./graphiti-swift) ![Swift Version](https://img.shields.io/github/v/tag/mfreiwald/Graphiti?filter=swift%2F*&label=version)
Swift 6 client SDK for the Graphiti REST API.

**Features:**
- Actor-based client for thread safety
- Pluggable transport (URLSession or AsyncHTTPClient)
- Full API coverage with type-safe models
- macOS 26+, iOS 26+, watchOS 26+, tvOS 26+, visionOS 26+, Linux support

**Installation:**
```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/mfreiwald/Graphiti", from: "1.0.0")
]
```

**Quick Start:**
```swift
import GraphitiClient

let client = GraphitiClient(
    baseURL: URL(string: "http://localhost:8000")!
)

let request = AddMemoryRequest(
    name: "Meeting Notes",
    episodeBody: "Discussed the new project...",
    groupId: "my-kb",
    source: .text
)

let response = try await client.addMemory(request)
```

---

## 🚀 Getting Started

### 1. Start the REST Server

```bash
cd rest_server
docker compose up -d
```

The server will be available at `http://localhost:8000`

### 2. Use the Swift Client

Add to your `Package.swift`:
```swift
dependencies: [
    .package(path: "../graphiti-swift")
]
```

Or build it directly:
```bash
cd graphiti-swift
swift build
swift test
```

---

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-5-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### Temperature Auto-Configuration

The server automatically sets `temperature=None` for GPT-5 models and `temperature=1.0` for other models.

---

## 📖 Documentation

- **REST Server:** [graphiti-server/README.md](./graphiti-server/README.md)
- **Swift SDK:** [graphiti-swift/README.md](./graphiti-swift/README.md)
- **API Docs:** http://localhost:8000/docs (when server is running)
- **Release Guide:** [.github/RELEASE.md](./.github/RELEASE.md)
- **CI/CD Workflows:** [.github/workflows/README.md](./.github/workflows/README.md)

---

## 🚀 Releases

This monorepo uses independent versioning for each package:

- **Server releases**: Tagged as `server/v1.0.0`
  - Docker images: `ghcr.io/mfreiwald/Graphiti/graphiti-server:1.0.0`
  - [View releases](https://github.com/mfreiwald/Graphiti/releases?q=server)

- **Swift SDK releases**: Tagged as `swift/v1.0.0`
  - Swift Package Manager compatible
  - [View releases](https://github.com/mfreiwald/Graphiti/releases?q=swift)

### Quick Release

```bash
# Release REST Server
git tag server/v1.0.0
git push origin server/v1.0.0

# Release Swift SDK
git tag swift/v1.0.0
git push origin swift/v1.0.0
```

See [Release Guide](.github/RELEASE.md) for details.

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Swift Client   │  (macOS/iOS/Linux apps)
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  REST Server    │  (FastAPI + Graphiti Core)
└────────┬────────┘
         │ Bolt
         ▼
┌─────────────────┐
│     Neo4j       │  (Graph Database)
└─────────────────┘
```

---

## 💡 Use Cases

- **Personal Knowledge Base:** Store notes, thoughts, and ideas
- **Meeting Notes:** Extract entities and relationships from conversations
- **Project Documentation:** Track requirements, procedures, and preferences
- **Customer Data:** Build relationship graphs from CRM data

---

## 📝 License

Uses [graphiti-core](https://github.com/getzep/graphiti) under the hood.
