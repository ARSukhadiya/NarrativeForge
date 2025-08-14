import Foundation

// MARK: - Story Models

struct StoryChoice: Codable, Identifiable {
    let id = UUID()
    let text: String
    let action: String
    let description: String?
    
    enum CodingKeys: String, CodingKey {
        case text, action, description
    }
}

struct StorySegment: Codable, Identifiable {
    let id: String
    let text: String
    let choices: [StoryChoice]
    let backgroundContext: String?
    let mood: String?
    let location: String?
    
    enum CodingKeys: String, CodingKey {
        case id, text, choices, backgroundContext, mood, location
    }
}

struct StoryState: Codable {
    let storyId: String
    let currentSegment: StorySegment
    let storyHistory: [StorySegment]
    let characterInfo: [String: String]
    let worldInfo: [String: String]
    let genre: String
    let difficulty: String
    let createdAt: String
    let lastUpdated: String?
    
    enum CodingKeys: String, CodingKey {
        case storyId = "story_id"
        case currentSegment = "current_segment"
        case storyHistory = "story_history"
        case characterInfo = "character_info"
        case worldInfo = "world_info"
        case genre, difficulty
        case createdAt = "created_at"
        case lastUpdated = "last_updated"
    }
}

// MARK: - API Request Models

struct CreateStoryRequest: Codable {
    let genre: String
    let difficulty: String
}

struct MakeChoiceRequest: Codable {
    let choiceIndex: Int
    
    enum CodingKeys: String, CodingKey {
        case choiceIndex = "choice_index"
    }
}

// MARK: - API Response Models

struct StoryResponse: Codable {
    let success: Bool
    let message: String
    let data: [String: AnyCodable]?
}

struct StorySegmentResponse: Codable {
    let segment: StorySegment
    let sessionId: String
    
    enum CodingKeys: String, CodingKey {
        case segment
        case sessionId = "session_id"
    }
}

// MARK: - Genre and Difficulty Models

struct Genre: Codable, Identifiable {
    let id: String
    let name: String
    let description: String
}

struct Difficulty: Codable, Identifiable {
    let id: String
    let name: String
    let description: String
}

// MARK: - Helper for AnyCodable

struct AnyCodable: Codable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if container.decodeNil() {
            self.value = NSNull()
        } else if let bool = try? container.decode(Bool.self) {
            self.value = bool
        } else if let int = try? container.decode(Int.self) {
            self.value = int
        } else if let double = try? container.decode(Double.self) {
            self.value = double
        } else if let string = try? container.decode(String.self) {
            self.value = string
        } else if let array = try? container.decode([AnyCodable].self) {
            self.value = array.map { $0.value }
        } else if let dictionary = try? container.decode([String: AnyCodable].self) {
            self.value = dictionary.mapValues { $0.value }
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "AnyCodable value cannot be decoded")
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch self.value {
        case is NSNull:
            try container.encodeNil()
        case let bool as Bool:
            try container.encode(bool)
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let string as String:
            try container.encode(string)
        case let array as [Any]:
            try container.encode(array.map { AnyCodable($0) })
        case let dictionary as [String: Any]:
            try container.encode(dictionary.mapValues { AnyCodable($0) })
        default:
            let context = EncodingError.Context(codingPath: container.codingPath, debugDescription: "AnyCodable value cannot be encoded")
            throw EncodingError.invalidValue(self.value, context)
        }
    }
}
