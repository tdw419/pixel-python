"""PixelProgram — composable pixel-level programs for PixelCanvas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional


RGBA = tuple[int, int, int, int]


class PixelProgram(ABC):
    """Base class for all pixel programs.

    Subclass this and implement ``update()`` to define a per-pixel
    computation.  Optionally override ``setup()`` and ``teardown()``
    for lifecycle hooks.
    """

    @property
    def name(self) -> str:
        """Human-readable name (defaults to class name)."""
        return self.__class__.__name__

    @abstractmethod
    def update(self, canvas, x: int, y: int) -> RGBA:
        """Compute the RGBA value for pixel (x, y).

        Parameters
        ----------
        canvas : PixelCanvas
            The canvas being processed (read-only during update).
        x, y : int
            Pixel coordinates.

        Returns
        -------
        tuple[int, int, int, int]
            (r, g, b, a) values, each 0-255.
        """
        ...

    def setup(self, canvas) -> None:
        """Called once before the first frame. Default: no-op."""
        pass

    def teardown(self, canvas) -> None:
        """Called once after the last frame. Default: no-op."""
        pass


# ── Blend helpers ────────────────────────────────────────────────

def _blend_normal(src: RGBA, dst: RGBA) -> RGBA:
    return src

def _blend_add(src: RGBA, dst: RGBA) -> RGBA:
    return tuple(min(255, s + d) for s, d in zip(src, dst))

def _blend_multiply(src: RGBA, dst: RGBA) -> RGBA:
    return tuple(s * d // 255 for s, d in zip(src, dst))

def _blend_alpha(src: RGBA, dst: RGBA) -> RGBA:
    sa = src[3] / 255.0
    da = 1.0 - sa
    return (
        int(src[0] * sa + dst[0] * da),
        int(src[1] * sa + dst[1] * da),
        int(src[2] * sa + dst[2] * da),
        max(src[3], dst[3]),
    )

_BLEND_MODES = {
    "normal": _blend_normal,
    "add": _blend_add,
    "multiply": _blend_multiply,
    "alpha": _blend_alpha,
}


class CompositeProgram(PixelProgram):
    """Combine multiple programs with layer-based composition.

    Programs are executed in order; each result is blended onto the
    accumulated output using the specified blend mode.

    Example::

        comp = CompositeProgram()
        comp.add(my_gradient(), "normal")
        comp.add(my_noise(), "alpha")
    """

    def __init__(
        self,
        programs: Optional[list[tuple[PixelProgram, str]]] = None,
    ) -> None:
        self._layers: list[tuple[PixelProgram, str]] = list(programs or [])

    def add(self, program: PixelProgram, blend_mode: str = "normal") -> None:
        """Append a program layer.

        Parameters
        ----------
        program : PixelProgram
            The program to add.
        blend_mode : str
            One of "normal", "add", "multiply", "alpha".
        """
        if blend_mode not in _BLEND_MODES:
            raise ValueError(
                f"unknown blend mode {blend_mode!r}; "
                f"choose from {sorted(_BLEND_MODES)}"
            )
        self._layers.append((program, blend_mode))

    def update(self, canvas, x: int, y: int) -> RGBA:
        result: RGBA = (0, 0, 0, 0)
        for prog, mode in self._layers:
            layer = prog.update(canvas, x, y)
            blend_fn = _BLEND_MODES[mode]
            result = blend_fn(layer, result)
        return result

    def setup(self, canvas) -> None:
        for prog, _ in self._layers:
            prog.setup(canvas)

    def teardown(self, canvas) -> None:
        for prog, _ in self._layers:
            prog.teardown(canvas)


# ── ProgramRunner ────────────────────────────────────────────────

OnFrameFn = Callable  # (canvas, frame_number) -> None


class ProgramRunner:
    """Execute a PixelProgram on a PixelCanvas over multiple frames.

    Example::

        runner = ProgramRunner(canvas, my_program, frames=60, save_every=10)
        paths = runner.run("/tmp/output/")
    """

    def __init__(
        self,
        canvas,
        program: PixelProgram,
        *,
        frames: int = 1,
        on_frame: Optional[OnFrameFn] = None,
        save_every: int = 0,
    ) -> None:
        if frames < 1:
            raise ValueError(f"frames must be >= 1, got {frames}")
        self.canvas = canvas
        self.program = program
        self.frames = frames
        self.on_frame = on_frame
        self.save_every = save_every
        self.frame_paths: list[str] = []

    def run(self, output_dir: Optional[str] = None) -> list[str]:
        """Run all frames.

        Parameters
        ----------
        output_dir : str, optional
            If provided with save_every > 0, frames are auto-saved here.

        Returns
        -------
        list[str]
            Paths to saved frames (empty if no auto-save).
        """
        self.frame_paths = []

        try:
            self.program.setup(self.canvas)

            for frame_num in range(1, self.frames + 1):
                # Execute one frame: step() calls program.update for every pixel
                self.canvas.step(self.program.update)

                if self.on_frame is not None:
                    self.on_frame(self.canvas, frame_num)

                if self.save_every > 0 and output_dir and frame_num % self.save_every == 0:
                    path = self.canvas.save_frame(output_dir, frame_num)
                    self.frame_paths.append(path)

        finally:
            self.program.teardown(self.canvas)

        return self.frame_paths
