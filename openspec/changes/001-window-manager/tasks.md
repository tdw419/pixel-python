# Tasks: Window Manager

## 1. Window Dataclass
- [ ] 1.1 Create `pixel_python/window.py` with a `Window` dataclass containing fields: x (int), y (int), width (int), height (int), title (str, default "Untitled"), z_order (int, default 0), visible (bool, default True), focused (bool, default False)
- [ ] 1.2 Add `Window.buffer` property that lazily creates and returns a PixelCanvas(width, height, use_gpu=False) for the window's local pixel buffer
- [ ] 1.3 Add `Window.resize(w, h)` method that updates width/height and recreates the buffer (preserving existing pixels where possible by copying)
- [ ] 1.4 Add `Window.move(x, y)` method that updates position

## 2. WindowManager Class
- [ ] 2.1 Create `WindowManager` class with `__init__(self, screen_width: int, screen_height: int)` storing root dimensions and an internal list of windows
- [ ] 2.2 Implement `WindowManager.add(window: Window) -> int` that assigns a unique window ID, clamps window to screen bounds, adds to internal list, returns the ID
- [ ] 2.3 Implement `WindowManager.remove(window_id: int) -> None` that removes the window and reassigns focus if the removed window was focused
- [ ] 2.4 Implement `WindowManager.get(window_id: int) -> Window` lookup method
- [ ] 2.5 Implement `WindowManager.windows_z_sorted() -> list[Window]` returning all visible windows sorted by z_order ascending (lowest first = background)

## 3. Focus and Z-Order Management
- [ ] 3.1 Implement `WindowManager.focus(window_id: int) -> None` that sets focused=True on target and False on all others
- [ ] 3.2 Implement `WindowManager.focused() -> Optional[Window]` returning the currently focused window or None
- [ ] 3.3 Implement `WindowManager.reorder(window_id: int, z_order: int) -> None` that updates a window's z_order
- [ ] 3.4 Implement `WindowManager.bring_to_front(window_id: int) -> None` that sets z_order to max(existing) + 1

## 4. Tests
- [ ] 4.1 Create `tests/test_window.py` with tests for Window creation, buffer allocation, resize, move
- [ ] 4.2 Add tests for WindowManager: add/remove, z-sorting, focus management, boundary clamping, bring_to_front
