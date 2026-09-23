# [[file:../orukeet-dictation.org::*The agent][The agent:1]]
"""Hold a key, record, transcribe, paste."""

from __future__ import annotations

import atexit
import signal
import sys
import threading

from dictation.client import prepare_text, transcribe
from dictation.config import Config, hotkey_name
from dictation.server_process import ensure_server


def log(message: str) -> None:
    print(f"orukeet-dictation: {message}", file=sys.stderr)


def main() -> None:
    if sys.platform != "darwin":
        log("this agent runs on macOS, where it can paste into the focused app.")
        sys.exit(1)
    config = Config.from_env()
    log(f"hold {hotkey_name(config.hotkey_code)} to speak. Release to paste.")
    DictationApp(config).run()


class DictationApp:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.recorder = None
        self.busy = False
        self.hotkey = None
        self.server = None
        self.cleaner = None

    def run(self) -> None:
        from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
        from PyObjCTools import AppHelper

        from dictation.record import Recorder

        self.recorder = Recorder()
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        atexit.register(self.shutdown)
        signal.signal(signal.SIGINT, lambda *_args: AppHelper.stopEventLoop())
        AppHelper.callLater(0.1, self.setup)
        AppHelper.runEventLoop()

    def shutdown(self) -> None:
        if self.hotkey is not None:
            self.hotkey.stop()
        if self.recorder is not None:
            self.recorder.cancel()
        if self.server is not None and self.server.poll() is None:
            self.server.terminate()

    def begin(self) -> None:
        if self.busy:
            log("still transcribing the last clip")
            return
        try:
            self.recorder.start(self.config.max_seconds)
        except Exception as exc:  # noqa: BLE001
            log(f"could not record: {exc}")
            return
        log("recording")

    def finish(self) -> None:
        if self.recorder is None or not self.recorder.is_recording:
            return
        self.busy = True
        try:
            wav = self.recorder.stop()
        except Exception as exc:  # noqa: BLE001
            self.busy = False
            log(f"could not finish the recording: {exc}")
            return
        log(f"transcribing {len(wav)} bytes")

        def work() -> None:
            from PyObjCTools import AppHelper

            from dictation.paste import insert_text

            try:
                result = transcribe(self.config.server_url, wav)
                raw = str(result.get("text", ""))
                if self.cleaner is not None:
                    raw = self.cleaner.clean(raw)
                text = prepare_text(raw, self.config.trailing_space)
                if text:
                    AppHelper.callLater(0, insert_text, text)
                    log(f"inserted {len(text)} characters")
            except Exception as exc:  # noqa: BLE001
                log(f"transcription failed: {exc}")
            finally:
                self.busy = False

        threading.Thread(target=work, daemon=True).start()

    def setup(self) -> None:
        from PyObjCTools import AppHelper

        from dictation.hotkey import HotkeyMonitor
        from dictation.permissions import prompt_accessibility, request_microphone

        prompt_accessibility()
        mic_done, mic_result = request_microphone()

        def wait() -> None:
            mic_done.wait(timeout=180)
            if mic_done.is_set() and not mic_result["ok"]:
                log("microphone permission denied. Enable it for this terminal.")
            try:
                self.server = ensure_server(self.config)
            except Exception as exc:  # noqa: BLE001
                log(f"Orukeet server is not ready: {exc}")
                AppHelper.callLater(0, AppHelper.stopEventLoop)
                return
            if self.config.cleanup:
                from dictation.cleanup import Cleaner

                self.cleaner = Cleaner(self.config.cleanup_model)
                try:
                    log("loading the cleanup model")
                    self.cleaner.load()
                except Exception as exc:  # noqa: BLE001
                    self.cleaner = None
                    log(f"cleanup model unavailable, pasting the transcript as heard: {exc}")

            def arm() -> None:
                self.hotkey = HotkeyMonitor(self.config.hotkey_code, self.begin, self.finish)
                log(f"ready. Hold {hotkey_name(self.config.hotkey_code)} and speak.")

            AppHelper.callLater(0, arm)

        threading.Thread(target=wait, daemon=True).start()
# The agent:1 ends here
