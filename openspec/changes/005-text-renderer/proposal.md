## Why
Every OS needs a terminal. Before we can build one, we need to render text
onto pixel buffers. This provides a bitmap font (5x7 glyphs for printable
ASCII) and a scrollable text buffer that writes characters into a Window's
pixel buffer.

## What Changes
- New file: `pixel_python/font.py` -- bitmap font definitions and character rendering
- New file: `pixel_python/text_buffer.py` -- scrollable text buffer that renders into a PixelCanvas

## Impact
- Affected code: new files only
- Dependencies: PixelCanvas from canvas.py
