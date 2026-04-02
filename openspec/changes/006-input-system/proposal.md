## Why
An OS needs input. This module provides an event queue for keyboard/mouse
events and routes them to the focused window's process. It's the bridge
between user interaction and program behavior.

## What Changes
- New file: `pixel_python/input.py`
- `InputEvent` dataclass: event_type (KEY_DOWN, KEY_UP, MOUSE_MOVE, MOUSE_CLICK, RESIZE), key/button, x, y
- `InputRouter` class: enqueue events, deliver to focused window's process via process table

## Impact
- Affected code: new file only
- Dependencies: WindowManager, ProcessTable
