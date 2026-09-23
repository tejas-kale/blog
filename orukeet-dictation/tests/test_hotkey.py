# [[file:../orukeet-dictation.org::*The hotkey][The hotkey:2]]
"""Tests for the hold-to-talk state change."""

from __future__ import annotations

import unittest

from dictation.hotkey import hold_transition


class HotkeyTests(unittest.TestCase):
    def test_edges(self) -> None:
        self.assertEqual(hold_transition(False, True), (True, "down"))
        self.assertEqual(hold_transition(True, True), (True, None))
        self.assertEqual(hold_transition(True, False), (False, "up"))
        self.assertEqual(hold_transition(False, False), (False, None))


if __name__ == "__main__":
    unittest.main()
# The hotkey:2 ends here
