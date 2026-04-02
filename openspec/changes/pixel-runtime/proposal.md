# Proposal: Pixel Runtime Core

## Why

We need a GPU-backed pixel substrate — a 2D texture that programs read and write as their primary state. This is the foundation for pixel-based programming where computation IS visual state. Without it, there's no canvas to paint on.

## Problem

- No GPU texture allocation in Python that's simple enough for an LLM agent to drive
- cupy/numpy are array libraries, not pixel execution runtimes
- We need spatial semantics: cells, neighborhoods, kernels — not just matrix ops
- Visual output must be immediate and verifiable (save frame to PNG)

## Solution

Build a `PixelCanvas` class that:
1. Allocates a 2D GPU texture via cupy (falls back to numpy if no GPU)
2. Provides per-pixel read/write with RGBA packing
3. Supports spatial operations: flood fill, kernel convolution, neighbor queries
4. Can save frames to PNG for visual verification
5. Supports a simple execution loop: `canvas.step(fn)` where `fn(canvas, x, y) -> RGBA`

## Success Criteria

- [ ] `PixelCanvas` class in `pixel_python/canvas.py`
- [ ] GPU allocation with CPU fallback
- [ ] Per-pixel get/set with RGBA
- [ ] Spatial operations (neighbors, fill, kernel)
- [ ] Frame export to PNG
- [ ] Execution loop with step function
