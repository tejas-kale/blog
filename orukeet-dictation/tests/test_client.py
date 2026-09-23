# [[file:../orukeet-dictation.org::*The client][The client:2]]
"""Tests for the HTTP client against the stub worker."""

from __future__ import annotations

import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "server"))

import orukeet_server  # noqa: E402

from dictation.client import TranscriptionError, health, prepare_text, transcribe  # noqa: E402
from dictation.wav import pcm16_wav  # noqa: E402


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        fn, _worker = orukeet_server.make_stub_transcriber()
        self.server = orukeet_server.serve(fn, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_health_and_transcribe(self) -> None:
        self.assertTrue(health(self.url))
        body = transcribe(self.url, pcm16_wav([0, 1, -1]))
        self.assertEqual(body["text"], "stub transcript")

    def test_rejects_non_wav(self) -> None:
        with self.assertRaises(TranscriptionError):
            transcribe(self.url, b"not-a-wav")

    def test_down_server(self) -> None:
        self.assertFalse(health("http://127.0.0.1:1"))

    def test_prepare_text(self) -> None:
        self.assertEqual(prepare_text("hello", True), "hello ")
        self.assertEqual(prepare_text("  hello  ", False), "hello")
        self.assertEqual(prepare_text("   ", True), "")


if __name__ == "__main__":
    unittest.main()
# The client:2 ends here
