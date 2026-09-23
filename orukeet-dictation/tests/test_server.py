# [[file:../orukeet-dictation.org::*The worker][The worker:2]]
"""Tests for the worker, using the stub model."""

from __future__ import annotations

import json
import sys
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "server"))

import orukeet_server  # noqa: E402

from dictation.wav import pcm16_wav  # noqa: E402


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        transcribe, _worker = orukeet_server.make_stub_transcriber()
        self.server = orukeet_server.serve(transcribe, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def _request(self, method: str, path: str, body: bytes | None = None) -> tuple[int, dict]:
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers={"Content-Type": "audio/wav"})
        response = conn.getresponse()
        payload = json.loads(response.read())
        conn.close()
        return response.status, payload

    def test_health(self) -> None:
        status, payload = self._request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["model"], "orukeet")

    def test_transcribe_wav(self) -> None:
        status, payload = self._request("POST", "/transcribe", pcm16_wav([0, 1, -1]))
        self.assertEqual(status, 200)
        self.assertEqual(payload["text"], "stub transcript")
        self.assertEqual(payload["segments"][0]["text"], "stub transcript")

    def test_rejects_non_wav(self) -> None:
        status, payload = self._request("POST", "/transcribe", b"not-a-wav")
        self.assertEqual(status, 400)
        self.assertFalse(payload["ok"])

    def test_empty_transcript_is_an_error(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

        def transcribe(_path: Path) -> dict:
            return {"text": "  ", "segments": [], "language": None}

        self.server = orukeet_server.serve(transcribe, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        status, payload = self._request("POST", "/transcribe", pcm16_wav([0]))
        self.assertEqual(status, 422)
        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
# The worker:2 ends here
