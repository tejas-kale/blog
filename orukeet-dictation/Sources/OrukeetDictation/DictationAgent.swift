#if os(macOS)
import AppKit
import AVFoundation
import Foundation
import OrukeetDictationCore

final class DictationAgent: NSObject, NSApplicationDelegate {
    private let config: DictationConfig
    private let client: OrukeetClient
    private let recorder = AudioRecorder()
    private let inserter = TextInserter()
    private let hotkey = HotkeyMonitor()
    private var server: Process?
    private var busy = false

    init(config: DictationConfig) {
        self.config = config
        self.client = OrukeetClient(baseURL: config.serverURL)
        super.init()
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        Task { @MainActor in
            await Permissions.ensureMicrophone()
            Permissions.promptAccessibilityIfNeeded()
            do {
                try await ensureServer()
            } catch {
                fputs("orukeet-dictation: Orukeet server is not ready: \(error)\n", stderr)
                NSApp.terminate(nil)
                return
            }
            hotkey.start(keyCode: config.hotkeyCode, onDown: { [weak self] in
                self?.beginRecording()
            }, onUp: { [weak self] in
                self?.finishRecording()
            })
            fputs("orukeet-dictation: ready. Speak after holding \(Hotkey.name(config.hotkeyCode)).\n", stderr)
        }
    }

    func applicationWillTerminate(_ notification: Notification) {
        hotkey.stop()
        recorder.cancel()
        server?.terminate()
    }

    private func beginRecording() {
        guard !busy else { return }
        do {
            try recorder.start(maxSeconds: config.maxSeconds)
            fputs("orukeet-dictation: recording\n", stderr)
        } catch {
            fputs("orukeet-dictation: could not record: \(error)\n", stderr)
        }
    }

    private func finishRecording() {
        guard recorder.isRecording else { return }
        busy = true
        let samples = recorder.stop()
        fputs("orukeet-dictation: transcribing \(samples.count) samples\n", stderr)
        Task {
            defer { busy = false }
            let wav = WavEncoder.pcm16MonoWav(samples: samples)
            do {
                let transcript = try await client.transcribe(wav: wav)
                let text = transcript.insertableText(trailingSpace: config.trailingSpace)
                guard !text.isEmpty else { return }
                await MainActor.run {
                    inserter.insert(text)
                }
                fputs("orukeet-dictation: inserted \(text.count) characters\n", stderr)
            } catch {
                fputs("orukeet-dictation: transcription failed: \(error)\n", stderr)
            }
        }
    }

    private func ensureServer() async throws {
        if await (try? client.health()) == true {
            return
        }
        guard config.spawnServer else {
            throw OrukeetClientError.unhealthy
        }
        server = try ServerProcess.start(config: config)
        fputs("orukeet-dictation: loading Orukeet (first start can take a minute on 8 GB)...\n", stderr)
        for _ in 0 ..< 180 {
            try await Task.sleep(nanoseconds: 1_000_000_000)
            if await (try? client.health()) == true {
                return
            }
        }
        throw OrukeetClientError.unhealthy
    }
}
#endif
