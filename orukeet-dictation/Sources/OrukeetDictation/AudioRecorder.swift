#if os(macOS)
import AVFoundation
import Foundation

enum AudioRecorderError: Error {
    case engineStartFailed
}

final class AudioRecorder {
    private let engine = AVAudioEngine()
    private var converter: AVAudioConverter?
    private var samples: [Int16] = []
    private var startedAt: Date?
    private(set) var isRecording = false
    private var maxSeconds: Double = 60

    func start(maxSeconds: Double) throws {
        cancel()
        self.maxSeconds = maxSeconds
        let input = engine.inputNode
        let inputFormat = input.outputFormat(forBus: 0)
        guard let target = AVAudioFormat(
            commonFormat: .pcmFormatInt16,
            sampleRate: 16_000,
            channels: 1,
            interleaved: true
        ) else {
            throw AudioRecorderError.engineStartFailed
        }
        converter = AVAudioConverter(from: inputFormat, to: target)
        samples = []
        startedAt = Date()
        input.installTap(onBus: 0, bufferSize: 2048, format: inputFormat) { [weak self] buffer, _ in
            self?.append(buffer, target: target)
        }
        engine.prepare()
        try engine.start()
        isRecording = true
    }

    func stop() -> [Int16] {
        let captured = samples
        cancel()
        return captured
    }

    func cancel() {
        if engine.isRunning {
            engine.stop()
        }
        engine.inputNode.removeTap(onBus: 0)
        converter = nil
        samples = []
        startedAt = nil
        isRecording = false
    }

    private func append(_ buffer: AVAudioPCMBuffer, target: AVAudioFormat) {
        if let startedAt, Date().timeIntervalSince(startedAt) > maxSeconds {
            return
        }
        guard let converter else { return }
        let ratio = target.sampleRate / buffer.format.sampleRate
        let capacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio) + 32
        guard let converted = AVAudioPCMBuffer(pcmFormat: target, frameCapacity: capacity) else { return }
        var error: NSError?
        var consumed = false
        converter.convert(to: converted, error: &error) { _, status in
            if consumed {
                status.pointee = .noDataNow
                return nil
            }
            consumed = true
            status.pointee = .haveData
            return buffer
        }
        guard error == nil, let channel = converted.int16ChannelData else { return }
        let count = Int(converted.frameLength)
        samples.append(contentsOf: UnsafeBufferPointer(start: channel[0], count: count))
    }
}
#endif
