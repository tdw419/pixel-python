"""Declarative DSL for defining pixel programs without subclassing."""

from __future__ import annotations

import time as _time
from typing import Any, Callable, Optional

from .program import PixelProgram, ProgramRunner


RGBA = tuple[int, int, int, int]


# ── Uniforms ─────────────────────────────────────────────────────

class Uniforms:
    """Dict-like container for uniform variables passed to programs.

    Built-in uniforms (set automatically by ProgramRunner):
        time        — float, seconds since run started
        frame       — int, current frame number (1-based)
        resolution  — (width, height) of the canvas

    Custom uniforms are set via constructor kwargs or .set().
    """

    def __init__(self, **kwargs: Any) -> None:
        self._data: dict[str, Any] = dict(kwargs)
        # Built-ins — populated by ProgramRunner
        self._builtins: dict[str, Any] = {
            "time": 0.0,
            "frame": 0,
            "resolution": (0, 0),
        }

    def __getitem__(self, key: str) -> Any:
        if key in self._builtins:
            return self._builtins[key]
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._builtins or key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, key: str, value: Any) -> None:
        if key in ("time", "frame", "resolution"):
            self._builtins[key] = value
        else:
            self._data[key] = value

    def update_builtins(self, **kwargs: Any) -> None:
        """Update built-in uniforms (called by ProgramRunner)."""
        self._builtins.update(kwargs)

    def update(self, **kwargs: Any) -> None:
        """Update custom uniforms."""
        self._data.update(kwargs)

    def keys(self) -> set[str]:
        return set(self._builtins.keys()) | set(self._data.keys())

    def __repr__(self) -> str:
        items = {**self._builtins, **self._data}
        return f"Uniforms({items})"


# ── @pixel_program decorator ────────────────────────────────────

def pixel_program(fn: Callable) -> type[PixelProgram]:
    """Decorator that wraps a function into a PixelProgram subclass.

    Usage::

        @pixel_program
        def red(canvas, x, y):
            return (255, 0, 0, 255)

        prog = red()
        prog.update(canvas, 0, 0)  # -> (255, 0, 0, 255)

    The decorated function becomes a class. Instantiating it creates a
    PixelProgram that delegates ``update()`` to the original function.
    Supports optional ``uniforms`` kwarg at construction.
    """

    class WrappedProgram(PixelProgram):
        def __init__(self, uniforms: Optional[Uniforms] = None, **kwargs: Any):
            self.uniforms = uniforms or Uniforms()
            self._extra = kwargs

        def update(self, canvas, x: int, y: int) -> RGBA:
            return fn(canvas, x, y, self.uniforms) if fn.__code__.co_argcount >= 4 else fn(canvas, x, y)

    WrappedProgram.__name__ = fn.__name__
    WrappedProgram.__qualname__ = fn.__qualname__
    WrappedProgram.__doc__ = fn.__doc__
    return WrappedProgram


# ── Enhanced ProgramRunner with uniform support ──────────────────

class DSLProgramRunner(ProgramRunner):
    """ProgramRunner that injects uniforms into programs each frame."""

    def __init__(self, canvas, program, *, frames: int = 1,
                 on_frame=None, save_every: int = 0,
                 uniforms: Optional[Uniforms] = None):
        super().__init__(canvas, program, frames=frames,
                         on_frame=on_frame, save_every=save_every)
        self.uniforms = uniforms or Uniforms()
        self._start_time: float = 0.0

    def run(self, output_dir: Optional[str] = None) -> list[str]:
        self._start_time = _time.monotonic()
        self.frame_paths = []

        # Inject uniforms into program if it supports them
        if hasattr(self.program, 'uniforms'):
            self.program.uniforms = self.uniforms

        try:
            self.program.setup(self.canvas)

            for frame_num in range(1, self.frames + 1):
                # Update built-in uniforms
                self.uniforms.update_builtins(
                    time=_time.monotonic() - self._start_time,
                    frame=frame_num,
                    resolution=(self.canvas.width, self.canvas.height),
                )

                self.canvas.step(self.program.update)

                if self.on_frame is not None:
                    self.on_frame(self.canvas, frame_num)

                if self.save_every > 0 and output_dir and frame_num % self.save_every == 0:
                    path = self.canvas.save_frame(output_dir, frame_num)
                    self.frame_paths.append(path)

        finally:
            self.program.teardown(self.canvas)

        return self.frame_paths
