## Why
Every OS needs a process table. This tracks running ComputeProgram instances,
assigns them PIDs, and manages their lifecycle (running/paused/stopped). This
decouples the "what is running" question from the scheduler.

## What Changes
- New file: `pixel_python/process.py`
- `ProcessState` enum: RUNNING, PAUSED, STOPPED, ZOMBIE
- `ProcessInfo` dataclass: pid, name, state, priority, program ref, window_id, created_at, cpu_ticks
- `ProcessTable` class: spawn/register/kill/pause/resume processes, query by PID/state

## Impact
- Affected code: new file only
- Dependencies: uses ComputeProgram from compute.py
