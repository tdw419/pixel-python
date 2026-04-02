# Proposal: Compute Bridge for Arbitrary Python Pipelines

## Why

pixel-python currently only supports pixel-level computation: `update(canvas, x, y) -> RGBA`. To use pixel-python's architectural patterns (lifecycle hooks, composable pipelines, frame-based execution) for arbitrary Python code like AI agent orchestration, we need a compute layer that isn't tied to the pixel grid.

## Problem

- PixelProgram.update() must return RGBA -- can't return arbitrary data
- PixelCanvas is a uint32 buffer -- can't store dicts, strings, or complex objects
- ProgramRunner iterates every pixel -- no way to run "once per frame" logic
- AIPM v5 needs the same patterns (lifecycle, composition, frame loops) but for state dicts, not pixel buffers

## Solution

Add a `ComputeProgram` hierarchy parallel to `PixelProgram`:

1. `ComputeProgram(ABC)` -- same lifecycle (setup/compute/teardown) but `compute(state: dict) -> dict`
2. `ComputePipeline` -- sequential chaining like CompositeProgram but piping state dict through
3. `ComputeRunner` -- frame-based execution like ProgramRunner but calls compute() once per frame
4. `@compute_program` decorator -- like @pixel_program for quick one-function programs

The state dict replaces the pixel canvas. Metadata (frame, elapsed time) is injected into `state["_meta"]`.

## Success Criteria

- [x] ComputeProgram ABC in pixel_python/compute.py
- [x] ComputePipeline with sequential chaining
- [x] ComputeRunner with frame loop and metadata injection
- [x] @compute_program decorator
- [x] All existing pixel tests still pass
- [x] Test coverage for compute module (34 tests)
- [ ] Visual bridge: ComputeProgram that renders pipeline state to PixelCanvas
