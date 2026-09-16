import XCTest
@testable import OrukeetDictationCore

final class ConfigTests: XCTestCase {
    func testParsesNamedHotkeysAndClampsDuration() {
        let config = DictationConfig.fromEnvironment([
            "ORUKEET_HOTKEY": "globe",
            "ORUKEET_MAX_SECONDS": "999",
            "ORUKEET_TRAILING_SPACE": "false",
            "ORUKEET_SERVER_URL": "http://127.0.0.1:9000",
        ])
        XCTAssertEqual(config.hotkeyCode, Hotkey.globe)
        XCTAssertEqual(config.maxSeconds, 120)
        XCTAssertFalse(config.trailingSpace)
        XCTAssertEqual(config.serverURL.port, 9000)
    }

    func testDefaultHotkeyIsRightOption() {
        XCTAssertEqual(DictationConfig().hotkeyCode, 61)
        XCTAssertEqual(Hotkey.parse("right-option"), 61)
    }
}

final class TranscriptTests: XCTestCase {
    func testAddsTrailingSpaceAndDecodesMissingSegments() throws {
        let json = Data(#"{"text":"hello"}"#.utf8)
        let transcript = try JSONDecoder().decode(Transcript.self, from: json)
        XCTAssertEqual(transcript.insertableText(trailingSpace: true), "hello ")
        XCTAssertEqual(transcript.segments, [])
    }
}

final class WavEncoderTests: XCTestCase {
    func testWritesPcm16MonoHeader() {
        let wav = WavEncoder.pcm16MonoWav(samples: [1, -1], sampleRate: 16_000)
        XCTAssertEqual(Array(wav.prefix(4)), Array("RIFF".utf8))
        XCTAssertEqual(Array(wav[8 ..< 12]), Array("WAVE".utf8))
        XCTAssertEqual(wav.count, 48)
        XCTAssertEqual(wav[22], 1)
        XCTAssertEqual(wav[34], 16)
    }

    func testEmptyRecordingStillHasHeader() {
        let wav = WavEncoder.pcm16MonoWav(samples: [])
        XCTAssertEqual(wav.count, 44)
    }
}
