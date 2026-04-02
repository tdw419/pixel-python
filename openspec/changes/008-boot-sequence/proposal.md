## Why
The init system ties everything together: create root canvas -> start window
manager -> launch compositor -> start default programs -> enter scheduler
loop. This is the "power on" button for the pixel OS.

## What Changes
- New file: `pixel_python/kernel.py`
- `PixelOS` class: the top-level OS object that owns all subsystems and runs
  the main loop (scheduler tick + compositor render, repeat)

## Impact
- Affected code: new file only
- Dependencies: all previous modules
