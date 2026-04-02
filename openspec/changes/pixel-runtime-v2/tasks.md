# Tasks: Pixel Programming Interface

## 1. Program Definition
- [x] 1.1 Define a `PixelProgram` base class in `pixel_python/program.py`. It should have an `update(canvas, x, y)` method that returns an RGBA tuple.
- [x] 1.2 Implement a `CompositeProgram` that allows combining multiple programs (e.g., layer-based composition).
- [x] 1.3 Add a `ProgramRunner` that manages the execution of a `PixelProgram` on a `PixelCanvas` over multiple frames, with an optional `on_frame` callback.

## 2. Declarative Interface
- [x] 2.1 Create a DSL or decorator-based interface for defining simple pixel programs without subclassing (e.g., `@pixel_program`).
- [x] 2.2 Support passing uniform variables to programs (e.g., time, mouse position, custom parameters).

## 3. Library of Basic Programs
- [x] 3.1 Implement a set of basic "shader-like" programs: `SolidColor`, `Gradient`, `Noise`, `TextureLookup`.
- [x] 3.2 Implement a `ConwayLife` program as a canonical example of a stateful cellular automaton using the new interface.

## 4. Documentation and Examples
- [x] 4.1 Write a README.md explaining how to use the new programming interface.
- [x] 4.2 Provide an example script `examples/lava_lamp.py` that uses the composite interface to create a complex visual effect.
