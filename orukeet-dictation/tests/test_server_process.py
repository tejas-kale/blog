# [[file:../orukeet-dictation.org::*Starting the worker][Starting the worker:2]]
"""Tests for the worker's environment. They do not load the model."""

from __future__ import annotations

import unittest

from dictation.config import Config
from dictation.server_process import default_server_script, server_env


class ServerProcessTests(unittest.TestCase):
    def test_env_carries_host_port_and_receipt(self) -> None:
        config = Config(
            server_url="http://127.0.0.1:9000",
            installation="/tmp/installation.json",
        )
        env = server_env(config)
        self.assertEqual(env["ORUKEET_HOST"], "127.0.0.1")
        self.assertEqual(env["ORUKEET_PORT"], "9000")
        self.assertEqual(env["ORUKEET_INSTALLATION"], "/tmp/installation.json")

    def test_default_script_points_at_the_worker(self) -> None:
        self.assertEqual(default_server_script().name, "orukeet_server.py")


if __name__ == "__main__":
    unittest.main()
# Starting the worker:2 ends here
