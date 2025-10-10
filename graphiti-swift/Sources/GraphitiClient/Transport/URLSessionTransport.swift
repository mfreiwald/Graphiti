import Foundation
import HTTPTypes
import HTTPTypesFoundation

#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

/// URLSession-based HTTP transport
public final class URLSessionTransport: HTTPTransport, @unchecked Sendable {
    private let session: URLSession

    public init(session: URLSession = .shared) {
        self.session = session
    }

    public func execute(
        request: HTTPRequest,
        body: Data?
    ) async throws(GraphitiError) -> (Data, HTTPResponse) {
        var urlRequest = URLRequest(httpRequest: request)!

        if let body {
            urlRequest.httpBody = body
        }

        do {
            let (data, response) = try await session.data(for: urlRequest)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw GraphitiError.invalidResponse
            }

            // Convert HTTPURLResponse to HTTPResponse
            var httpTypesResponse = HTTPResponse(
                status: HTTPResponse.Status(
                    code: httpResponse.statusCode,
                    reasonPhrase: HTTPURLResponse.localizedString(forStatusCode: httpResponse.statusCode)
                )
            )

            // Copy headers
            for (key, value) in httpResponse.allHeaderFields {
                if let headerName = key as? String,
                   let headerValue = value as? String,
                   let fieldName = HTTPField.Name(headerName) {
                    httpTypesResponse.headerFields[fieldName] = headerValue
                }
            }

            return (data, httpTypesResponse)
        } catch let error as URLError where error.code == .cancelled {
            throw GraphitiError.cancelled
        } catch is CancellationError {
            throw GraphitiError.cancelled
        } catch {
            throw GraphitiError.networkError(error)
        }
    }
}
