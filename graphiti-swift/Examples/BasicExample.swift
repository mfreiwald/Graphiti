import Foundation
import GraphitiClient

@main
struct BasicExample {
    static func main() async throws {
        // Initialize the client
        let client = GraphitiClient(
            baseURL: URL(string: "http://localhost:8000")!
        )

        print("🚀 Graphiti Client Example\n")

        // 1. Check server status
        print("1. Checking server status...")
        let status = try await client.getStatus()
        print("   ✅ Server is \(status.status)")
        if let config = status.config {
            print("   Model: \(config.model)")
            print("   Temperature: \(config.temperature)")
        }
        print()

        // 2. Add a memory
        print("2. Adding a memory...")
        let addRequest = AddMemoryRequest(
            name: "Meeting with Sarah",
            episodeBody: """
            Had a productive meeting with Sarah about the Graphiti project.
            She prefers Python for backend development.
            We decided to use Neo4j as the graph database.
            Deadline is end of March 2025.
            """,
            groupId: "swift-example",
            source: .text,
            sourceDescription: "meeting notes"
        )

        let addResponse = try await client.addMemory(addRequest)
        print("   ✅ \(addResponse.message)")
        print()

        // 3. Wait a bit for processing
        print("3. Waiting for processing...")
        try await Task.sleep(for: .seconds(15))
        print("   ✅ Done")
        print()

        // 4. Search for facts
        print("4. Searching for facts about Sarah...")
        let factResults = try await client.searchFacts(
            query: "Sarah preferences",
            groupIds: ["swift-example"],
            maxFacts: 5
        )

        print("   ✅ Found \(factResults.facts.count) facts:")
        for fact in factResults.facts {
            print("   - \(fact.fact)")
        }
        print()

        // 5. Search for nodes
        print("5. Searching for nodes...")
        let nodeResults = try await client.searchNodes(
            query: "Python Neo4j",
            groupIds: ["swift-example"],
            maxNodes: 5
        )

        print("   ✅ Found \(nodeResults.nodes.count) nodes:")
        for node in nodeResults.nodes {
            print("   - \(node.name): \(node.summary.prefix(50))...")
        }
        print()

        // 6. Get recent episodes
        print("6. Getting recent episodes...")
        let episodes = try await client.getEpisodes(
            groupId: "swift-example",
            lastN: 5
        )

        print("   ✅ Found \(episodes.count) episodes")
        print()

        print("✨ Example completed successfully!")
    }
}
