---
name: pixel-python
description: GPU-backed pixel programming runtime with PixelCanvas, PixelProgram, CompositeProgram, ComputeProgram, ComputePipeline, DSL, pixel_program decorator, Uniforms, ProgramRunner, DSLProgramRunner, shaders (SolidColor, Gradient, Noise, TextureLookup), Window, ConwayLife Game of Life, and Pixel OS. Covers packed RGBA uint32 convention, GPU/CPU cupy numpy dual backend, program lifecycle, blend modes, apply_kernel convolution, and double-buffered step() rendering.
---

# Pixel Python — AI Agent Skill

GPU-backed pixel programming runtime. Write per-pixel programs, compose them, and render to PNG.

## Project Location

`~/zion/projects/pixel-python/`

## Install

```bash
pip install -e .
# Optional GPU acceleration (RTX 5090 / CUDA 12)
pip install cupy-cuda12x
```

## Core Architecture

### PixelCanvas (`pixel_python.canvas`)

2D RGBA pixel buffer. GPU (cupy) when available, CPU (numpy) fallback.

CRITICAL: Pixels are packed as **uint32** in `(R<<24 | G<<16 | B<<8 | A)` format. NOT a (H,W,4) uint8 array. The internal buffer is `shape (height, width)` of `uint32`. Always use `get()`/`set()` or the pack/unpack helpers — never index the buffer directly expecting RGBA channels.

```python
from pixel_python.canvas import PixelCanvas

canvas = PixelCanvas(256, 256)              # GPU if available
canvas = PixelCanvas(256, 256, use_gpu=False)  # force CPU

# Read/write
r, g, b, a = canvas.get(x, y)
canvas.set(x, y, 255, 0, 0)       # alpha defaults to 255
canvas.fill(0, 0, 0)               # clear to black

# Kernel convolution (blur, sharpen, edge detect)
canvas.apply_kernel([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

# Double-buffered per-pixel eval
canvas.step(lambda c, x, y: (x % 256, y % 256, 128, 255))

# Output
canvas.save("out.png")             # requires Pillow
canvas.save_frame("frames/", 42)   # -> frames/frame_000042.png
```

Properties: `width`, `height`, `shape`, `is_gpu`, `device`, `buffer`.

### PixelProgram (`pixel_python.program`)

Abstract base class for per-pixel computations.

```python
from pixel_python.program import PixelProgram, ProgramRunner

class MyEffect(PixelProgram):
    def update(self, canvas, x, y):
        # Must return (r, g, b, a) tuple, each 0-255
        return (255, 0, 0, 255)

    def setup(self, canvas):
        """Called once before first frame. Optional."""
        pass

    def teardown(self, canvas):
        """Called once after last frame. Optional."""
        pass
```

Running programs:
```python
runner = ProgramRunner(canvas, my_program, frames=60, save_every=10)
paths = runner.run(output_dir="/tmp/output/")
```

### CompositeProgram (`pixel_python.program`)

Layer multiple programs with blend modes.

```python
from pixel_python.program import CompositeProgram
from pixel_python.shaders import Gradient, Noise

comp = CompositeProgram()
comp.add(Gradient("horizontal"), "normal")
comp.add(Noise(seed=42), "alpha")
```

Blend modes: `normal`, `add`, `multiply`, `alpha`.

### ComputeProgram (`pixel_python.compute`)

State-transformation programs (not pixel-based). Same lifecycle (setup/compute/teardown) but `compute(state) -> state` instead of `update(canvas, x, y) -> RGBA`.

```python
from pixel_python.compute import ComputeProgram, ComputePipeline, ComputeRunner

class MyStage(ComputeProgram):
    def compute(self, state):
        state["counter"] = state.get("counter", 0) + 1
        return state

pipe = ComputePipeline([MyStage(), AnotherStage()])
runner = ComputeRunner(pipe, frames=10)
final = runner.run({"counter": 0})
```

State gets `_meta` dict auto-injected with `frame`, `elapsed`, `start_time`.

### DSL (`pixel_python.dsl`)

Decorator-based program creation with uniforms.

```python
from pixel_python.dsl import pixel_program, DSLProgramRunner, Uniforms

@pixel_program
def fade(canvas, x, y, uniforms):
    t = uniforms["time"]       # seconds since run started
    frame = uniforms["frame"]  # 1-based frame number
    w, h = uniforms["resolution"]
    return (int(x/w * 255), int(y/h * 255 * t), 128, 255)

runner = DSLProgramRunner(canvas, fade(), frames=30, save_every=10)
paths = runner.run(output_dir="/tmp/fade/")
```

Built-in uniforms: `time` (float), `frame` (int), `resolution` (tuple).

### Built-in Shaders (`pixel_python.shaders`)

- `SolidColor(r, g, b, a=255)` — constant fill
- `Gradient(direction, start_color, end_color)` — linear gradient (`"horizontal"` or `"vertical"`)
- `Noise(seed=None, grayscale=True)` — per-pixel random
- `TextureLookup(path)` — sample from image file (requires Pillow)

### Window (`pixel_python.window`)

Rectangular region with lazy PixelCanvas buffer. Used by the Pixel OS layer.

```python
from pixel_python.window import Window

win = Window(x=10, y=10, width=128, height=64, title="Terminal", z_order=1)
win.buffer.set(0, 0, 255, 255, 255)  # write to window's local buffer
win.move(20, 20)
win.resize(200, 100)  # preserves existing pixels that fit
```

### Game of Life (`pixel_python.game_of_life`)

`ConwayLife(threshold=63.75)` — alive when mean RGB > threshold.

## Key Conventions

1. **Coordinate system**: (x, y) where x=column, y=row. Buffer indexed as `[y, x]`.
2. **Alpha**: Defaults to 255 (fully opaque). Always include alpha in return values.
3. **Double buffering**: `canvas.step()` evaluates all pixels from the OLD buffer, writes to a new buffer, then swaps. Every pixel sees the same input state within a frame.
4. **GPU fallback**: cupy is optional. `use_gpu=True` (default) falls back silently to numpy. Check `canvas.is_gpu` if you need to know.
5. **Channel packing**: `R<<24 | G<<16 | B<<8 | A` as uint32. Never assume uint8 channels.
6. **Pillow**: Required only for `save()` and `TextureLookup`. The core library has no PIL dependency.

## Pixel OS Roadmap (Phases 1-4)

The project is building a pixel-level OS on top of the rendering engine:

- Phase 1: Window Manager, Process Table, Scheduler
- Phase 2: Compositor, Text Renderer
- Phase 3: Input System, IPC/Signals, Boot Sequence
- Phase 4: Shell, Built-in Programs (Clock, SysMon, Screensaver)

Layers (top to bottom): User Programs -> System Services -> OS Kernel -> Display Server -> Rendering Substrate (PixelCanvas/PixelProgram/GPU)

## Testing

```bash
python3 -m pytest tests/ -v
# 153 tests passing as of current state
```

## Common Pitfalls

- Forgetting alpha in return tuples — always return 4 values `(r, g, b, a)`
- Indexing buffer as `[y, x]` not `[x, y]` — y is rows, x is columns
- Using `apply_kernel` with even-dimensioned kernels — must be odd-sized square
- Not handling GPU->CPU transfer when reading pixel data from a GPU canvas
- `step()` swaps buffers — if you need the previous frame's data, save a reference before calling step
- ComputeProgram `compute()` must RETURN the state dict, not mutate in-place (though mutation works, the convention is return)
