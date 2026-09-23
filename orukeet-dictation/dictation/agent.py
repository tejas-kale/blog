"""Hold a key, record, transcribe, paste.

This is the whole app. It has no window. Flow:

1. hotkey.py notices Right Option going down, in any app.
2. record.py starts the microphone.
3. On release, client.py sends the WAV to the local Orukeet server.
4. paste.py inserts the transcript at the caret and restores the clipboard.
"""

from __future__ import annotations

import atexit
import signal
import sys
import threading

from dictation.client import prepare_text, transcribe
from dictation.config import Config, hotkey_name
from dictation.server_process import ensure_server


def main() -> None:
    if sys.platform != "darwin":
        print("orukeet-dictation runs on macOS. It pastes into the focused app via AppKit.", file=sys.stderr)
        sys.exit(1)

    config = Config.from_env()
    print(
        f"orukeet-dictation: hold {hotkey_name(config.hotkey_code)} to speak. "
        "Release to paste into the app you were typing in.",
        file=sys.stderr,
    )
    _run(config)


def _run(config: Config) -> None:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    from PyObjCTools import AppHelper

    from dictation.hotkey import HotkeyMonitor
    from dictation.paste import insert_text
    from dictation.permissions import ask_for_access
    from dictation.record import Recorder

    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    recorder = Recorder()
    state: dict = {"busy": False, "hotkey": None, "server": None}

    def shutdown() -> None:
        hotkey = state.get("hotkey")
        if hotkey is not None:
            hotkey.stop()
        recorder.cancel()
        process = state.get("server")
        if process is not None and process.poll() is None:
            process.terminate()

    atexit.register(shutdown)
    signal.signal(signal.SIGINT, lambda *_args: AppHelper.stopEventLoop())

    def begin() -> None:
        if state["busy"]:
            print("orukeet-dictation: still transcribing the last clip", file=sys.stderr)
            return
        try:
            recorder.start(config.max_seconds)
        except Exception as exc:  # noqa: BLE001 — show mic errors in the log
            print(f"orukeet-dictation: could not record: {exc}", file=sys.stderr)
            return
        print("orukeet-dictation: recording", file=sys.stderr)

    def finish() -> None:
        if not recorder.is_recording:
            return
        state["busy"] = True
        try:
            wav = recorder.stop()
        except Exception as exc:  # noqa: BLE001
            state["busy"] = False
            print(f"orukeet-dictation: could not finish the recording: {exc}", file=sys.stderr)
            return
        print(f"orukeet-dictation: transcribing {len(wav)} bytes", file=sys.stderr)

        def work() -> None:
            try:
                result = transcribe(config.server_url, wav)
                text = prepare_text(str(result.get("text", "")), config.trailing_space)
                if text:
                    AppHelper.callLater(0, insert_text, text)
                    print(f"orukeet-dictation: inserted {len(text)} characters", file=sys.stderr)
            except Exception as exc:  # noqa: BLE001
                print(f"orukeet-dictation: transcription failed: {exc}", file=sys.stderr)
            finally:
                state["busy"] = False

        threading.Thread(target=work, daemon=True).start()

    def setup() -> None:
        mic_done = ask_for_access()

        def wait_until_ready() -> None:
            mic_done.wait(timeout=180)
            try:
                state["server"] = ensure_server(config)
            except Exception as exc:  # noqa: BLE001
                print(f"orukeet-dictation: Orukeet server is not ready: {exc}", file=sys.stderr)
                AppHelper.callLater(0, AppHelper.stopEventLoop)
                return

            def arm() -> None:
                state["hotkey"] = HotkeyMonitor(config.hotkey_code, begin, finish)
                print(f"orukeet-dictation: ready. Hold {hotkey_name(config.hotkey_code)} and speak.", file=sys.stderr)

            AppHelper.callLater(0, arm)

        threading.Thread(target=wait_until_ready, daemon=True).start()

    AppHelper.callLater(0.1, setup)
    AppHelper.runEventLoop()
