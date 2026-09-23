"""Record the microphone to a 16 kHz mono WAV byte string.

Uses Apple's AVAudioRecorder through PyObjC, the same API the old Swift
agent used. The orange microphone dot in the menu bar is on while you hold
the hotkey.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

# Apple's four-character code 'lpcm' (linear PCM).
LINEAR_PCM = 1819304813


class Recorder:
    def __init__(self) -> None:
        self._recorder = None
        self._path: Path | None = None
        self.is_recording = False

    def start(self, max_seconds: float) -> None:
        self.cancel()
        from AVFoundation import AVAudioRecorder
        from Foundation import NSURL

        handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        handle.close()
        self._path = Path(handle.name)
        url = NSURL.fileURLWithPath_(str(self._path))
        settings = {
            "AVFormatIDKey": LINEAR_PCM,
            "AVSampleRateKey": 16000.0,
            "AVNumberOfChannelsKey": 1,
            "AVLinearPCMBitDepthKey": 16,
            "AVLinearPCMIsBigEndianKey": False,
            "AVLinearPCMIsFloatKey": False,
        }
        created = AVAudioRecorder.alloc().initWithURL_settings_error_(url, settings, None)
        recorder, error = created if isinstance(created, tuple) else (created, None)
        if recorder is None:
            self.cancel()
            raise RuntimeError(f"could not open the microphone ({error})")
        if not recorder.prepareToRecord() or not recorder.recordForDuration_(float(max_seconds)):
            self.cancel()
            raise RuntimeError(
                "microphone did not start. Allow microphone access for this terminal "
                "in System Settings → Privacy & Security → Microphone."
            )
        self._recorder = recorder
        self.is_recording = True

    def stop(self) -> bytes:
        path = self._path
        try:
            if self._recorder is not None:
                self._recorder.stop()
            if path is None or not path.is_file():
                return b""
            data = path.read_bytes()
        finally:
            self._recorder = None
            self._path = None
            self.is_recording = False
            if path is not None:
                path.unlink(missing_ok=True)
        if data and not data.startswith(b"RIFF"):
            raise RuntimeError("microphone wrote a file that is not a WAV")
        return data

    def cancel(self) -> None:
        path = self._path
        if self._recorder is not None:
            self._recorder.stop()
        self._recorder = None
        self._path = None
        self.is_recording = False
        if path is not None:
            path.unlink(missing_ok=True)
