## GraphitiClient

A Swift client library for the Graphiti REST API, built with Swift Concurrency and HTTPTypes.

### Features

- ✅ **Swift 6** with strict concurrency checking
- ✅ **HTTPTypes** for modern HTTP handling
- ✅ **Pluggable Transport** - Choose between URLSession or AsyncHTTPClient
- ✅ **Cross-platform** - macOS 15+, iOS 18+, Linux
- ✅ **Actor-isolated** - Thread-safe by design
- ✅ **Fully typed** - Comprehensive Codable models
- ✅ **Async/await** - Native Swift concurrency

### Installation

#### Swift Package Manager

```swift
dependencies: [
    .package(url: "https://github.com/getzep/graphiti.git", from: "1.0.0")
]
```

### Usage

#### Basic Setup (URLSession)

```swift
import GraphitiClient

// Initialize with URLSession (default, works on Apple platforms)
let client = GraphitiClient(
    baseURL: URL(string: "http://localhost:8000")!
)

// Add a memory
let request = AddMemoryRequest(
    name: "Meeting Notes",
    episodeBody: "Had a great meeting with Sarah about the project.",
    groupId: "my-knowledge-base",
    source: .text
)

let response = try await client.addMemory(request)
print(response.message)
```

#### Using AsyncHTTPClient (Linux/Server)

```swift
import GraphitiClient
import AsyncHTTPClient

// Initialize with AsyncHTTPClient
let httpClient = HTTPClient(eventLoopGroupProvider: .singleton)
let transport = AsyncHTTPClientTransport(client: httpClient)

let client = GraphitiClient(
    baseURL: URL(string: "http://localhost:8000")!,
    transport: transport
)

// Use the client...
try await client.addMemory(request)

// Cleanup
try await transport.shutdown()
```

#### Search Operations

```swift
// Search for nodes
let nodeResults = try await client.searchNodes(
    query: "Sarah",
    groupIds: ["my-knowledge-base"],
    maxNodes: 10,
    entity: "Preference"
)

for node in nodeResults.nodes {
    print("\(node.name): \(node.summary)")
}

// Search for facts
let factResults = try await client.searchFacts(
    query: "project decisions",
    groupIds: ["my-knowledge-base"],
    maxFacts: 20
)

for fact in factResults.facts {
    print(fact.fact)
}
```

#### Episode Management

```swift
// Get recent episodes
let episodes = try await client.getEpisodes(
    groupId: "my-knowledge-base",
    lastN: 10
)

// Delete an episode
try await client.deleteEpisode(uuid: "episode-uuid")

// Get entity edge
let edge = try await client.getEntityEdge(uuid: "edge-uuid")
print(edge.fact)

// Delete entity edge
try await client.deleteEntityEdge(uuid: "edge-uuid")
```

#### Admin Operations

```swift
// Check server status
let status = try await client.getStatus()
print("Server: \(status.status)")
print("Model: \(status.config?.model ?? "unknown")")

// Health check
let isHealthy = try await client.healthCheck()

// Clear graph (use with caution!)
try await client.clearGraph()
```

### Advanced Usage

#### Custom Headers

```swift
import HTTPTypes

var headers: HTTPFields = [:]
headers[.authorization] = "Bearer your-api-key"

let client = GraphitiClient(
    baseURL: URL(string: "http://localhost:8000")!,
    additionalHeaders: headers
)
```

#### Custom Transport

Implement the `HTTPTransport` protocol for custom HTTP handling:

```swift
import GraphitiClient

struct CustomTransport: HTTPTransport {
    func execute(
        request: HTTPRequest,
        body: Data?
    ) async throws -> (Data, HTTPResponse) {
        // Your custom implementation
    }
}

let client = GraphitiClient(
    baseURL: URL(string: "http://localhost:8000")!,
    transport: CustomTransport()
)
```

### Architecture

```
GraphitiClient/
├── Models/
│   └── GraphitiModels.swift       # Request/Response types
├── Core/
│   └── GraphitiError.swift        # Error types
├── Transport/
│   ├── HTTPTransport.swift        # Protocol + HTTPRequestBuilder
│   ├── URLSessionTransport.swift  # URLSession implementation
│   └── AsyncHTTPClientTransport.swift  # AsyncHTTPClient implementation
└── Client/
    └── GraphitiClient.swift       # Main actor-based client
```

### Error Handling

All errors conform to `GraphitiError`:

```swift
do {
    try await client.addMemory(request)
} catch GraphitiError.serverError(let errorResponse) {
    print("Server error: \(errorResponse.error)")
} catch GraphitiError.httpError(let status, let message) {
    print("HTTP \(status.code): \(message ?? "unknown")")
} catch GraphitiError.networkError(let error) {
    print("Network error: \(error)")
} catch {
    print("Unexpected error: \(error)")
}
```

### Platform Support

| Platform | Minimum Version | Transport |
|----------|----------------|-----------|
| macOS | 15.0 | URLSession, AsyncHTTPClient |
| iOS | 18.0 | URLSession, AsyncHTTPClient |
| watchOS | 11.0 | URLSession |
| tvOS | 18.0 | URLSession |
| visionOS | 2.0 | URLSession |
| Linux | - | AsyncHTTPClient |

### Thread Safety

`GraphitiClient` is an `actor`, ensuring all operations are thread-safe:

```swift
// Safe to use from multiple tasks
Task {
    try await client.addMemory(request1)
}

Task {
    try await client.searchFacts(query: "test")
}
```

### Examples

See `Tests/GraphitiClientTests/` for comprehensive examples.

### Requirements

- Swift 6.0+
- swift-http-types 1.3.0+
- async-http-client 1.23.0+ (for AsyncHTTPClient transport)

### License

Same as the parent Graphiti project.

### Contributing

Contributions welcome! Please ensure:
- Swift 6 strict concurrency compliance
- Full test coverage
- Documentation for public APIs
- Cross-platform compatibility
