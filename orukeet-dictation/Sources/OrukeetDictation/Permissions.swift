#if os(macOS)
import AppKit
import AVFoundation
import ApplicationServices

enum Permissions {
    static func promptAccessibilityIfNeeded() {
        let prompt = kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String
        let options = [prompt: true] as CFDictionary
        _ = AXIsProcessTrustedWithOptions(options)
    }

    @MainActor
    static func ensureMicrophone() async {
        if #available(macOS 14.0, *) {
            let granted = await AVAudioApplication.requestRecordPermission()
            if !granted {
                fputs("orukeet-dictation: microphone permission denied.\n", stderr)
            }
            return
        }
        await withCheckedContinuation { continuation in
            AVCaptureDevice.requestAccess(for: .audio) { granted in
                if !granted {
                    fputs("orukeet-dictation: microphone permission denied.\n", stderr)
                }
                continuation.resume()
            }
        }
    }
}
#endif
