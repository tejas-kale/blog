import Foundation

public struct DictationConfig: Equatable, Sendable {
    public var serverURL: URL
    public var hotkeyCode: UInt16
    public var maxSeconds: Double
    public var trailingSpace: Bool
    public var spawnServer: Bool
    public var pythonExecutable: String
    public var serverScript: String?
    public var installationReceipt: String?

    public init(
        serverURL: URL = URL(string: "http://127.0.0.1:8765")!,
        hotkeyCode: UInt16 = Hotkey.rightOption,
        maxSeconds: Double = 60,
        trailingSpace: Bool = true,
        spawnServer: Bool = true,
        pythonExecutable: String = "python3",
        serverScript: String? = nil,
        installationReceipt: String? = nil
    ) {
        self.serverURL = serverURL
        self.hotkeyCode = hotkeyCode
        self.maxSeconds = maxSeconds
        self.trailingSpace = trailingSpace
        self.spawnServer = spawnServer
        self.pythonExecutable = pythonExecutable
        self.serverScript = serverScript
        self.installationReceipt = installationReceipt
    }

    public static func fromEnvironment(_ environment: [String: String] = ProcessInfo.processInfo.environment) -> DictationConfig {
        var config = DictationConfig()
        if let raw = environment["ORUKEET_SERVER_URL"], let url = URL(string: raw) {
            config.serverURL = url
        }
        if let raw = environment["ORUKEET_HOTKEY"] {
            config.hotkeyCode = Hotkey.parse(raw)
        }
        if let raw = environment["ORUKEET_MAX_SECONDS"], let value = Double(raw) {
            config.maxSeconds = min(max(value, 1), 120)
        }
        if let raw = environment["ORUKEET_TRAILING_SPACE"] {
            config.trailingSpace = ["1", "true", "yes"].contains(raw.lowercased())
        }
        if let raw = environment["ORUKEET_SPAWN_SERVER"] {
            config.spawnServer = ["1", "true", "yes"].contains(raw.lowercased())
        }
        if let raw = environment["ORUKEET_PYTHON"] {
            config.pythonExecutable = raw
        }
        config.serverScript = environment["ORUKEET_SERVER_SCRIPT"]
        config.installationReceipt = environment["ORUKEET_INSTALLATION"]
        return config
    }
}

public enum Hotkey {
    /// Right Option — hold to talk. Avoids Fn/Globe flakiness on MacBook Air.
    public static let rightOption: UInt16 = 61
    /// Globe / Fn on recent Macs.
    public static let globe: UInt16 = 63
    public static let rightShift: UInt16 = 60
    public static let f5: UInt16 = 96

    public static func parse(_ raw: String) -> UInt16 {
        switch raw.lowercased() {
        case "rightoption", "right-option", "ralt", "option":
            return rightOption
        case "globe", "fn":
            return globe
        case "rightshift", "right-shift":
            return rightShift
        case "f5":
            return f5
        default:
            return UInt16(raw) ?? rightOption
        }
    }

    public static func name(_ code: UInt16) -> String {
        switch code {
        case rightOption: return "Right Option"
        case globe: return "Globe/Fn"
        case rightShift: return "Right Shift"
        case f5: return "F5"
        default: return "keyCode \(code)"
        }
    }
}
