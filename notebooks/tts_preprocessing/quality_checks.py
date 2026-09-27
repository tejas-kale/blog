"""Independent audio checks for the TTS preprocessing experiment."""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path

WHISPER_MODEL = "mlx-community/whisper-tiny"
MAX_WER = 0.02
MAX_SEAM_DELTA_LU = 3.0
MAX_PLAUSIBLE_WPM = 360


def words(text: str) -> list[str]:
    """Tokenise speech text without case or punctuation differences."""
    normalised = unicodedata.normalize("NFKC", text).casefold()
    return re.findall(r"[\w]+(?:['’][\w]+)?", normalised, flags=re.UNICODE)


def word_error_rate(reference: str, hypothesis: str) -> float:
    """Return word-level Levenshtein distance divided by reference words."""
    expected, actual = words(reference), words(hypothesis)
    if not expected:
        return 0.0 if not actual else 1.0
    previous = list(range(len(actual) + 1))
    for row, expected_word in enumerate(expected, 1):
        current = [row]
        for column, actual_word in enumerate(actual, 1):
            current.append(min(
                current[-1] + 1,
                previous[column] + 1,
                previous[column - 1] + (expected_word != actual_word),
            ))
        previous = current
    return previous[-1] / len(expected)


def word_diff(reference: str, hypothesis: str) -> str:
    """Render a readable word-level diff for human review."""
    return "\n".join(difflib.unified_diff(
        words(reference), words(hypothesis), fromfile="sent", tofile="heard", lineterm=""
    ))


def probe_duration(audio_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)],
        check=True, capture_output=True, text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def integrated_loudness(audio_path: Path) -> float:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio_path), "-filter_complex", "ebur128=framelog=verbose", "-f", "null", "-"],
        check=True, capture_output=True, text=True,
    )
    matches = re.findall(
        r"Integrated loudness:\s*I:\s*(-?\d+(?:\.\d+)?)\s*LUFS", result.stderr
    )
    if not matches:
        raise ValueError(f"ffmpeg did not report integrated loudness for {audio_path}")
    return float(matches[-1])


def transcribe(audio_path: Path, model: str = WHISPER_MODEL) -> str:
    """Transcribe locally with Whisper running through Apple's MLX runtime."""
    try:
        import mlx_whisper
    except ImportError as error:
        raise RuntimeError("Install mlx-whisper in the experiment Python environment") from error
    response = mlx_whisper.transcribe(
        str(audio_path), path_or_hf_repo=model, language="en", condition_on_previous_text=False
    )
    transcript = response.get("text", "").strip()
    if not transcript:
        raise ValueError(f"Whisper returned an empty transcript for {audio_path}")
    return transcript


def duration_metrics(text: str, seconds: float) -> dict[str, float | bool]:
    expected = len(words(text))
    minimum = expected * 60 / MAX_PLAUSIBLE_WPM
    return {
        "duration_seconds": round(seconds, 3),
        "expected_min_duration_seconds": round(minimum, 3),
        "duration_flag": seconds < minimum,
    }


def add_seam_metrics(rows: list[dict[str, object]], threshold: float = MAX_SEAM_DELTA_LU) -> None:
    """Add each next-chunk loudness change to its left-hand render row."""
    for index, row in enumerate(rows):
        if index + 1 == len(rows):
            row["seam_delta_lu"] = ""
            row["seam_flag"] = False
            continue
        delta = abs(float(row["loudness_lufs"]) - float(rows[index + 1]["loudness_lufs"]))
        row["seam_delta_lu"] = round(delta, 2)
        row["seam_flag"] = delta > threshold


def check_loudness_fixture() -> float:
    """Generate a calibrated -23 LUFS tone and check ffmpeg parses it."""
    with tempfile.TemporaryDirectory() as directory:
        fixture = Path(directory) / "known-level.wav"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
            "sine=frequency=1000:duration=5", "-af", "volume=0.8",
            "-c:a", "pcm_s16le", str(fixture),
        ], check=True, capture_output=True, text=True)
        measured = integrated_loudness(fixture)
    if abs(measured - (-23.0)) > 0.5:
        raise AssertionError(f"Expected fixture at -23 LUFS, parsed {measured:.2f} LUFS")
    return measured


def analyse_render(
    audio_path: Path,
    text: str,
    transcript_path: Path,
    diff_path: Path,
    cached_transcript: str | None = None,
    model: str = WHISPER_MODEL,
) -> dict[str, object]:
    transcript = cached_transcript if cached_transcript is not None else transcribe(audio_path, model)
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(transcript + "\n", encoding="utf-8")
    diff = word_diff(text, transcript)
    diff_path.write_text(diff + ("\n" if diff else ""), encoding="utf-8")
    wer = word_error_rate(text, transcript)
    experiment_root = Path(__file__).resolve().parent
    return {
        "transcript_file": str(transcript_path.resolve().relative_to(experiment_root)),
        "word_diff_file": str(diff_path.resolve().relative_to(experiment_root)),
        "audio_sha256": hashlib.sha256(audio_path.read_bytes()).hexdigest(),
        "asr_model": model,
        "wer": round(wer, 5),
        "wer_flag": wer > MAX_WER,
        **duration_metrics(text, probe_duration(audio_path)),
        "loudness_lufs": round(integrated_loudness(audio_path), 2),
    }
