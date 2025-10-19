import Foundation

// MARK: - Request Models

/// Request to add an episode to memory
public struct AddMemoryRequest: Sendable, Codable {
    /// Name of the episode
    public let name: String

    /// Content of the episode
    public let episodeBody: String

    /// Group ID for namespace isolation
    public let groupId: String?

    /// Source type
    public let source: SourceType

    /// Description of the source
    public let sourceDescription: String?

    /// Optional UUID for the episode
    public let uuid: String?

    enum CodingKeys: String, CodingKey {
        case name
        case episodeBody = "episode_body"
        case groupId = "group_id"
        case source
        case sourceDescription = "source_description"
        case uuid
    }

    public init(
        name: String,
        episodeBody: String,
        groupId: String? = nil,
        source: SourceType = .text,
        sourceDescription: String? = nil,
        uuid: String? = nil
    ) {
        self.name = name
        self.episodeBody = episodeBody
        self.groupId = groupId
        self.source = source
        self.sourceDescription = sourceDescription
        self.uuid = uuid
    }
}

/// Source type for episodes
public enum SourceType: String, Sendable, Codable {
    case text
    case json
    case message
}

// MARK: - Response Models

/// Generic success response
public struct SuccessResponse: Sendable, Codable {
    public let message: String
    public let success: Bool
}

/// Response for add_memory endpoint with episode UUID
public struct AddMemoryResponse: Sendable, Codable {
    public let message: String
    public let episodeUuid: String
    public let success: Bool

    enum CodingKeys: String, CodingKey {
        case message
        case episodeUuid = "episode_uuid"
        case success
    }
}

/// Generic error response
public struct ErrorResponse: Sendable, Codable, Error {
    public let error: String
    public let success: Bool
}

/// Node search result
public struct NodeResult: Sendable, Codable, Identifiable {
    public let uuid: String
    public let name: String
    public let summary: String
    public let labels: [String]
    public let groupId: String
    public let createdAt: String
    public let attributes: [String: AnyCodable]

    public var id: String { uuid }

    enum CodingKeys: String, CodingKey {
        case uuid, name, summary, labels
        case groupId = "group_id"
        case createdAt = "created_at"
        case attributes
    }
}

/// Node search response
public struct NodeSearchResponse: Sendable, Codable {
    public let message: String
    public let nodes: [NodeResult]
    public let success: Bool
}

/// Fact (entity edge) result
public struct FactResult: Sendable, Codable, Identifiable {
    public let uuid: String
    public let name: String
    public let fact: String
    public let validAt: Date?
    public let invalidAt: Date?
    public let createdAt: Date
    public let expiredAt: Date?
    public let sourceNodeUuid: String?
    public let targetNodeUuid: String?

    public var id: String { uuid }

    enum CodingKeys: String, CodingKey {
        case uuid, name, fact
        case validAt = "valid_at"
        case invalidAt = "invalid_at"
        case createdAt = "created_at"
        case expiredAt = "expired_at"
        case sourceNodeUuid = "source_node_uuid"
        case targetNodeUuid = "target_node_uuid"
    }
}

/// Fact search response
public struct FactSearchResponse: Sendable, Codable {
    public let message: String
    public let facts: [FactResult]
    public let success: Bool
}

/// Server status response
public struct StatusResponse: Sendable, Codable {
    public let status: ServerStatus
    public let message: String
    public let config: ServerConfig?

    public enum ServerStatus: String, Sendable, Codable {
        case ok
        case error
    }

    public struct ServerConfig: Sendable, Codable {
        public let model: String
        public let smallModel: String
        public let temperature: Double?
        public let defaultGroupId: String
        public let customEntitiesEnabled: Bool
        public let semaphoreLimit: Int

        enum CodingKeys: String, CodingKey {
            case model
            case smallModel = "small_model"
            case temperature
            case defaultGroupId = "default_group_id"
            case customEntitiesEnabled = "custom_entities_enabled"
            case semaphoreLimit = "semaphore_limit"
        }
    }
}

/// Episode data
public typealias Episode = [String: AnyCodable]

// MARK: - Helper: AnyCodable

/// Type-erased Codable value
public struct AnyCodable: @unchecked Sendable, Codable {
    public let value: Any

    public init(_ value: Any) {
        self.value = value
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if container.decodeNil() {
            self.value = Optional<Any>.none as Any
        } else if let bool = try? container.decode(Bool.self) {
            self.value = bool
        } else if let int = try? container.decode(Int.self) {
            self.value = int
        } else if let double = try? container.decode(Double.self) {
            self.value = double
        } else if let string = try? container.decode(String.self) {
            self.value = string
        } else if let array = try? container.decode([AnyCodable].self) {
            self.value = array.map(\.value)
        } else if let dictionary = try? container.decode([String: AnyCodable].self) {
            self.value = dictionary.mapValues(\.value)
        } else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "AnyCodable value cannot be decoded"
            )
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        switch value {
        case let value as Bool:
            try container.encode(value)
        case let value as Int:
            try container.encode(value)
        case let value as Double:
            try container.encode(value)
        case let value as String:
            try container.encode(value)
        case let value as [Any]:
            try container.encode(value.map { AnyCodable($0) })
        case let value as [String: Any]:
            try container.encode(value.mapValues { AnyCodable($0) })
        case Optional<Any>.none:
            try container.encodeNil()
        default:
            let context = EncodingError.Context(
                codingPath: container.codingPath,
                debugDescription: "AnyCodable value cannot be encoded"
            )
            throw EncodingError.invalidValue(value, context)
        }
    }
}
