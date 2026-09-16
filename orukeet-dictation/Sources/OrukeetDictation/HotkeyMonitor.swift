#if os(macOS)
import AppKit
import OrukeetDictationCore

final class HotkeyMonitor {
    private var global: Any?
    private var local: Any?
    private var down = false
    private var onDown: (() -> Void)?
    private var onUp: (() -> Void)?
    private var keyCode: UInt16 = Hotkey.rightOption

    func start(keyCode: UInt16, onDown: @escaping () -> Void, onUp: @escaping () -> Void) {
        stop()
        self.keyCode = keyCode
        self.onDown = onDown
        self.onUp = onUp
        let mask: NSEvent.EventTypeMask = [.keyDown, .keyUp, .flagsChanged]
        global = NSEvent.addGlobalMonitorForEvents(matching: mask) { [weak self] event in
            self?.handle(event)
        }
        local = NSEvent.addLocalMonitorForEvents(matching: mask) { [weak self] event in
            self?.handle(event)
            return event
        }
    }

    func stop() {
        if let global {
            NSEvent.removeMonitor(global)
        }
        if let local {
            NSEvent.removeMonitor(local)
        }
        global = nil
        local = nil
    }

    private func handle(_ event: NSEvent) {
        let matches: Bool
        if event.type == .flagsChanged {
            matches = event.keyCode == keyCode
        } else {
            matches = event.keyCode == keyCode
        }
        guard matches else { return }

        let pressed: Bool
        if event.type == .flagsChanged {
            pressed = event.modifierFlags.contains(flag(for: keyCode))
        } else {
            pressed = event.type == .keyDown
        }

        if pressed, !down {
            down = true
            onDown?()
        } else if !pressed, down {
            down = false
            onUp?()
        }
    }

    private func flag(for keyCode: UInt16) -> NSEvent.ModifierFlags {
        switch keyCode {
        case Hotkey.rightOption:
            return .option
        case Hotkey.rightShift:
            return .shift
        case Hotkey.globe:
            return .function
        default:
            return []
        }
    }
}
#endif
