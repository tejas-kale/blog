"""Tests for the parts of the agent that do not need a Mac."""

from __future__ import annotations

import json
import struct
import sys
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "server"))

import orukeet_server  # noqa: E402

from dictation.client import TranscriptionError, health, prepare_text, transcribe  # noqa: E402
from dictation.config import F5, GLOBE, RIGHT_OPTION, Config, hotkey_name, parse_hotkey  # noqa: E402
from dictation.paste import PASTE_KEY_CODE  # noqa: E402


def _wav(samples: list[int]) -> bytes:
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
        16000,
        32000,
        2,
        16,
        b"data",
        data_size,
    )
    return header + b"".join(struct.pack("<h", sample) for sample in samples)


class ConfigTests(unittest.TestCase):
    def test_named_hotkeys_and_limits(self) -> None:
        config = Config.from_env(
            {
                "ORUKEET_HOTKEY": "globe",
                "ORUKEET_MAX_SECONDS": "999",
                "ORUKEET_TRAILING_SPACE": "false",
                "ORUKEET_SERVER_URL": "http://127.0.0.1:9000",
                "ORUKEET_SPAWN_SERVER": "no",
            }
        )
        self.assertEqual(config.hotkey_code, GLOBE)
        self.assertEqual(config.max_seconds, 120)
        self.assertFalse(config.trailing_space)
        self.assertFalse(config.spawn_server)
        self.assertEqual(config.server_url, "http://127.0.0.1:9000")

    def test_default_hotkey_is_right_option(self) -> None:
        self.assertEqual(Config.from_env({}).hotkey_code, RIGHT_OPTION)
        self.assertEqual(parse_hotkey("right-option"), RIGHT_OPTION)
        self.assertEqual(parse_hotkey("96"), F5)
        self.assertEqual(parse_hotkey("not-a-key"), RIGHT_OPTION)
        self.assertEqual(hotkey_name(RIGHT_OPTION), "Right Option")

    def test_trailing_space(self) -> None:
        self.assertEqual(prepare_text("hello", True), "hello ")
        self.assertEqual(prepare_text("  hello  ", False), "hello")
        self.assertEqual(prepare_text("   ", True), "")


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        transcribe_fn, _worker = orukeet_server.make_stub_transcriber()
        self.server = orukeet_server.serve(transcribe_fn, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_health_and_transcribe(self) -> None:
        self.assertTrue(health(self.url))
        body = transcribe(self.url, _wav([0, 1, -1]))
        self.assertEqual(body["text"], "stub transcript")

    def test_rejects_non_wav(self) -> None:
        with self.assertRaises(TranscriptionError):
            transcribe(self.url, b"not-a-wav")

    def test_down_server(self) -> None:
        self.assertFalse(health("http://127.0.0.1:1"))


class ImportTests(unittest.TestCase):
    def test_agent_imports_without_appkit(self) -> None:
        import dictation.agent
        import dictation.hotkey
        import dictation.paste
        import dictation.record

        self.assertTrue(callable(dictation.agent.main))


class PasteKeyTests(unittest.TestCase):
    def test_paste_uses_physical_v_key(self) -> None:
        self.assertEqual(PASTE_KEY_CODE, 9)


class ServerContractTests(unittest.TestCase):
    def test_health_payload_shape(self) -> None:
        transcribe_fn, _worker = orukeet_server.make_stub_transcriber()
        server = orukeet_server.serve(transcribe_fn, host="127.0.0.1", port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
            conn.request("GET", "/health")
            response = conn.getresponse()
            payload = json.loads(response.read())
            conn.close()
            self.assertEqual(payload["model"], "orukeet")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
