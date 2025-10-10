import Foundation
import HTTPTypes
import HTTPTypesFoundation

/// Protocol for HTTP transport
public protocol HTTPTransport: Sendable {
    /// Execute an HTTP request
    func execute(
        request: HTTPRequest,
        body: Data?
    ) async throws(GraphitiError) -> (Data, HTTPResponse)
}

/// HTTP request builder
public struct HTTPRequestBuilder: Sendable {
    let baseURL: URL
    let defaultHeaders: HTTPFields

    public init(baseURL: URL, defaultHeaders: HTTPFields = [:]) {
        self.baseURL = baseURL
        self.defaultHeaders = defaultHeaders
    }

    public func buildRequest(
        method: HTTPRequest.Method,
        path: String,
        queryItems: [(String, String)] = [],
        headers: HTTPFields = [:]
    ) throws(GraphitiError) -> HTTPRequest {
        var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: true)!
        components.path = path

        if !queryItems.isEmpty {
            components.queryItems = queryItems.map { URLQueryItem(name: $0.0, value: $0.1) }
        }

        guard let url = components.url else {
            throw GraphitiError.invalidURL(path)
        }

        var request = HTTPRequest(method: method, url: url)
        request.headerFields = defaultHeaders

        for header in headers {
            request.headerFields[header.name] = header.value
        }

        return request
    }
}
