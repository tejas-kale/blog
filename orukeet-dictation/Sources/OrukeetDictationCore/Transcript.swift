import Foundation

public struct Transcript: Codable, Equatable, Sendable {
    public var text: String
    public var segments: [Segment]
    public var language: String?

    public struct Segment: Codable, Equatable, Sendable {
        public var text: String
        public var start: Double?
        public var end: Double?
    }

    public init(text: String, segments: [Segment] = [], language: String? = nil) {
        self.text = text
        self.segments = segments
        self.language = language
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        text = try container.decode(String.self, forKey: .text)
        segments = try container.decodeIfPresent([Segment].self, forKey: .segments) ?? []
        language = try container.decodeIfPresent(String.self, forKey: .language)
    }

    public func insertableText(trailingSpace: Bool) -> String {
        var trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return "" }
        if trailingSpace, !trimmed.hasSuffix(" ") {
            trimmed += " "
        }
        return trimmed
    }
}
