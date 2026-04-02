# Tasks: Scheduler

## 1. Scheduler Core
- [ ] 1.1 Create `pixel_python/scheduler.py` with a `Scheduler` class that takes a ProcessTable in `__init__` and stores a shared state dict (the OS kernel state)
- [ ] 1.2 Implement `Scheduler.tick() -> dict` that: gets all RUNNING processes sorted by priority desc, calls `program.compute(state)` on each, increments cpu_ticks via ProcessTable.tick(), returns the updated state dict
- [ ] 1.3 Implement `Scheduler.run(cycles: int = 1) -> dict` that calls tick() N times, returning final state

## 2. Priority and Time Slicing
- [ ] 2.1 Add `max_ticks_per_cycle` parameter to Scheduler (default None = no limit). When set, each tick() runs at most this many compute calls total across all processes
- [ ] 2.2 Add priority weighting: processes with higher priority get proportionally more compute calls per tick. A process with priority 2 gets 2x the calls of priority 1
- [ ] 2.3 Add `_round_robin_order()` internal method that returns the execution order for one tick as a flat list of (pid, ProcessInfo) pairs, expanded by priority weights

## 3. State Injection
- [ ] 3.1 Each process's compute() receives a copy of the kernel state dict with extra keys injected: `_pid`, `_priority`, `_cpu_ticks`, `_frame` (global tick counter)
- [ ] 3.2 Add a `_frame_counter` attribute to Scheduler incremented each tick()

## 4. Tests
- [ ] 4.1 Create `tests/test_scheduler.py` with tests for: basic tick with one process, round-robin with multiple processes, priority weighting (verify higher priority gets more calls)
- [ ] 4.2 Add tests for: max_ticks_per_cycle limiting, state injection (_pid, _priority, _cpu_ticks present), paused processes skipped, run(N) calls tick N times
