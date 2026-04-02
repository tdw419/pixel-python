# Tasks: Boot Sequence

## 1. PixelOS Kernel
- [ ] 1.1 Create `pixel_python/kernel.py` with a `PixelOS` class. `__init__(self, screen_width: int = 80, screen_height: int = 40)` creates and stores: WindowManager, ProcessTable, Scheduler, Compositor, and a running flag (False initially)
- [ ] 1.2 Implement `PixelOS.spawn(program: ComputeProgram, title: str = "Untitled", x=0, y=0, w=None, h=None, priority=0) -> int` that creates a Window, adds it to WindowManager, spawns the program in ProcessTable linked to that window's ID, returns PID
- [ ] 1.3 Implement `PixelOS.tick() -> PixelCanvas` that calls scheduler.tick() to advance all processes, then compositor.composite() to render windows, returns the root canvas

## 2. Main Loop
- [ ] 2.1 Implement `PixelOS.run(cycles: int = -1, on_frame: Callable = None) -> None` that loops calling tick() until cycles reached or running flag is False. If cycles is -1, runs forever. Calls on_frame(canvas, frame_num) each cycle.
- [ ] 2.2 Implement `PixelOS.stop() -> None` that sets running flag to False for graceful shutdown
- [ ] 2.3 Implement `PixelOS.status() -> dict` that returns a summary dict: {processes: int, running: int, paused: int, windows: int, frame: int}

## 3. Tests
- [ ] 3.1 Create `tests/test_kernel.py` with tests for: boot creates all subsystems, spawn creates window+process, tick advances scheduler and renders compositor
- [ ] 3.2 Add tests for: run(N) executes exactly N cycles, stop() halts the loop, status() returns correct counts
