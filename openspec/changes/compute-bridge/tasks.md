# Tasks: Compute Bridge

## SEC-1: ComputeProgram base class
- [x] Create pixel_python/compute.py
- [x] ComputeProgram ABC with setup/compute/teardown lifecycle
- [x] name property defaults to class name
- [x] Tests: instantiation, subclassing, lifecycle hooks

## SEC-2: ComputePipeline
- [x] Sequential chaining of ComputePrograms
- [x] Constructor accepts list of programs
- [x] add() method to append programs
- [x] Type checking on add (reject non-ComputeProgram)
- [x] setup/teardown propagation to all stages
- [x] Read-only programs property (returns copy)
- [x] Tests: empty pipeline, chaining, lifecycle, type safety

## SEC-3: ComputeRunner
- [x] Frame-based execution loop
- [x] Metadata injection into state["_meta"] (frame, elapsed, start_time)
- [x] on_frame callback with state and frame number
- [x] Initial state not mutated (runner makes a copy)
- [x] teardown called even on error (try/finally)
- [x] frames validation (must be >= 1)
- [x] Tests: single/multi frame, callbacks, error handling, pipeline integration

## SEC-4: @compute_program decorator
- [x] Wraps function into ComputeProgram subclass
- [x] Preserves __name__, __qualname__, __doc__
- [x] Supports kwargs at construction
- [x] Works in ComputePipeline and ComputeRunner
- [x] Tests: decorator, naming, docs, pipeline integration

## SEC-5: Module exports and integration
- [x] Update __init__.py with all compute exports
- [x] All 153 tests pass (119 existing + 34 new)
- [x] No breaking changes to existing pixel API
