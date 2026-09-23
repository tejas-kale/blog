"""Watch a key even when another app is in front.

macOS only delivers those events to programs that have Accessibility
permission. The monitor does not swallow the key.
"""

from __future__ import annotations

import sys

from dictation.config import GLOBE, RIGHT_OPTION, RIGHT_SHIFT


class HotkeyMonitor:
    def __init__(self, key_code: int, on_down, on_up) -> None:
        from AppKit import (
            NSEvent,
            NSEventMaskFlagsChanged,
            NSEventMaskKeyDown,
            NSEventMaskKeyUp,
        )

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
                "Turn on Accessibility for this terminal in System Settings → Privacy & Security.",
                file=sys.stderr,
            )

    def _handle_local(self, event):
        self._handle(event)
        return event

    def _handle(self, event) -> None:
        from AppKit import NSEventTypeFlagsChanged, NSEventTypeKeyDown

        try:
            if int(event.keyCode()) != self.key_code:
                return
            if int(event.type()) == int(NSEventTypeFlagsChanged):
                pressed = bool(int(event.modifierFlags()) & _flag(self.key_code))
            else:
                pressed = int(event.type()) == int(NSEventTypeKeyDown)
            if pressed and not self._held:
                self._held = True
                self._on_down()
            elif not pressed and self._held:
                self._held = False
                self._on_up()
        except Exception as exc:  # noqa: BLE001 — a raise inside the monitor removes it
            print(f"orukeet-dictation: hotkey error: {exc}", file=sys.stderr)

    def stop(self) -> None:
        from AppKit import NSEvent

        if self._global is not None:
            NSEvent.removeMonitor_(self._global)
        if self._local is not None:
            NSEvent.removeMonitor_(self._local)
        self._global = None
        self._local = None


def _flag(key_code: int) -> int:
    from AppKit import (
        NSEventModifierFlagFunction,
        NSEventModifierFlagOption,
        NSEventModifierFlagShift,
    )

    if key_code == RIGHT_OPTION:
        return int(NSEventModifierFlagOption)
    if key_code == RIGHT_SHIFT:
        return int(NSEventModifierFlagShift)
    if key_code == GLOBE:
        return int(NSEventModifierFlagFunction)
    return 0
