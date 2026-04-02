# Tasks: Text Renderer

## 1. Bitmap Font
- [ ] 1.1 Create `pixel_python/font.py` with a `BitmapFont` class. Define a class-level dict `_GLYPHS` mapping each printable ASCII character (32-126) to a list of 7 strings, each string being 5 chars of '#' or '.' representing pixel on/off (e.g. 'A' = ['..#..', '.#.#.', '#...#', '#####', '#...#', '#...#', '#...#'])
- [ ] 1.2 Implement `BitmapFont.__init__(self, fg: tuple = (0,255,0), bg: tuple = (0,0,0))` storing foreground and background colors
- [ ] 1.3 Implement `BitmapFont.render_char(canvas: PixelCanvas, ch: str, x: int, y: int) -> None` that draws the glyph for `ch` onto the canvas starting at pixel (x, y), using fg color for '#' pixels and bg for '.' pixels
- [ ] 1.4 Implement `BitmapFont.render_string(canvas: PixelCanvas, text: str, x: int, y: int) -> int` that renders each character left-to-right with 1px spacing, returns the x position after the last character

## 2. Text Buffer
- [ ] 2.1 Create `pixel_python/text_buffer.py` with a `TextBuffer` class. `__init__(self, width_chars: int, height_chars: int, font: BitmapFont)` stores dimensions in character cells and the font
- [ ] 2.2 Implement `TextBuffer.write(text: str) -> None` that appends text to an internal list of lines. Newline characters start a new line. Lines longer than width_chars wrap. When line count exceeds height_chars, scroll (drop oldest line).
- [ ] 2.3 Implement `TextBuffer.render(canvas: PixelCanvas) -> None` that clears the canvas and renders all visible lines onto it using the font, starting from line 0 at y=0
- [ ] 2.4 Implement `TextBuffer.clear() -> None` that empties all lines
- [ ] 2.5 Implement `TextBuffer.lines -> list[str]` read-only property returning current lines

## 3. Tests
- [ ] 3.1 Create `tests/test_font.py` with tests for: all printable ASCII chars have glyphs, render_char draws correct pixels, render_string advances x correctly
- [ ] 3.2 Create `tests/test_text_buffer.py` with tests for: write single line, write multiple lines, wrapping, scrolling when exceeding height, clear, render produces expected pixels
