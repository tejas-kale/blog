# [[file:../orukeet-dictation.org::*Settings][Settings:2]]
"""Tests for environment settings."""

from __future__ import annotations

import unittest

from dictation.config import F5, GLOBE, RIGHT_OPTION, Config, hotkey_name, parse_hotkey


class ConfigTests(unittest.TestCase):
    def test_names_and_limits(self) -> None:
        config = Config.from_env(
            {
                "ORUKEET_HOTKEY": "globe",
                "ORUKEET_MAX_SECONDS": "999",
                "ORUKEET_TRAILING_SPACE": "false",
                "ORUKEET_SERVER_URL": "http://127.0.0.1:9000",
                "ORUKEET_SPAWN_SERVER": "no",
                "ORUKEET_CLEANUP": "no",
            }
        )
        self.assertEqual(config.hotkey_code, GLOBE)
        self.assertEqual(config.max_seconds, 120)
        self.assertFalse(config.trailing_space)
        self.assertFalse(config.spawn_server)
        self.assertFalse(config.cleanup)
        self.assertEqual(config.server_url, "http://127.0.0.1:9000")

    def test_default_hotkey(self) -> None:
        self.assertEqual(Config.from_env({}).hotkey_code, RIGHT_OPTION)
        self.assertEqual(parse_hotkey("right-option"), RIGHT_OPTION)
        self.assertEqual(parse_hotkey("96"), F5)
        self.assertEqual(parse_hotkey("not-a-key"), RIGHT_OPTION)
        self.assertEqual(hotkey_name(RIGHT_OPTION), "Right Option")


if __name__ == "__main__":
    unittest.main()
# Settings:2 ends here
