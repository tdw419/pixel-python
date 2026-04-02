## Why
Programs in the OS need to communicate. Signals (like UNIX signals) let one
process notify another. Shared memory regions let programs exchange pixel data
without copying -- they map a region of a PixelCanvas into both processes.

## What Changes
- New file: `pixel_python/ipc.py`
- `Signal` enum: SIG_TERM, SIG_PAUSE, SIG_RESUME, SIG_CUSTOM(n)
- `SignalHandler` class: register per-PID signal handlers, deliver signals
- `SharedRegion` class: named region backed by a PixelCanvas sub-area

## Impact
- Affected code: new file only
- Dependencies: ProcessTable, PixelCanvas
