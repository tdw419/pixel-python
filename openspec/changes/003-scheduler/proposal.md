## Why
The scheduler is the kernel loop. It decides which process gets CPU time each
frame, handles priority boosting, and provides yield/resume semantics. This is
what makes it an OS rather than just a library.

## What Changes
- New file: `pixel_python/scheduler.py`
- `Scheduler` class: takes a ProcessTable, runs one "tick" per call (advances
  each RUNNING process by one compute() call in round-robin order), respects
  priorities (higher priority gets more ticks per cycle)

## Impact
- Affected code: new file only
- Dependencies: uses ProcessTable from process.py
