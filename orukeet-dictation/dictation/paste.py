# [[file:../orukeet-dictation.org::*Pasting into the focused app][Pasting into the focused app:1]]
"""Paste text into the focused app, then restore the clipboard."""

from __future__ import annotations

# Physical V key. Command-V follows this key, whichever letter the layout paints on it.
PASTE_KEY_CODE = 9
TRANSIENT_TYPE = "org.nspasteboard.TransientType"
CONCEALED_TYPE = "org.nspasteboard.ConcealedType"


def insert_text(text: str) -> None:
    from AppKit import NSPasteboard, NSPasteboardTypeString
    from Foundation import NSData
    from PyObjCTools import AppHelper

    pasteboard = NSPasteboard.generalPasteboard()
    saved = _snapshot(pasteboard)
    empty = NSData.data()
    pasteboard.clearContents()
    pasteboard.setString_forType_(text, NSPasteboardTypeString)
    pasteboard.setData_forType_(empty, TRANSIENT_TYPE)
    pasteboard.setData_forType_(empty, CONCEALED_TYPE)
    stamp = int(pasteboard.changeCount())
    _press_command_v()
    AppHelper.callLater(0.2, _restore, pasteboard, saved, stamp)


def _snapshot(pasteboard) -> list[dict]:
    saved = []
    for item in pasteboard.pasteboardItems() or []:
        payload = {}
        for paste_type in item.types():
            data = item.dataForType_(paste_type)
            if data is not None:
                payload[str(paste_type)] = bytes(data)
        saved.append(payload)
    return saved


def _restore(pasteboard, saved: list[dict], stamp: int) -> None:
    from Foundation import NSData, NSPasteboardItem

    if int(pasteboard.changeCount()) != stamp:
        return
    pasteboard.clearContents()
    items = []
    for payload in saved:
        item = NSPasteboardItem.alloc().init()
        for paste_type, data in payload.items():
            item.setData_forType_(NSData.dataWithBytes_length_(data, len(data)), paste_type)
        items.append(item)
    if items:
        pasteboard.writeObjects_(items)


def _press_command_v() -> None:
    from Quartz import (
        CGEventCreateKeyboardEvent,
        CGEventPost,
        CGEventSetFlags,
        CGEventSourceCreate,
        kCGEventFlagMaskCommand,
        kCGEventSourceStateCombinedSessionState,
        kCGHIDEventTap,
    )

    source = CGEventSourceCreate(kCGEventSourceStateCombinedSessionState)
    down = CGEventCreateKeyboardEvent(source, PASTE_KEY_CODE, True)
    up = CGEventCreateKeyboardEvent(source, PASTE_KEY_CODE, False)
    CGEventSetFlags(down, kCGEventFlagMaskCommand)
    CGEventSetFlags(up, kCGEventFlagMaskCommand)
    CGEventPost(kCGHIDEventTap, down)
    CGEventPost(kCGHIDEventTap, up)
# Pasting into the focused app:1 ends here
