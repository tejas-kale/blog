# [[file:../orukeet-dictation.org::*Pasting into the focused app][Pasting into the focused app:2]]
"""The part of paste we can check without a Mac."""

from __future__ import annotations

import unittest

from dictation.paste import PASTE_KEY_CODE


class PasteTests(unittest.TestCase):
    def test_command_v_uses_the_physical_v_key(self) -> None:
        self.assertEqual(PASTE_KEY_CODE, 9)


if __name__ == "__main__":
    unittest.main()
# Pasting into the focused app:2 ends here
