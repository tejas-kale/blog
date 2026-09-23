"""Ask macOS for the two permissions dictation needs.

Microphone: so we can hear you.
Accessibility: so we can see the hotkey, and press Command-V, while another
app is focused. macOS shows the dialogs; this only triggers them.
"""

from __future__ import annotations

import sys
import threading


def ask_for_access() -> threading.Event:
    """Prompt for both permissions. The returned event is set once the mic answer arrives."""
    _prompt_accessibility()
    return _request_microphone()


def _prompt_accessibility() -> None:
    try:
        from ApplicationServices import AXIsProcessTrustedWithOptions
    except ImportError:
        print("orukeet-dictation: ApplicationServices is missing; skipping the Accessibility prompt.", file=sys.stderr)
        return
    trusted = bool(AXIsProcessTrustedWithOptions({"AXTrustedCheckOptionPrompt": True}))
    if not trusted:
        print(
            "orukeet-dictation: allow Accessibility for this terminal in "
            "System Settings → Privacy & Security → Accessibility.",
            file=sys.stderr,
        )


def _request_microphone() -> threading.Event:
    from AVFoundation import AVCaptureDevice, AVMediaTypeAudio

    done = threading.Event()
    granted = {"ok": False}

    def handler(allowed) -> None:
        granted["ok"] = bool(allowed)
        done.set()

    AVCaptureDevice.requestAccessForMediaType_completionHandler_(AVMediaTypeAudio, handler)

    def report() -> None:
        if done.wait(timeout=180) and not granted["ok"]:
            print(
                "orukeet-dictation: microphone permission denied. "
                "Enable it for this terminal in System Settings → Privacy & Security → Microphone.",
                file=sys.stderr,
            )

    threading.Thread(target=report, daemon=True).start()
    return done
