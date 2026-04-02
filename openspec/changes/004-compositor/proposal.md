## Why
The compositor takes all windows from the WindowManager and blits them onto
a single root PixelCanvas. This is the display server -- without it, windows
exist in isolation but nothing shows up on screen.

## What Changes
- New file: `pixel_python/compositor.py`
- `Compositor` class: takes a WindowManager, owns the root PixelCanvas (screen),
  blits all z-sorted windows onto it, draws 1px borders around windows, handles
  transparency (skip alpha=0 pixels during blit)

## Impact
- Affected code: new file only
- Dependencies: WindowManager from window.py, PixelCanvas from canvas.py
