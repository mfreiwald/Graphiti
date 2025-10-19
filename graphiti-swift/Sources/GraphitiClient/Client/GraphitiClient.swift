import Foundation
import HTTPTypes

#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

/// Main client for interacting with Graphiti REST API
public actor GraphitiClient {
    private let transport: HTTPTransport
    private let requestBuilder: HTTPRequestBuilder
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    /// Initialize with a custom transport
    public init(
        baseURL: URL,
        transport: HTTPTransport,
        additionalHeaders: HTTPFields = [:]
    ) {
        self.transport = transport

        var headers: HTTPFields = [
            .contentType: "application/json",
            .accept: "application/json"
        ]

        for header in additionalHeaders {
            headers[header.name] = header.value
        }

        self.requestBuilder = HTTPRequestBuilder(baseURL: baseURL, defaultHeaders: headers)

        self.decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        self.encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
    }

    /// Convenience initializer with URLSession transport
    public init(
        baseURL: URL,
        session: URLSession = .shared,
        additionalHeaders: HTTPFields = [:]
    ) {
        self.init(
            baseURL: baseURL,
            transport: URLSessionTransport(session: session),
            additionalHeaders: additionalHeaders
        )
    }

    // MARK: - Memory Operations

    /// Add an episode to memory asynchronously (queued)
    /// - Returns: Success response with queue position
    /// - Note: This endpoint queues the episode for background processing and returns immediately
    public func addMemory(_ request: AddMemoryRequest) async throws(GraphitiError) -> SuccessResponse {
        let httpRequest = try requestBuilder.buildRequest(
            method: .post,
            path: "/api/v1/memory"
        )

        let body: Data
        do {
            body = try encoder.encode(request)
        } catch {
            throw .encodingError(error)
        }

        return try await executeRequest(httpRequest, body: body)
    }

    /// Add an episode to memory synchronously
    /// - Returns: Response with episode UUID
    /// - Note: This endpoint processes the episode immediately and waits for completion
    public func addMemorySync(_ request: AddMemoryRequest) async throws(GraphitiError) -> AddMemoryResponse {
        let httpRequest = try requestBuilder.buildRequest(
            method: .post,
            path: "/api/v1/memory/sync"
        )

        let body: Data
        do {
            body = try encoder.encode(request)
        } catch {
            throw .encodingError(error)
        }

        return try await executeRequest(httpRequest, body: body)
    }

    /// Get recent episodes for a group
    public func getEpisodes(groupId: String, lastN: Int = 10) async throws(GraphitiError) -> [Episode] {
        let httpRequest = try requestBuilder.buildRequest(
            method: .get,
            path: "/api/v1/episodes/\(groupId)",
            queryItems: [("last_n", String(lastN))]
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    /// Delete an episode by UUID
    public func deleteEpisode(uuid: String) async throws(GraphitiError) -> SuccessResponse {
        let httpRequest = try requestBuilder.buildRequest(
            method: .delete,
            path: "/api/v1/episode/\(uuid)"
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    /// Get an entity edge by UUID
    public func getEntityEdge(uuid: String) async throws(GraphitiError) -> FactResult {
        let httpRequest = try requestBuilder.buildRequest(
            method: .get,
            path: "/api/v1/entity-edge/\(uuid)"
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    /// Delete an entity edge by UUID
    public func deleteEntityEdge(uuid: String) async throws(GraphitiError) -> SuccessResponse {
        let httpRequest = try requestBuilder.buildRequest(
            method: .delete,
            path: "/api/v1/entity-edge/\(uuid)"
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    // MARK: - Search Operations

    /// Search for nodes
    public func searchNodes(
        query: String,
        groupIds: [String]? = nil,
        maxNodes: Int = 10,
        centerNodeUuid: String? = nil,
        entity: String? = nil
    ) async throws(GraphitiError) -> NodeSearchResponse {
        var queryItems: [(String, String)] = [
            ("query", query),
            ("max_nodes", String(maxNodes))
        ]

        if let groupIds {
            for groupId in groupIds {
                queryItems.append(("group_ids", groupId))
            }
        }

        if let centerNodeUuid {
            queryItems.append(("center_node_uuid", centerNodeUuid))
        }

        if let entity {
            queryItems.append(("entity", entity))
        }

        let httpRequest = try requestBuilder.buildRequest(
            method: .get,
            path: "/api/v1/search/nodes",
            queryItems: queryItems
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    /// Search for facts
    public func searchFacts(
        query: String,
        groupIds: [String]? = nil,
        maxFacts: Int = 10,
        centerNodeUuid: String? = nil
    ) async throws(GraphitiError) -> FactSearchResponse {
        var queryItems: [(String, String)] = [
            ("query", query),
            ("max_facts", String(maxFacts))
        ]

        if let groupIds {
            for groupId in groupIds {
                queryItems.append(("group_ids", groupId))
            }
        }

        if let centerNodeUuid {
            queryItems.append(("center_node_uuid", centerNodeUuid))
        }

        let httpRequest = try requestBuilder.buildRequest(
            method: .get,
            path: "/api/v1/search/facts",
            queryItems: queryItems
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    // MARK: - Admin Operations

    /// Get server status
    public func getStatus() async throws(GraphitiError) -> StatusResponse {
        let httpRequest = try requestBuilder.buildRequest(
            method: .get,
            path: "/api/v1/status"
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    /// Clear the graph
    public func clearGraph() async throws(GraphitiError) -> SuccessResponse {
        let httpRequest = try requestBuilder.buildRequest(
            method: .post,
            path: "/api/v1/clear"
        )

        return try await executeRequest(httpRequest, body: nil)
    }

    /// Check if server is healthy
    public func healthCheck() async throws(GraphitiError) -> Bool {
        let httpRequest = try requestBuilder.buildRequest(
            method: .get,
            path: "/healthcheck"
        )

        let (_, response) = try await transport.execute(request: httpRequest, body: nil)

        return response.status.kind == .successful
    }

    // MARK: - Private Helpers

    private func executeRequest<T: Decodable>(
        _ request: HTTPRequest,
        body: Data?
    ) async throws(GraphitiError) -> T {
        let (data, response) = try await transport.execute(request: request, body: body)

        // Check for HTTP errors
        guard response.status.kind == .successful else {
            // Try to decode error response
            if let errorResponse = try? decoder.decode(ErrorResponse.self, from: data) {
                throw GraphitiError.serverError(errorResponse)
            }

            // Fallback to generic HTTP error
            let message = String(data: data, encoding: .utf8)
            throw GraphitiError.httpError(response.status, message)
        }

        // Decode response
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw GraphitiError.decodingError(error)
        }
    }
}
