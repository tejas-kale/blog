"""Settings read from the environment.

Right Option is the default hold-to-talk key. On a MacBook Air it is more
predictable than the Globe/Fn key Wispr Flow uses.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

RIGHT_OPTION = 61
GLOBE = 63
RIGHT_SHIFT = 60
F5 = 96

_NAMES = {
    RIGHT_OPTION: "Right Option",
    GLOBE: "Globe/Fn",
    RIGHT_SHIFT: "Right Shift",
    F5: "F5",
}


def hotkey_name(code: int) -> str:
    return _NAMES.get(code, f"key code {code}")


def parse_hotkey(raw: str) -> int:
    key = raw.strip().lower()
    named = {
        "rightoption": RIGHT_OPTION,
        "right-option": RIGHT_OPTION,
        "ralt": RIGHT_OPTION,
        "option": RIGHT_OPTION,
        "globe": GLOBE,
        "fn": GLOBE,
        "rightshift": RIGHT_SHIFT,
        "right-shift": RIGHT_SHIFT,
        "f5": F5,
    }
    if key in named:
        return named[key]
    try:
        return int(key)
    except ValueError:
        return RIGHT_OPTION


def _truthy(raw: str | None, default: bool) -> bool:
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Config:
    server_url: str = "http://127.0.0.1:8765"
    hotkey_code: int = RIGHT_OPTION
    max_seconds: float = 60
    trailing_space: bool = True
    spawn_server: bool = True
    server_script: str | None = None
    installation: str | None = None

    @classmethod
    def from_env(cls, environment: dict[str, str] | None = None) -> Config:
        env = os.environ if environment is None else environment
        max_seconds = 60.0
        if raw := env.get("ORUKEET_MAX_SECONDS"):
            try:
                max_seconds = min(max(float(raw), 1.0), 120.0)
            except ValueError:
                max_seconds = 60.0
        return cls(
            server_url=env.get("ORUKEET_SERVER_URL", "http://127.0.0.1:8765"),
            hotkey_code=parse_hotkey(env["ORUKEET_HOTKEY"]) if "ORUKEET_HOTKEY" in env else RIGHT_OPTION,
            max_seconds=max_seconds,
            trailing_space=_truthy(env.get("ORUKEET_TRAILING_SPACE"), True),
            spawn_server=_truthy(env.get("ORUKEET_SPAWN_SERVER"), True),
            server_script=env.get("ORUKEET_SERVER_SCRIPT"),
            installation=env.get("ORUKEET_INSTALLATION"),
        )
