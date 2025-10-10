import Foundation
import HTTPTypes

/// Errors that can occur when using the Graphiti client
public enum GraphitiError: Error, Sendable {
    /// Network error
    case networkError(Error)

    /// Invalid URL
    case invalidURL(String)

    /// HTTP error with status code
    case httpError(HTTPResponse.Status, String?)

    /// Decoding error
    case decodingError(Error)

    /// Encoding error
    case encodingError(Error)

    /// Server returned an error response
    case serverError(ErrorResponse)

    /// Invalid response
    case invalidResponse

    /// Request cancelled
    case cancelled
}

extension GraphitiError: LocalizedError {
    public var errorDescription: String? {
        switch self {
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .invalidURL(let url):
            return "Invalid URL: \(url)"
        case .httpError(let status, let message):
            if let message {
                return "HTTP \(status.code): \(message)"
            }
            return "HTTP \(status.code): \(status.reasonPhrase)"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .encodingError(let error):
            return "Failed to encode request: \(error.localizedDescription)"
        case .serverError(let response):
            return "Server error: \(response.error)"
        case .invalidResponse:
            return "Invalid response from server"
        case .cancelled:
            return "Request was cancelled"
        }
    }
}
