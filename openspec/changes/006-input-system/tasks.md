# Tasks: Input System

## 1. Input Event Types
- [ ] 1.1 Create `pixel_python/input.py` with an `EventType` enum: KEY_DOWN, KEY_UP, MOUSE_MOVE, MOUSE_CLICK, RESIZE
- [ ] 1.2 Create `InputEvent` dataclass with fields: event_type (EventType), key (str, default ""), button (int, default 0), x (int, default 0), y (int, default 0), timestamp (float, default 0.0)

## 2. Input Router
- [ ] 2.1 Create `InputRouter` class with `__init__(self, window_manager: WindowManager, process_table: ProcessTable)` storing refs and an internal deque for the event queue
- [ ] 2.2 Implement `InputRouter.enqueue(event: InputEvent) -> None` that adds event to the queue and sets timestamp via time.monotonic() if not set
- [ ] 2.3 Implement `InputRouter.drain() -> list[InputEvent]` that returns all queued events and clears the queue
- [ ] 2.4 Implement `InputRouter.route_to_focused() -> dict[int, list[InputEvent]]` that groups events by the PID of the focused window's process, returns {pid: [events]}

## 3. Convenience Methods
- [ ] 3.1 Implement `InputRouter.key_down(key: str) -> None` shorthand that creates and enqueues a KEY_DOWN event
- [ ] 3.2 Implement `InputRouter.mouse_click(x: int, y: int, button: int = 1) -> None` shorthand
- [ ] 3.3 Implement `InputRouter.mouse_click_focus(window_manager: WindowManager) -> None` that takes a MOUSE_CLICK event's x,y and finds which window was clicked, then focuses it via window_manager.focus()

## 4. Tests
- [ ] 4.1 Create `tests/test_input.py` with tests for: event creation, enqueue/drain, route_to_focused returns events for correct PID
- [ ] 4.2 Add tests for: convenience methods create correct event types, mouse_click_focus changes focus to clicked window
