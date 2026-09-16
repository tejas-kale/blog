import Foundation

public enum OrukeetClientError: Error, Equatable {
    case unhealthy
    case httpStatus(Int)
    case emptyTranscript
    case decodingFailed
}

public struct OrukeetClient: Sendable {
    public var baseURL: URL
    public var session: URLSession
    public var timeout: TimeInterval

    public init(baseURL: URL, session: URLSession = .shared, timeout: TimeInterval = 120) {
        self.baseURL = baseURL
        self.session = session
        self.timeout = timeout
    }

    public func health() async throws -> Bool {
        var request = URLRequest(url: baseURL.appendingPathComponent("health"))
        request.timeoutInterval = 3
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse, (200 ..< 300).contains(http.statusCode) else {
            return false
        }
        if let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let ok = object["ok"] as? Bool {
            return ok
        }
        return true
    }

    public func transcribe(wav: Data) async throws -> Transcript {
        var request = URLRequest(url: baseURL.appendingPathComponent("transcribe"))
        request.httpMethod = "POST"
        request.setValue("audio/wav", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = timeout
        request.httpBody = wav
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw OrukeetClientError.decodingFailed
        }
        guard (200 ..< 300).contains(http.statusCode) else {
            throw OrukeetClientError.httpStatus(http.statusCode)
        }
        let decoder = JSONDecoder()
        guard let transcript = try? decoder.decode(Transcript.self, from: data) else {
            throw OrukeetClientError.decodingFailed
        }
        if transcript.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            throw OrukeetClientError.emptyTranscript
        }
        return transcript
    }
}
