# [[file:../orukeet-dictation.org::*The hotkey][The hotkey:1]]
"""Hold-to-talk. The state change is a pure function; AppKit supplies the booleans."""

from __future__ import annotations

import sys

from dictation.config import GLOBE, RIGHT_OPTION, RIGHT_SHIFT


def hold_transition(held: bool, pressed: bool) -> tuple[bool, str | None]:
    if pressed and not held:
        return True, "down"
    if held and not pressed:
        return False, "up"
    return held, None


class HotkeyMonitor:
    def __init__(self, key_code: int, on_down, on_up) -> None:
        from AppKit import NSEvent, NSEventMaskFlagsChanged, NSEventMaskKeyDown, NSEventMaskKeyUp

        self.key_code = key_code
        self._on_down = on_down
        self._on_up = on_up
        self._held = False
        mask = NSEventMaskKeyDown | NSEventMaskKeyUp | NSEventMaskFlagsChanged
        self._global = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self._handle)
        self._local = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(mask, self._handle_local)
        if self._global is None:
            print(
                "orukeet-dictation: no global key monitor. "
                "Enable Accessibility for this terminal.",
                file=sys.stderr,
            )

    def _handle_local(self, event):
        self._handle(event)
        return event

    def _handle(self, event) -> None:
        try:
            pressed = _pressed(event, self.key_code)
        except Exception as exc:  # noqa: BLE001
            print(f"orukeet-dictation: hotkey error: {exc}", file=sys.stderr)
            return
        if pressed is None:
            return
        self._held, action = hold_transition(self._held, pressed)
        if action == "down":
            self._on_down()
        elif action == "up":
            self._on_up()

    def stop(self) -> None:
        from AppKit import NSEvent

        if self._global is not None:
            NSEvent.removeMonitor_(self._global)
        if self._local is not None:
            NSEvent.removeMonitor_(self._local)
        self._global = None
        self._local = None


def _pressed(event, key_code: int) -> bool | None:
    from AppKit import NSEventTypeFlagsChanged, NSEventTypeKeyDown

    if int(event.keyCode()) != key_code:
        return None
    if int(event.type()) == int(NSEventTypeFlagsChanged):
        return bool(int(event.modifierFlags()) & _flag(key_code))
    return int(event.type()) == int(NSEventTypeKeyDown)


def _flag(key_code: int) -> int:
    from AppKit import (
        NSEventModifierFlagFunction,
        NSEventModifierFlagOption,
        NSEventModifierFlagShift,
    )

    flags = {
        RIGHT_OPTION: NSEventModifierFlagOption,
        RIGHT_SHIFT: NSEventModifierFlagShift,
        GLOBE: NSEventModifierFlagFunction,
    }
    return int(flags.get(key_code, 0))
# The hotkey:1 ends here
