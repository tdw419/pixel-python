# Tasks: IPC and Signals

## 1. Signal System
- [ ] 1.1 Create `pixel_python/ipc.py` with a `Signal` dataclass containing signal_id (int) and payload (dict, default empty). Define constants SIG_TERM=15, SIG_PAUSE=17, SIG_RESUME=19, SIG_USR1=30, SIG_USR2=31
- [ ] 1.2 Create `SignalBroker` class with `__init__(self)` storing per-pid signal queues (dict[int, deque[Signal]]) and per-pid handler functions (dict[int, dict[int, Callable]])
- [ ] 1.3 Implement `SignalBroker.send(pid: int, signal: Signal) -> None` that enqueues the signal for the target PID
- [ ] 1.4 Implement `SignalBroker.register_handler(pid: int, signal_id: int, handler: Callable[[Signal], None]) -> None`
- [ ] 1.5 Implement `SignalBroker.process_pending(pid: int) -> list[Signal]` that delivers all pending signals for a PID, calling registered handlers, returning unhandled signals

## 2. Shared Memory Regions
- [ ] 2.1 Create `SharedRegion` class with `__init__(self, name: str, width: int, height: int)` that creates a named PixelCanvas buffer
- [ ] 2.2 Implement a class-level registry `_regions: dict[str, SharedRegion]` and class methods `SharedRegion.get(name) -> SharedRegion` and `SharedRegion.list() -> list[str]`
- [ ] 2.3 Implement `SharedRegion.canvas -> PixelCanvas` property returning the shared buffer

## 3. Tests
- [ ] 3.1 Create `tests/test_ipc.py` with tests for: send/receive signals, handler invocation, unhandled signals returned, process_pending clears queue
- [ ] 3.2 Add tests for: SharedRegion creation, registry get/list, multiple processes sharing same region see same data
