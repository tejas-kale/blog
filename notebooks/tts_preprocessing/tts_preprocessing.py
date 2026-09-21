"""Generated from tts_preprocessing.org; do not edit directly."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import requests


OPENROUTER_URL = "https://openrouter.ai/api/v1"
OUTPUT_DIRECTORY = Path("audio")
RESULTS_PATH = Path("probe-results.json")
MODELS = {
    "microsoft/mai-voice-2": {
        "voice": "en-US-Harper:MAI-Voice-2",
        "price_per_million_characters": 22,
    },
    "microsoft/mai-voice-2-flash": {
        "voice": "en-US-Harper:MAI-Voice-2",
        "price_per_million_characters": 15,
    },
    "deepgram/flux-tts:free": {
        "voice": "flux-alexis-en",
        "price_per_million_characters": 0,
    },
}
AUDITION_VOICES = (
    "flux-alexis-en",
    "flux-bree-en",
    "flux-elise-en",
    "flux-haley-en",
    "flux-meena-en",
    "flux-paige-en",
)
FIXED_SENTENCE = (
    "This is the fixed voice audition sentence for the TTS preprocessing "
    "experiment. It contains a pause, a number: forty-two, and a name: Tejas Kale."
)
INITIAL_PROBE_LENGTHS = (2_000, 5_000, 10_000, 20_000)
MAXIMUM_PROBE_LENGTH = 160_000
WORKING_CHUNK_SIZE_CHARACTERS = 8_000
SPEND_CEILING_USD = 10.00
REQUEST_TIMEOUT_SECONDS = 120


@dataclass
class RequestRecord:
    model: str
    voice: str
    characters_sent: int
    estimated_cost_usd: float
    status_code: int
    content_type: str | None
    generation_id: str | None
    output_file: str | None
    error: str | None
    playable: bool


def api_key() -> str:
    value = os.environ.get("OPENROUTER_API_KEY")
    if not value:
        raise RuntimeError("OPENROUTER_API_KEY is required.")
    return value


def estimated_cost(model: str, characters: int) -> float:
    return MODELS[model]["price_per_million_characters"] * characters / 1_000_000


def checked_budget(records: list[RequestRecord], model: str, characters: int) -> None:
    projected = sum(record.estimated_cost_usd for record in records) + estimated_cost(
        model, characters
    )
    if projected > SPEND_CEILING_USD:
        raise RuntimeError(
            f"Probe would exceed the ${SPEND_CEILING_USD:.2f} ceiling "
            f"(${projected:.2f} projected); stopping."
        )


def write_checkpoint(records: list[RequestRecord], stop_reason: str | None = None) -> None:
    RESULTS_PATH.write_text(
        json.dumps(
            {
                "status": "blocked" if stop_reason else "incomplete",
                "stop_reason": stop_reason,
                "records": [asdict(record) for record in records],
                "estimated_total_cost_usd": sum(
                    record.estimated_cost_usd for record in records
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def is_playable_mp3(path: Path) -> bool:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=format_name,duration",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        return False
    format_info = json.loads(completed.stdout).get("format", {})
    return (
        "mp3" in format_info.get("format_name", "").split(",")
        and float(format_info.get("duration", 0)) > 0
    )


def synthesize(
    records: list[RequestRecord],
    model: str,
    voice: str,
    text: str,
    filename: str | None,
) -> RequestRecord:
    checked_budget(records, model, len(text))
    response = requests.post(
        f"{OPENROUTER_URL}/audio/speech",
        headers={"Authorization": f"Bearer {api_key()}"},
        json={
            "model": model,
            "input": text,
            "voice": voice,
            "response_format": "mp3",
            "speed": 1,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    content_type = response.headers.get("Content-Type")
    generation_id = response.headers.get("X-Generation-Id")
    output_file = None
    playable = False
    error = None
    if response.ok and content_type and content_type.startswith("audio/mpeg"):
        if filename:
            OUTPUT_DIRECTORY.mkdir(exist_ok=True)
            path = OUTPUT_DIRECTORY / filename
            path.write_bytes(response.content)
            output_file = str(path)
            playable = is_playable_mp3(path)
            if not playable:
                error = "ffprobe did not recognize a non-empty MP3."
    else:
        error = response.text[:1_000]

    record = RequestRecord(
        model=model,
        voice=voice,
        characters_sent=len(text),
        estimated_cost_usd=estimated_cost(model, len(text)),
        status_code=response.status_code,
        content_type=content_type,
        generation_id=generation_id,
        output_file=output_file,
        error=error,
        playable=playable,
    )
    records.append(record)
    write_checkpoint(records)
    return record


def probe_text(characters: int) -> str:
    sentence = "The quick brown fox jumps over the lazy dog. "
    return (sentence * (characters // len(sentence) + 1))[:characters]


def accepted(record: RequestRecord) -> bool:
    return record.status_code == 200 and record.content_type == "audio/mpeg"


def probe_input_limit(
    records: list[RequestRecord], model: str, voice: str
) -> dict[str, object]:
    attempts: list[dict[str, object]] = []

    def attempt(characters: int) -> bool:
        record = synthesize(records, model, voice, probe_text(characters), None)
        success = accepted(record)
        attempts.append(
            {
                "characters": characters,
                "accepted": success,
                "status_code": record.status_code,
                "error": record.error,
                "generation_id": record.generation_id,
            }
        )
        return success

    last_success = 0
    first_failure = None
    for characters in INITIAL_PROBE_LENGTHS:
        if attempt(characters):
            last_success = characters
        else:
            first_failure = characters
            break
    if first_failure is None:
        candidate = INITIAL_PROBE_LENGTHS[-1] * 2
        while candidate <= MAXIMUM_PROBE_LENGTH:
            if attempt(candidate):
                last_success = candidate
                candidate *= 2
            else:
                first_failure = candidate
                break
    if first_failure is None:
        return {
            "attempts": attempts,
            "maximum_accepted_characters": last_success,
            "first_failed_characters": None,
            "conclusion": (
                f"No failure through {MAXIMUM_PROBE_LENGTH} characters; "
                "the maximum is not established."
            ),
        }

    low, high = last_success, first_failure
    while high - low > 1:
        midpoint = (low + high) // 2
        if attempt(midpoint):
            low = midpoint
        else:
            high = midpoint
    return {
        "attempts": attempts,
        "maximum_accepted_characters": low,
        "first_failed_characters": high,
        "conclusion": "Bisection completed.",
    }


def provider_usage(generation_id: str) -> dict[str, object]:
    response = requests.get(
        f"{OPENROUTER_URL}/generation",
        headers={"Authorization": f"Bearer {api_key()}"},
        params={"id": generation_id},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if not response.ok:
        raise RuntimeError(
            f"Generation lookup for {generation_id} failed: "
            f"{response.status_code} {response.text[:1_000]}"
        )
    return response.json().get("data", response.json())


def main() -> None:
    records: list[RequestRecord] = []
    limits = {}
    try:
        for model, settings in MODELS.items():
            limits[model] = probe_input_limit(records, model, settings["voice"])

        successful_limits = [
            result["maximum_accepted_characters"]
            for result in limits.values()
            if result["first_failed_characters"] is not None
        ]
        if len(successful_limits) != len(MODELS):
            raise RuntimeError("At least one input maximum was not established; stopping.")
        lowest_limit = min(successful_limits)
        if WORKING_CHUNK_SIZE_CHARACTERS >= lowest_limit:
            raise RuntimeError(
                f"Working chunk size {WORKING_CHUNK_SIZE_CHARACTERS} is not below "
                f"the lowest measured ceiling {lowest_limit}; stopping."
            )

        mp3_record = synthesize(
            records,
            "microsoft/mai-voice-2",
            MODELS["microsoft/mai-voice-2"]["voice"],
            FIXED_SENTENCE,
            "end-to-end-mp3.mp3",
        )
        if not mp3_record.playable:
            raise RuntimeError(f"MP3 probe failed: {mp3_record.error}")

        auditions = []
        for voice in AUDITION_VOICES:
            record = synthesize(
                records,
                "deepgram/flux-tts:free",
                voice,
                FIXED_SENTENCE,
                f"audition-{voice}.mp3",
            )
            if not record.playable:
                raise RuntimeError(f"Voice audition failed for {voice}: {record.error}")
            auditions.append(asdict(record))

        provider_records = {}
        for record in records:
            if record.generation_id:
                time.sleep(1)
                provider_records[record.generation_id] = provider_usage(record.generation_id)
    except (RuntimeError, requests.RequestException) as error:
        write_checkpoint(records, str(error))
        raise

    result = {
        "status": "complete",
        "models": MODELS,
        "working_chunk_size_characters": WORKING_CHUNK_SIZE_CHARACTERS,
        "spend_ceiling_usd": SPEND_CEILING_USD,
        "input_limits": limits,
        "mp3_probe": asdict(mp3_record),
        "auditions": auditions,
        "records": [asdict(record) for record in records],
        "provider_usage": provider_records,
        "estimated_total_cost_usd": sum(record.estimated_cost_usd for record in records),
        "human_action": (
            "Tejas must listen to all audition MP3s, choose a voice, and record "
            "the choice and reason before downstream work starts."
        ),
    }
    RESULTS_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {RESULTS_PATH}")
    print("Play the MP3 probe with: afplay audio/end-to-end-mp3.mp3")


if __name__ == "__main__":
    main()
