# [[file:../orukeet-dictation.org::*Permissions][Permissions:2]]
"""The Accessibility prompt key is a fixed macOS string."""

from __future__ import annotations

import unittest

from dictation.permissions import ACCESSIBILITY_OPTION


class PermissionTests(unittest.TestCase):
    def test_prompt_option_name(self) -> None:
        self.assertEqual(ACCESSIBILITY_OPTION, "AXTrustedCheckOptionPrompt")


if __name__ == "__main__":
    unittest.main()
# Permissions:2 ends here
