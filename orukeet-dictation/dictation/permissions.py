# [[file:../orukeet-dictation.org::*Permissions][Permissions:1]]
"""Ask macOS for the microphone and for Accessibility."""

from __future__ import annotations

import sys
import threading

ACCESSIBILITY_OPTION = "AXTrustedCheckOptionPrompt"


def prompt_accessibility() -> None:
    try:
        from ApplicationServices import AXIsProcessTrustedWithOptions
    except ImportError:
        print("orukeet-dictation: ApplicationServices is missing.", file=sys.stderr)
        return
    trusted = bool(AXIsProcessTrustedWithOptions({ACCESSIBILITY_OPTION: True}))
    if not trusted:
        print(
            "orukeet-dictation: enable Accessibility for this terminal "
            "in System Settings → Privacy & Security → Accessibility.",
            file=sys.stderr,
        )


def request_microphone() -> tuple[threading.Event, dict]:
    from AVFoundation import AVCaptureDevice, AVMediaTypeAudio

    done = threading.Event()
    result = {"ok": False}

    def handler(allowed) -> None:
        result["ok"] = bool(allowed)
        done.set()

    AVCaptureDevice.requestAccessForMediaType_completionHandler_(AVMediaTypeAudio, handler)
    return done, result
# Permissions:1 ends here
