import Foundation
import Combine

class StoryService: ObservableObject {
    private let baseURL = "http://localhost:8000/api/v1"
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Published Properties
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    // MARK: - Story Management
    
    func createStory(genre: String = "fantasy", difficulty: String = "medium") -> AnyPublisher<String, Error> {
        let request = CreateStoryRequest(genre: genre, difficulty: difficulty)
        
        return makeRequest(
            endpoint: "/stories",
            method: "POST",
            body: request
        )
        .tryMap { (response: StoryResponse) -> String in
            guard response.success,
                  let data = response.data,
                  let sessionId = data["session_id"]?.value as? String else {
                throw StoryServiceError.invalidResponse
            }
            return sessionId
        }
        .eraseToAnyPublisher()
    }
    
    func getStoryState(sessionId: String) -> AnyPublisher<StoryState, Error> {
        return makeRequest(
            endpoint: "/stories/\(sessionId)",
            method: "GET"
        )
        .tryMap { (response: StoryResponse) -> StoryState in
            guard response.success,
                  let data = response.data else {
                throw StoryServiceError.invalidResponse
            }
            
            // Convert AnyCodable back to JSON data for decoding
            let jsonData = try JSONSerialization.data(withJSONObject: data.mapValues { $0.value })
            return try JSONDecoder().decode(StoryState.self, from: jsonData)
        }
        .eraseToAnyPublisher()
    }
    
    func makeChoice(sessionId: String, choiceIndex: Int) -> AnyPublisher<StorySegment, Error> {
        let request = MakeChoiceRequest(choiceIndex: choiceIndex)
        
        return makeRequest(
            endpoint: "/stories/\(sessionId)/choices",
            method: "POST",
            body: request
        )
        .tryMap { (response: StorySegmentResponse) -> StorySegment in
            return response.segment
        }
        .eraseToAnyPublisher()
    }
    
    func getStoryHistory(sessionId: String) -> AnyPublisher<[StorySegment], Error> {
        return makeRequest(
            endpoint: "/stories/\(sessionId)/history",
            method: "GET"
        )
        .tryMap { (response: StoryResponse) -> [StorySegment] in
            guard response.success,
                  let data = response.data,
                  let historyData = data["history"]?.value as? [[String: Any]] else {
                throw StoryServiceError.invalidResponse
            }
            
            let jsonData = try JSONSerialization.data(withJSONObject: historyData)
            return try JSONDecoder().decode([StorySegment].self, from: jsonData)
        }
        .eraseToAnyPublisher()
    }
    
    func endStory(sessionId: String) -> AnyPublisher<Void, Error> {
        return makeRequest(
            endpoint: "/stories/\(sessionId)",
            method: "DELETE"
        )
        .tryMap { (response: StoryResponse) -> Void in
            guard response.success else {
                throw StoryServiceError.invalidResponse
            }
        }
        .eraseToAnyPublisher()
    }
    
    // MARK: - Genre and Difficulty
    
    func getGenres() -> AnyPublisher<[Genre], Error> {
        return makeRequest(
            endpoint: "/genres",
            method: "GET"
        )
        .tryMap { (response: StoryResponse) -> [Genre] in
            guard response.success,
                  let data = response.data,
                  let genresData = data["genres"]?.value as? [[String: Any]] else {
                throw StoryServiceError.invalidResponse
            }
            
            let jsonData = try JSONSerialization.data(withJSONObject: genresData)
            return try JSONDecoder().decode([Genre].self, from: jsonData)
        }
        .eraseToAnyPublisher()
    }
    
    func getDifficulties() -> AnyPublisher<[Difficulty], Error> {
        return makeRequest(
            endpoint: "/difficulties",
            method: "GET"
        )
        .tryMap { (response: StoryResponse) -> [Difficulty] in
            guard response.success,
                  let data = response.data,
                  let difficultiesData = data["difficulties"]?.value as? [[String: Any]] else {
                throw StoryServiceError.invalidResponse
            }
            
            let jsonData = try JSONSerialization.data(withJSONObject: difficultiesData)
            return try JSONDecoder().decode([Difficulty].self, from: jsonData)
        }
        .eraseToAnyPublisher()
    }
    
    // MARK: - Private Methods
    
    private func makeRequest<T: Codable, U: Codable>(
        endpoint: String,
        method: String,
        body: T? = nil
    ) -> AnyPublisher<U, Error> {
        guard let url = URL(string: baseURL + endpoint) else {
            return Fail(error: StoryServiceError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let body = body {
            do {
                request.httpBody = try JSONEncoder().encode(body)
            } catch {
                return Fail(error: StoryServiceError.encodingError)
                    .eraseToAnyPublisher()
            }
        }
        
        return URLSession.shared.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: U.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .handleEvents(
                receiveSubscription: { _ in
                    self.isLoading = true
                    self.errorMessage = nil
                },
                receiveCompletion: { completion in
                    self.isLoading = false
                    if case .failure(let error) = completion {
                        self.errorMessage = error.localizedDescription
                    }
                }
            )
            .eraseToAnyPublisher()
    }
}

// MARK: - Errors

enum StoryServiceError: LocalizedError {
    case invalidURL
    case encodingError
    case invalidResponse
    case networkError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .encodingError:
            return "Failed to encode request"
        case .invalidResponse:
            return "Invalid response from server"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
}
