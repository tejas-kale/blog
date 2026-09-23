# [[file:../orukeet-dictation.org::*The worker][The worker:1]]
"""Keep one Orukeet model loaded and transcribe WAV posts on localhost."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

TranscribeFn = Callable[[Path], dict[str, Any]]


def load_installation(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def make_orukeet_transcriber(installation: Path) -> tuple[TranscribeFn, Any]:
    from orukeet import Orukeet

    config = load_installation(installation)
    asr = Orukeet(config["model"], config["runtime"], device=config["device"])
    asr.__enter__()

    def transcribe(path: Path) -> dict[str, Any]:
        result = asr.transcribe(path)
        if not isinstance(result, dict):
            result = {"text": str(result)}
        result.setdefault("text", "")
        result.setdefault("segments", [])
        result.setdefault("language", None)
        return result

    return transcribe, asr


def make_stub_transcriber() -> tuple[TranscribeFn, Any]:
    def transcribe(path: Path) -> dict[str, Any]:
        return {
            "text": "stub transcript",
            "segments": [{"text": "stub transcript", "start": 0, "end": 0}],
            "language": None,
            "bytes": path.stat().st_size,
        }

    return transcribe, None


class Handler(BaseHTTPRequestHandler):
    lock: threading.Lock
    ready: bool
    max_body: int

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") in {"", "/health"}:
            self._json(200, {"ok": self.ready, "model": "orukeet"})
            return
        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/transcribe":
            self._json(404, {"ok": False, "error": "not found"})
            return
        if not self.ready:
            self._json(503, {"ok": False, "error": "model not loaded"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > self.max_body:
            self._json(413, {"ok": False, "error": "audio too large or empty"})
            return
        wav = self.rfile.read(length)
        if len(wav) < 44 or wav[:4] != b"RIFF":
            self._json(400, {"ok": False, "error": "expected a WAV body"})
            return
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            handle.write(wav)
            temp_path = Path(handle.name)
        try:
            with self.lock:
                result = self.server.transcribe_fn(temp_path)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"ok": False, "error": str(exc)})
            return
        finally:
            temp_path.unlink(missing_ok=True)
        if not str(result.get("text", "")).strip():
            self._json(422, {"ok": False, "error": "empty transcript"})
            return
        self._json(
            200,
            {
                "text": result.get("text", ""),
                "segments": result.get("segments", []),
                "language": result.get("language"),
            },
        )


def serve(
    transcribe_fn: TranscribeFn,
    host: str = "127.0.0.1",
    port: int = 8765,
    ready: bool = True,
) -> ThreadingHTTPServer:
    Handler.lock = threading.Lock()
    Handler.ready = ready
    Handler.max_body = int(os.environ.get("ORUKEET_MAX_BODY", str(12 * 1024 * 1024)))
    server = ThreadingHTTPServer((host, port), Handler)
    server.transcribe_fn = transcribe_fn  # type: ignore[attr-defined]
    return server


def main() -> int:
    host = os.environ.get("ORUKEET_HOST", "127.0.0.1")
    port = int(os.environ.get("ORUKEET_PORT", "8765"))
    stub = os.environ.get("ORUKEET_STUB", "").lower() in {"1", "true", "yes"}
    installation = Path(
        os.environ.get(
            "ORUKEET_INSTALLATION",
            str(Path(__file__).resolve().parent.parent / "installation.json"),
        )
    )
    try:
        if stub:
            transcribe_fn, worker = make_stub_transcriber()
        else:
            transcribe_fn, worker = make_orukeet_transcriber(installation)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to load Orukeet: {exc}", file=sys.stderr)
        return 1
    server = serve(transcribe_fn, host=host, port=port)
    print(f"orukeet-server listening on http://{host}:{port}", file=sys.stderr, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        closer = getattr(worker, "__exit__", None)
        if closer is not None:
            closer(None, None, None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# The worker:1 ends here
