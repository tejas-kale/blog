import Foundation
import OrukeetDictationCore

#if os(macOS)
import AppKit

let config = DictationConfig.fromEnvironment()
fputs(
    "orukeet-dictation: hold \(Hotkey.name(config.hotkeyCode)) to speak; release to paste into the focused app.\n",
    stderr
)

let agent = DictationAgent(config: config)
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
app.delegate = agent
app.run()
#else
fputs("orukeet-dictation is a macOS agent. Build it with: swift build -c release --product orukeet-dictation\n", stderr)
#endif
