"""ComputeProgram -- composable state-transformation programs.

Mirrors the PixelProgram architecture (lifecycle hooks, composition,
frame-based execution) but lifted off the pixel grid.  Instead of
``update(canvas, x, y) -> RGBA``, the contract is
``compute(state) -> state``.  The state dict is the "canvas" of
arbitrary computation.
"""

from __future__ import annotations

import time as _time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


# ── ComputeProgram ────────────────────────────────────────────────

class ComputeProgram(ABC):
    """Base class for state-transformation programs.

    Subclass this and implement ``compute()`` to define a single-step
    state transformation.  Optionally override ``setup()`` and
    ``teardown()`` for lifecycle hooks.

    The state dict is passed through each program in a pipeline.
    Programs read from it, transform it, and return the new state.
    """

    @property
    def name(self) -> str:
        """Human-readable name (defaults to class name)."""
        return self.__class__.__name__

    @abstractmethod
    def compute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Transform state and return the new state dict.

        Parameters
        ----------
        state : dict
            The current pipeline state.  Read what you need, modify
            and return it (or return a new dict).

        Returns
        -------
        dict
            The updated state, passed to the next program.
        """
        ...

    def setup(self, state: dict[str, Any]) -> None:
        """Called once before the first frame. Default: no-op."""
        pass

    def teardown(self, state: dict[str, Any]) -> None:
        """Called once after the last frame. Default: no-op."""
        pass


# ── ComputePipeline (like CompositeProgram but for state) ─────────

class ComputePipeline(ComputeProgram):
    """Chain multiple ComputePrograms into a sequential pipeline.

    Each program receives the output state of the previous one.
    Execution order is the order they were added.

    Example::

        pipe = ComputePipeline([
            LoadSpec(),
            SelectModel(),
            RunAgent(),
            DetectOutcome(),
        ])
    """

    def __init__(
        self,
        programs: Optional[list[ComputeProgram]] = None,
    ) -> None:
        self._programs: list[ComputeProgram] = list(programs or [])

    def add(self, program: ComputeProgram) -> None:
        """Append a program to the pipeline."""
        if not isinstance(program, ComputeProgram):
            raise TypeError(
                f"expected ComputeProgram, got {type(program).__name__}"
            )
        self._programs.append(program)

    def compute(self, state: dict[str, Any]) -> dict[str, Any]:
        for prog in self._programs:
            state = prog.compute(state)
        return state

    def setup(self, state: dict[str, Any]) -> None:
        for prog in self._programs:
            prog.setup(state)

    def teardown(self, state: dict[str, Any]) -> None:
        for prog in self._programs:
            prog.teardown(state)

    @property
    def programs(self) -> list[ComputeProgram]:
        """Read-only view of the pipeline stages."""
        return list(self._programs)


# ── ComputeRunner (like ProgramRunner but for state) ──────────────

OnComputeFrameFn = Callable  # (state, frame_number) -> None


class ComputeRunner:
    """Execute a ComputeProgram (or ComputePipeline) over multiple frames.

    Each frame calls ``program.compute(state)`` once, then increments
    the frame counter.  Lifecycle hooks (setup/teardown) are called
    automatically.

    Example::

        runner = ComputeRunner(my_pipeline, frames=10)
        final_state = runner.run({"project": "my-app"})
    """

    def __init__(
        self,
        program: ComputeProgram,
        *,
        frames: int = 1,
        on_frame: Optional[OnComputeFrameFn] = None,
    ) -> None:
        if frames < 1:
            raise ValueError(f"frames must be >= 1, got {frames}")
        self.program = program
        self.frames = frames
        self.on_frame = on_frame
        self.state: dict[str, Any] = {}

    def run(
        self,
        initial_state: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Run all frames and return the final state.

        Parameters
        ----------
        initial_state : dict, optional
            Starting state.  Defaults to empty dict.

        Returns
        -------
        dict
            The state after the last frame.
        """
        self.state = dict(initial_state or {})
        start_time = _time.monotonic()

        # Inject built-in metadata
        self.state.setdefault("_meta", {})
        self.state["_meta"]["start_time"] = start_time

        try:
            self.program.setup(self.state)

            for frame_num in range(1, self.frames + 1):
                self.state["_meta"]["frame"] = frame_num
                self.state["_meta"]["elapsed"] = _time.monotonic() - start_time

                self.state = self.program.compute(self.state)

                if self.on_frame is not None:
                    self.on_frame(self.state, frame_num)

        finally:
            self.program.teardown(self.state)

        return self.state


# ── @compute_program decorator (like @pixel_program) ─────────────

def compute_program(fn: Callable) -> type[ComputeProgram]:
    """Decorator that wraps a function into a ComputeProgram subclass.

    Usage::

        @compute_program
        def add_counter(state):
            state["counter"] = state.get("counter", 0) + 1
            return state

        prog = add_counter()
        prog.compute({"counter": 0})  # -> {"counter": 1}

    The decorated function becomes a class.  Instantiating it creates
    a ComputeProgram that delegates ``compute()`` to the original
    function.
    """

    class WrappedProgram(ComputeProgram):
        def __init__(self, **kwargs: Any):
            self._extra = kwargs

        def compute(self, state: dict[str, Any]) -> dict[str, Any]:
            return fn(state)

    WrappedProgram.__name__ = fn.__name__
    WrappedProgram.__qualname__ = fn.__qualname__
    WrappedProgram.__doc__ = fn.__doc__
    return WrappedProgram
