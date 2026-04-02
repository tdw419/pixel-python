## Why
The window manager is the first OS primitive. Without windows, there's no way
for multiple programs to render into isolated regions of the framebuffer. This
is the foundation for everything else.

## What Changes
- New file: `pixel_python/window.py`
- `Window` dataclass: x, y, width, height, title, z_order, visible, has_focus
- `WindowManager` class: add/remove/resize/move windows, z-sorted enumeration
  - Each Window owns a PixelCanvas buffer (width x height)
  - Z-ordering: higher z_order renders on top
  - Focus tracking: only one window focused at a time
  - Boundary clamping: windows can't extend past root canvas dimensions

## Impact
- Affected code: new file only
- Dependencies: uses PixelCanvas for per-window buffers
