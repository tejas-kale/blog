#!/usr/bin/env python3
"""Tests for the Orukeet localhost worker (stub mode, no model download)."""

from __future__ import annotations

import json
import struct
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

import orukeet_server  # noqa: E402


def pcm16_mono_wav(samples: list[int], sample_rate: int = 16000) -> bytes:
    data_size = len(samples) * 2
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        1,
        sample_rate,
        sample_rate * 2,
        2,
        16,
        b"data",
        data_size,
    )
    body = b"".join(struct.pack("<h", sample) for sample in samples)
    return header + body


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        transcribe, _ = orukeet_server.make_stub_transcriber()
        self.server = orukeet_server.serve(transcribe, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def _client(self) -> HTTPConnection:
        return HTTPConnection("127.0.0.1", self.port, timeout=5)

    def test_health(self) -> None:
        conn = self._client()
        conn.request("GET", "/health")
        response = conn.getresponse()
        payload = json.loads(response.read())
        conn.close()
        self.assertEqual(response.status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["model"], "orukeet")

    def test_transcribe_wav(self) -> None:
        wav = pcm16_mono_wav([0, 1, -1, 1234])
        conn = self._client()
        conn.request("POST", "/transcribe", body=wav, headers={"Content-Type": "audio/wav"})
        response = conn.getresponse()
        payload = json.loads(response.read())
        conn.close()
        self.assertEqual(response.status, 200)
        self.assertEqual(payload["text"], "stub transcript")
        self.assertEqual(payload["segments"][0]["text"], "stub transcript")

    def test_rejects_non_wav(self) -> None:
        conn = self._client()
        conn.request("POST", "/transcribe", body=b"not-a-wav", headers={"Content-Type": "audio/wav"})
        response = conn.getresponse()
        payload = json.loads(response.read())
        conn.close()
        self.assertEqual(response.status, 400)
        self.assertFalse(payload["ok"])

    def test_empty_transcript_is_an_error(self) -> None:
        def transcribe(_path: Path) -> dict:
            return {"text": "  ", "segments": [], "language": None}

        self.server.shutdown()
        self.server.server_close()
        self.server = orukeet_server.serve(transcribe, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        wav = pcm16_mono_wav([0, 0])
        conn = self._client()
        conn.request("POST", "/transcribe", body=wav, headers={"Content-Type": "audio/wav"})
        response = conn.getresponse()
        self.assertEqual(response.status, 422)
        conn.close()


class WavHeaderTests(unittest.TestCase):
    def test_header_layout_matches_swift_encoder(self) -> None:
        wav = pcm16_mono_wav([1, 2], sample_rate=16000)
        self.assertEqual(wav[:4], b"RIFF")
        self.assertEqual(wav[8:12], b"WAVE")
        self.assertEqual(struct.unpack_from("<H", wav, 22)[0], 1)
        self.assertEqual(struct.unpack_from("<I", wav, 24)[0], 16000)
        self.assertEqual(struct.unpack_from("<H", wav, 34)[0], 16)


if __name__ == "__main__":
    unittest.main()
