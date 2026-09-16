import Foundation

public enum WavEncoder {
    public static let sampleRate = 16_000

    public static func pcm16MonoWav(samples: [Int16], sampleRate: Int = sampleRate) -> Data {
        let dataSize = UInt32(samples.count * MemoryLayout<Int16>.size)
        var data = Data()
        data.reserveCapacity(44 + Int(dataSize))
        data.append(ascii: "RIFF")
        data.append(le: UInt32(36) + dataSize)
        data.append(ascii: "WAVE")
        data.append(ascii: "fmt ")
        data.append(le: UInt32(16))
        data.append(le: UInt16(1))
        data.append(le: UInt16(1))
        data.append(le: UInt32(sampleRate))
        data.append(le: UInt32(sampleRate * 2))
        data.append(le: UInt16(2))
        data.append(le: UInt16(16))
        data.append(ascii: "data")
        data.append(le: dataSize)
        if !samples.isEmpty {
            samples.withUnsafeBufferPointer { buffer in
                guard let base = buffer.baseAddress else { return }
                base.withMemoryRebound(to: UInt8.self, capacity: Int(dataSize)) { bytes in
                    data.append(bytes, count: Int(dataSize))
                }
            }
        }
        return data
    }
}

private extension Data {
    mutating func append(ascii string: String) {
        append(contentsOf: string.utf8)
    }

    mutating func append(le value: UInt16) {
        var little = value.littleEndian
        Swift.withUnsafeBytes(of: &little) { append(contentsOf: $0) }
    }

    mutating func append(le value: UInt32) {
        var little = value.littleEndian
        Swift.withUnsafeBytes(of: &little) { append(contentsOf: $0) }
    }
}
