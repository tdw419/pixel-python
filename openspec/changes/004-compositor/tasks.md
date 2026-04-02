# Tasks: Compositor

## 1. Compositor Core
- [ ] 1.1 Create `pixel_python/compositor.py` with a `Compositor` class that takes `screen_width`, `screen_height` in `__init__` and creates a root PixelCanvas
- [ ] 1.2 Implement `Compositor.composite(window_manager: WindowManager) -> PixelCanvas` that clears the root canvas, then iterates z-sorted windows and blits each window's buffer onto the root canvas at the window's (x, y) position
- [ ] 1.3 Implement the blit logic: for each visible window, copy pixels from window.buffer to root canvas at (window.x, window.y). Skip pixels with alpha=0 (transparent). Clip if window extends past screen bounds.

## 2. Window Decorations
- [ ] 2.1 Add `draw_borders: bool = True` parameter to Compositor constructor
- [ ] 2.2 When draw_borders is True, draw a 1-pixel border around each visible window in the focused window's border color (white for focused, gray for unfocused: RGB 100,100,100)
- [ ] 2.3 Add `draw_title: bool = True` parameter. When True, render the window title text in the top-left of the border using the bitmap font from text_renderer (can be deferred to 005)

## 3. Output
- [ ] 3.1 Implement `Compositor.screen -> PixelCanvas` read-only property returning the root canvas
- [ ] 3.2 Implement `Compositor.save(path: str) -> str` that saves the root canvas as PNG

## 4. Tests
- [ ] 4.1 Create `tests/test_compositor.py` with tests for: basic composition of one window at (0,0), multiple windows with z-ordering, transparency (alpha=0 pixels not blitted)
- [ ] 4.2 Add tests for: clipping when window extends past screen, border drawing, focus border color difference, empty window manager produces blank canvas
