# [[file:../orukeet-dictation.org::*Starting the worker][Starting the worker:1]]
"""Start the Orukeet worker when it is not already listening."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

from dictation.client import health
from dictation.config import Config

ROOT = Path(__file__).resolve().parents[1]


def default_server_script() -> Path:
    return ROOT / "server" / "orukeet_server.py"


def server_env(config: Config) -> dict[str, str]:
    env = os.environ.copy()
    parsed = urllib.parse.urlparse(config.server_url)
    if parsed.hostname:
        env["ORUKEET_HOST"] = parsed.hostname
    if parsed.port:
        env["ORUKEET_PORT"] = str(parsed.port)
    if config.installation:
        env["ORUKEET_INSTALLATION"] = config.installation
    return env


def ensure_server(config: Config) -> subprocess.Popen | None:
    if health(config.server_url):
        return None
    if not config.spawn_server:
        raise RuntimeError(f"nothing is listening at {config.server_url}")

    script = Path(config.server_script) if config.server_script else default_server_script()
    if not script.is_file():
        raise RuntimeError(f"server script not found: {script}")

    print("orukeet-dictation: loading Orukeet. The first load can take a minute.", file=sys.stderr)
    process = subprocess.Popen([sys.executable, str(script)], env=server_env(config))
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Orukeet server exited with status {process.returncode}")
        if health(config.server_url):
            return process
        time.sleep(0.5)
    process.terminate()
    raise RuntimeError("Orukeet server did not become ready within 3 minutes")
# Starting the worker:1 ends here
