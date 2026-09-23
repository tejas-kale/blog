# [[file:../orukeet-dictation.org::*The microphone][The microphone:1]]
"""Record the microphone to WAV bytes."""

from __future__ import annotations

import tempfile
from pathlib import Path

LINEAR_PCM = int.from_bytes(b"lpcm", "big")


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
        created = AVAudioRecorder.alloc().initWithURL_settings_error_(
            NSURL.fileURLWithPath_(str(self._path)),
            {
                "AVFormatIDKey": LINEAR_PCM,
                "AVSampleRateKey": 16000.0,
                "AVNumberOfChannelsKey": 1,
                "AVLinearPCMBitDepthKey": 16,
                "AVLinearPCMIsBigEndianKey": False,
                "AVLinearPCMIsFloatKey": False,
            },
            None,
        )
        recorder, error = created if isinstance(created, tuple) else (created, None)
        started = (
            recorder is not None
            and recorder.prepareToRecord()
            and recorder.recordForDuration_(float(max_seconds))
        )
        if not started:
            self.cancel()
            raise RuntimeError(f"microphone did not start ({error}). Allow microphone access for this terminal.")
        self._recorder = recorder
        self.is_recording = True

    def stop(self) -> bytes:
        path = self._finish()
        if path is None or not path.is_file():
            return b""
        data = path.read_bytes()
        path.unlink(missing_ok=True)
        if not data.startswith(b"RIFF"):
            raise RuntimeError("microphone wrote a file that is not a WAV")
        return data

    def cancel(self) -> None:
        path = self._finish()
        if path is not None:
            path.unlink(missing_ok=True)

    def _finish(self) -> Path | None:
        path = self._path
        if self._recorder is not None:
            self._recorder.stop()
        self._recorder = None
        self._path = None
        self.is_recording = False
        return path
# The microphone:1 ends here
