# Tasks: Process Table

## 1. Process State and Info Types
- [ ] 1.1 Create `pixel_python/process.py` with a `ProcessState` enum with values: RUNNING, PAUSED, STOPPED, ZOMBIE
- [ ] 1.2 Create `ProcessInfo` dataclass with fields: pid (int), name (str), state (ProcessState, default RUNNING), priority (int, default 0), program (ComputeProgram), window_id (Optional[int], default None), created_at (float from time.monotonic), cpu_ticks (int, default 0)

## 2. ProcessTable Class
- [ ] 2.1 Create `ProcessTable` class with `__init__(self)` storing a dict mapping pid->ProcessInfo and a _next_pid counter starting at 1
- [ ] 2.2 Implement `ProcessTable.spawn(program: ComputeProgram, name: str = None, priority: int = 0, window_id: int = None) -> int` that creates a ProcessInfo, assigns a PID, stores it, returns the PID
- [ ] 2.3 Implement `ProcessTable.kill(pid: int) -> None` that sets state to STOPPED
- [ ] 2.4 Implement `ProcessTable.pause(pid: int) -> None` and `ProcessTable.resume(pid: int) -> None` toggling between RUNNING and PAUSED states; raise ValueError if pid not found or wrong current state

## 3. Query Methods
- [ ] 3.1 Implement `ProcessTable.get(pid: int) -> ProcessInfo` (raise KeyError if not found)
- [ ] 3.2 Implement `ProcessTable.running() -> list[ProcessInfo]` returning all processes with state RUNNING, sorted by priority descending
- [ ] 3.3 Implement `ProcessTable.all() -> list[ProcessInfo]` returning all processes sorted by PID
- [ ] 3.4 Implement `ProcessTable.tick(pid: int) -> None` that increments cpu_ticks for a process (called by scheduler each frame the process runs)

## 4. Tests
- [ ] 4.1 Create `tests/test_process.py` with tests for spawn, kill, pause, resume, state transitions
- [ ] 4.2 Add tests for query methods: running(), all(), get(), tick(), error cases for invalid PIDs
