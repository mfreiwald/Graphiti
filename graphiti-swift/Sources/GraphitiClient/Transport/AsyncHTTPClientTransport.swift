import Foundation
import HTTPTypes
import HTTPTypesFoundation
import AsyncHTTPClient
import NIOCore
import NIOHTTP1

/// AsyncHTTPClient-based HTTP transport (for server-side Swift and Linux)
public final class AsyncHTTPClientTransport: HTTPTransport {
    private let client: HTTPClient

    /// Initialize with an existing HTTPClient
    public init(client: HTTPClient) {
        self.client = client
    }

    /// Initialize with a new HTTPClient
    public init(eventLoopGroupProvider: HTTPClient.EventLoopGroupProvider = .singleton) {
        self.client = HTTPClient(eventLoopGroupProvider: eventLoopGroupProvider)
    }

    deinit {
        try? client.syncShutdown()
    }

    public func execute(
        request: HTTPRequest,
        body: Data?
    ) async throws(GraphitiError) -> (Data, HTTPResponse) {
        // Convert HTTPRequest to AsyncHTTPClient.HTTPClientRequest
        var ahcRequest = HTTPClientRequest(url: request.url!.absoluteString)
        ahcRequest.method = HTTPMethod(rawValue: request.method.rawValue)

        // Copy headers
        for header in request.headerFields {
            ahcRequest.headers.add(name: header.name.rawName, value: header.value)
        }

        // Set body if present
        if let body {
            ahcRequest.body = .bytes(ByteBuffer(data: body))
        }

        do {
            let response = try await client.execute(ahcRequest, timeout: .seconds(60))

            // Collect body
            let responseBody = try await response.body.collect(upTo: 10 * 1024 * 1024) // 10MB limit

            // Convert response
            var httpResponse = HTTPResponse(
                status: HTTPResponse.Status(code: Int(response.status.code), reasonPhrase: response.status.reasonPhrase)
            )

            // Copy response headers
            for header in response.headers {
                httpResponse.headerFields[HTTPField.Name(header.name)!] = header.value
            }

            return (Data(buffer: responseBody), httpResponse)
        } catch let error as HTTPClientError where error == .cancelled {
            throw GraphitiError.cancelled
        } catch is CancellationError {
            throw GraphitiError.cancelled
        } catch {
            throw GraphitiError.networkError(error)
        }
    }

    /// Shutdown the HTTP client gracefully
    public func shutdown() async throws {
        try await client.shutdown()
    }
}
