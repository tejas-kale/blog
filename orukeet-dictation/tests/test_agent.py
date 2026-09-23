# [[file:../orukeet-dictation.org::*The agent][The agent:4]]
"""The agent module imports without AppKit."""

from __future__ import annotations

import unittest

import dictation.agent
import dictation.cleanup
import dictation.hotkey
import dictation.paste
import dictation.record


class AgentTests(unittest.TestCase):
    def test_main_is_callable(self) -> None:
        self.assertTrue(callable(dictation.agent.main))


if __name__ == "__main__":
    unittest.main()
# The agent:4 ends here
