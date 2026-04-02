# Pixel Python

A GPU-backed pixel programming runtime. Write per-pixel programs, compose them, and render to PNG.

## Install

```bash
pip install -e .
# Optional: GPU acceleration
pip install cupy-cuda12x
```

## Quick Start

```python
from pixel_python.canvas import PixelCanvas

# Create a 256x256 canvas (GPU if available, else CPU)
canvas = PixelCanvas(256, 256)

# Set pixels
canvas.set(10, 20, 255, 0, 0)        # red pixel at (10, 20)
canvas.fill(0, 0, 0)                   # fill black

# Save to PNG
canvas.save("output.png")
```

## Pixel Programs

Define effects by subclassing `PixelProgram`:

```python
from pixel_python.program import PixelProgram, ProgramRunner
from pixel_python.canvas import PixelCanvas

class Checkerboard(PixelProgram):
    def update(self, canvas, x, y):
        if (x + y) % 2 == 0:
            return (255, 255, 255, 255)
        return (0, 0, 0, 255)

canvas = PixelCanvas(64, 64, use_gpu=False)
runner = ProgramRunner(canvas, Checkerboard(), frames=1)
runner.run()
canvas.save("checkerboard.png")
```

## Declarative DSL

Use the `@pixel_program` decorator for simple effects:

```python
from pixel_python.dsl import pixel_program, DSLProgramRunner, Uniforms
from pixel_python.canvas import PixelCanvas

@pixel_program
def fade(canvas, x, y, uniforms):
    t = uniforms["time"]
    r = int((x / canvas.width) * 255)
    g = int((y / canvas.height) * 255 * t)
    return (r, g, 128, 255)

canvas = PixelCanvas(128, 128, use_gpu=False)
runner = DSLProgramRunner(canvas, fade(), frames=30, save_every=10)
paths = runner.run(output_dir="/tmp/fade/")
```

## Composite Programs

Layer multiple effects with blend modes:

```python
from pixel_python.program import CompositeProgram
from pixel_python.shaders import SolidColor, Gradient, Noise

comp = CompositeProgram()
comp.add(Gradient("horizontal"), "normal")
comp.add(Noise(seed=42), "alpha")
```

Blend modes: `normal`, `add`, `multiply`, `alpha`.

## Built-in Shaders

- **SolidColor(r, g, b, a)** — constant color
- **Gradient(direction, start, end)** — linear gradient
- **Noise(seed, grayscale)** — random noise
- **TextureLookup(path)** — sample from an image file

## Game of Life

```python
from pixel_python.game_of_life import ConwayLife
from pixel_python.program import ProgramRunner
from pixel_python.canvas import PixelCanvas

canvas = PixelCanvas(64, 64, use_gpu=False)
# Set up initial state
canvas.set(10, 10, 255, 255, 255)
canvas.set(11, 10, 255, 255, 255)
canvas.set(12, 10, 255, 255, 255)

runner = ProgramRunner(canvas, ConwayLife(), frames=10, save_every=1)
paths = runner.run(output_dir="/tmp/life/")
```

## Architecture

- `PixelCanvas` — GPU/CPU buffer with per-pixel get/set, kernels, neighbors, step(), save()
- `PixelProgram` — ABC for per-pixel computations
- `CompositeProgram` — layer multiple programs with blend modes
- `ProgramRunner` — executes programs over frames with callbacks and auto-save
- `Uniforms` — time, frame, resolution, and custom variables for programs
- `@pixel_program` — decorator to define programs from plain functions
