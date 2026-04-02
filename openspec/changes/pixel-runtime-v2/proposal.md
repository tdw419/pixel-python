# Proposal: Pixel Programming Interface

## Why

The `PixelRuntime` is a powerful engine, but it requires writing explicit execution loops for every effect. We need a higher-level abstraction that allows developers (and AI agents) to define "Pixel Programs" (shaders) declaratively and compose them together.

## Problem

- No standard way to define a re-usable pixel-based effect.
- Complex visual states (like layering a glow over a noise pattern) require manual buffer management.
- Interfacing with external inputs (time, mouse, parameters) is currently ad-hoc.

## Solution

Introduce a `PixelProgram` abstraction that separates the *what* (the math for a single pixel) from the *how* (the execution on the canvas). 

Key features:
1. Base class for all pixel programs.
2. Built-in composition (A + B, A over B).
3. Uniform parameter support.
4. A standard `ProgramRunner` to handle temporal evolution.

## Success Criteria

- [ ] `PixelProgram` and `ProgramRunner` implemented.
- [ ] Support for composite programs (layering).
- [ ] Declarative interface (@pixel_program).
- [ ] Library of basic shaders (Noise, Gradient, etc.).
- [ ] Canonical Conway's Game of Life implementation using the new interface.
