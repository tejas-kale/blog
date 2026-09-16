#if os(macOS)
import Foundation
import OrukeetDictationCore

enum ServerProcess {
    static func start(config: DictationConfig) throws -> Process {
        let script = config.serverScript ?? defaultScriptPath()
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = [config.pythonExecutable, script]
        var environment = ProcessInfo.processInfo.environment
        if let host = config.serverURL.host {
            environment["ORUKEET_HOST"] = host
        }
        if let port = config.serverURL.port {
            environment["ORUKEET_PORT"] = String(port)
        }
        if let receipt = config.installationReceipt {
            environment["ORUKEET_INSTALLATION"] = receipt
        }
        process.environment = environment
        process.standardOutput = FileHandle.standardError
        process.standardError = FileHandle.standardError
        try process.run()
        return process
    }

    static func defaultScriptPath() -> String {
        let executable = URL(fileURLWithPath: Bundle.main.executableURL?.path ?? CommandLine.arguments[0])
        let candidates = [
            executable.deletingLastPathComponent().appendingPathComponent("orukeet_server.py"),
            executable.deletingLastPathComponent().deletingLastPathComponent()
                .appendingPathComponent("Resources/orukeet_server.py"),
            URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
                .appendingPathComponent("server/orukeet_server.py"),
        ]
        return candidates.first(where: { FileManager.default.fileExists(atPath: $0.path) })?.path
            ?? "server/orukeet_server.py"
    }
}
#endif
