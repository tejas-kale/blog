# [[file:../orukeet-dictation.org::*The client][The client:1]]
"""Send one WAV clip to the local worker and read the transcript."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class TranscriptionError(RuntimeError):
    pass


def prepare_text(text: str, trailing_space: bool) -> str:
    trimmed = text.strip()
    if not trimmed:
        return ""
    if trailing_space and not trimmed.endswith(" "):
        trimmed += " "
    return trimmed


def health(server_url: str, timeout: float = 3) -> bool:
    url = server_url.rstrip("/") + "/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return False
    if isinstance(body, dict) and "ok" in body:
        return bool(body["ok"])
    return True


def transcribe(server_url: str, wav: bytes, timeout: float = 120) -> dict:
    request = urllib.request.Request(
        server_url.rstrip("/") + "/transcribe",
        data=wav,
        method="POST",
    )
    request.add_header("Content-Type", "audio/wav")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise TranscriptionError(f"server returned {exc.code}: {detail}") from exc
    except (OSError, urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        raise TranscriptionError(str(exc)) from exc
    if not isinstance(body, dict) or not str(body.get("text", "")).strip():
        raise TranscriptionError("empty transcript")
    return body
# The client:1 ends here
