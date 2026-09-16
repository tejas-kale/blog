#if os(macOS)
import AppKit
import Carbon.HIToolbox

final class TextInserter {
    static let pasteKeyCode = CGKeyCode(kVK_ANSI_V)
    private static let transientType = NSPasteboard.PasteboardType("org.nspasteboard.TransientType")
    private static let concealedType = NSPasteboard.PasteboardType("org.nspasteboard.ConcealedType")

    func insert(_ text: String) {
        let pasteboard = NSPasteboard.general
        let saved = snapshot(pasteboard)
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)
        pasteboard.setData(Data(), forType: Self.transientType)
        pasteboard.setData(Data(), forType: Self.concealedType)
        let stamp = pasteboard.changeCount
        sendCommandV()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            self.restore(saved, on: pasteboard, ifChangeCountIs: stamp)
        }
    }

    private func snapshot(_ pasteboard: NSPasteboard) -> [[NSPasteboard.PasteboardType: Data]] {
        (pasteboard.pasteboardItems ?? []).map { item in
            var payload: [NSPasteboard.PasteboardType: Data] = [:]
            for type in item.types {
                if let data = item.data(forType: type) {
                    payload[type] = data
                }
            }
            return payload
        }
    }

    private func restore(
        _ saved: [[NSPasteboard.PasteboardType: Data]],
        on pasteboard: NSPasteboard,
        ifChangeCountIs stamp: Int
    ) {
        guard pasteboard.changeCount == stamp else { return }
        pasteboard.clearContents()
        let items = saved.map { payload -> NSPasteboardItem in
            let item = NSPasteboardItem()
            for (type, data) in payload {
                item.setData(data, forType: type)
            }
            return item
        }
        pasteboard.writeObjects(items)
    }

    private func sendCommandV() {
        let source = CGEventSource(stateID: .combinedSessionState)
        let down = CGEvent(keyboardEventSource: source, virtualKey: Self.pasteKeyCode, keyDown: true)
        let up = CGEvent(keyboardEventSource: source, virtualKey: Self.pasteKeyCode, keyDown: false)
        down?.flags = .maskCommand
        up?.flags = .maskCommand
        down?.post(tap: .cghidEventTap)
        up?.post(tap: .cghidEventTap)
    }
}
#endif
