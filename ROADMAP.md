# Pixel Python OS Roadmap

A pixel-level operating system built on the pixel-python rendering engine.
Programs render to a shared framebuffer, managed by a kernel that schedules,
composites, and routes input. Think X11 for pixel art.

## Existing Inventory (Done)

- [x] PixelCanvas -- 2D RGBA buffer with GPU/CPU backend (canvas.py)
- [x] PixelProgram -- per-pixel computation ABC (program.py)
- [x] CompositeProgram -- layered blend composition (program.py)
- [x] ProgramRunner -- frame loop with auto-save (program.py)
- [x] ComputeProgram -- state-transformation ABC (compute.py)
- [x] ComputePipeline -- sequential state chaining (compute.py)
- [x] ComputeRunner -- frame loop for state programs (compute.py)
- [x] Uniforms + DSLProgramRunner -- shader-like uniforms (dsl.py)
- [x] @pixel_program / @compute_program decorators (dsl.py, compute.py)
- [x] Shader library: SolidColor, Gradient, Noise, TextureLookup (shaders.py)
- [x] 153 tests passing

## Phase 1: OS Primitives

The window manager, process table, and scheduler -- the three things that
turn a rendering library into an OS.

- [ ] 001-window-manager: Window class (rect region, title, z-order, visible flag) + WindowManager (add/remove/resize/move/focus, z-sorted enumeration)
- [ ] 002-process-table: ProcessTable (PID allocation, state tracking: running/paused/stopped/zombie, priority levels) + ProcessHandle (reference to a running ComputeProgram with metadata)
- [ ] 003-scheduler: Scheduler (round-robin frame slicing across registered processes, priority boosting, yield/resume, configurable time quanta per cycle)

## Phase 2: Display Server

The compositor that renders all windows onto the framebuffer, and the
built-in terminal program.

- [ ] 004-compositor: Compositor (iterate z-sorted windows, clip to canvas bounds, render each window's buffer onto the shared framebuffer with border decorations)
- [ ] 005-text-renderer: Font class (bitmap font from dict of char -> 5x7 glyph arrays) + TextWindow (scrollable text buffer rendered into a Window's pixel buffer)

## Phase 3: System Services

Input routing, inter-process communication, and the boot sequence.

- [ ] 006-input-system: InputEvent dataclass (key/mouse/resize events) + InputRouter (event queue, focus tracking, deliver events to focused window's process)
- [ ] 007-ipc-signals: Signal system (SIG_TERM, SIG_PAUSE, SIG_RESUME, custom signals) + SharedRegion (named shared memory region mapped into a canvas sub-buffer)
- [ ] 008-boot-sequence: Init system (boot sequence: create root canvas -> start window manager -> launch compositor -> start terminal -> enter scheduler loop) + graceful shutdown

## Phase 4: Shell & Utilities

Programs that ship with the OS.

- [ ] 009-shell: Command parser + built-in commands (list, kill, spawn, focus, move, resize, clear)
- [ ] 010-builtins: Clock program, system monitor (CPU/memory/process stats rendered as ASCII graphs), screensaver

## Architecture

```
┌─────────────────────────────────────┐
│            User Programs            │
│  (ComputeProgram subclasses)        │
├─────────────────────────────────────┤
│         System Services             │
│  Shell | Clock | SysMon | Screensaver│
├─────────────────────────────────────┤
│           OS Kernel                 │
│  Scheduler | IPC | Input Router     │
├─────────────────────────────────────┤
│        Display Server               │
│  Window Manager | Compositor        │
├─────────────────────────────────────┤
│       Rendering Substrate           │
│  PixelCanvas | PixelProgram | GPU   │
└─────────────────────────────────────┘
```

## Success Criteria

1. Multiple programs rendering simultaneously in separate windows
2. Scheduler fairly distributing frame time across processes
3. Compositor blending all windows onto a single output
4. Terminal window with scrollable text output
5. Full boot-to-shell cycle with keyboard input
6. All new code tested (aim for 250+ total tests)
