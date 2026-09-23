# [[file:../orukeet-dictation.org::*The microphone][The microphone:2]]
"""The format code is Apple's 'lpcm'. Recording itself needs a Mac."""

from __future__ import annotations

import unittest

from dictation.record import LINEAR_PCM


class RecordTests(unittest.TestCase):
    def test_linear_pcm_code(self) -> None:
        self.assertEqual(LINEAR_PCM, 1_819_304_813)
        self.assertEqual(LINEAR_PCM, int.from_bytes(b"lpcm", "big"))


if __name__ == "__main__":
    unittest.main()
# The microphone:2 ends here
