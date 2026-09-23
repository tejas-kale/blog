# [[file:../orukeet-dictation.org::*A WAV file][A WAV file:1]]
"""Build a mono 16-bit WAV file in memory."""

from __future__ import annotations

import struct

SAMPLE_RATE = 16_000


def pcm16_wav(samples: list[int], sample_rate: int = SAMPLE_RATE) -> bytes:
    data_size = len(samples) * 2
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,  # remaining bytes in the format chunk
        1,  # PCM
        1,  # one channel
        sample_rate,
        sample_rate * 2,
        2,  # bytes per sample frame
        16,  # bits per sample
        b"data",
        data_size,
    )
    body = b"".join(struct.pack("<h", sample) for sample in samples)
    return header + body
# A WAV file:1 ends here
