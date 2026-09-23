# [[file:../orukeet-dictation.org::*A WAV file][A WAV file:2]]
"""Tests for the WAV header."""

from __future__ import annotations

import struct
import unittest

from dictation.wav import SAMPLE_RATE, pcm16_wav


class WavTests(unittest.TestCase):
    def test_header_layout(self) -> None:
        wav = pcm16_wav([1, 2], sample_rate=SAMPLE_RATE)
        self.assertEqual(wav[:4], b"RIFF")
        self.assertEqual(wav[8:12], b"WAVE")
        self.assertEqual(struct.unpack_from("<H", wav, 22)[0], 1)
        self.assertEqual(struct.unpack_from("<I", wav, 24)[0], SAMPLE_RATE)
        self.assertEqual(struct.unpack_from("<H", wav, 34)[0], 16)
        self.assertEqual(len(wav), 44 + 4)

    def test_empty_clip_is_only_a_header(self) -> None:
        self.assertEqual(len(pcm16_wav([])), 44)


if __name__ == "__main__":
    unittest.main()
# A WAV file:2 ends here
