"""Window -- a rectangular region with a local pixel buffer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .canvas import PixelCanvas


@dataclass
class Window:
    """A rectangular region of the screen with its own pixel buffer.

    Fields
    ------
    x, y : int
        Top-left position in screen coordinates.
    width, height : int
        Dimensions in pixels (must be > 0).
    title : str
        Window title (cosmetic).
    z_order : int
        Stacking order; higher values render on top.
    visible : bool
        Whether the window should be rendered.
    focused : bool
        Whether the window currently has focus.
    """

    x: int
    y: int
    width: int
    height: int
    title: str = "Untitled"
    z_order: int = 0
    visible: bool = True
    focused: bool = False

    _buffer: Optional[PixelCanvas] = field(
        default=None, init=False, repr=False
    )

    # -- lazy buffer -----------------------------------------------------------

    @property
    def buffer(self) -> PixelCanvas:
        """Lazily create and return the window's local pixel buffer."""
        if self._buffer is None or self._buffer.width != self.width or self._buffer.height != self.height:
            old = self._buffer
            self._buffer = PixelCanvas(self.width, self.height, use_gpu=False)
            if old is not None:
                # Copy existing pixels that fit in the new buffer
                copy_h = min(old.height, self.height)
                copy_w = min(old.width, self.width)
                src = old.buffer
                dst = self._buffer.buffer
                dst[:copy_h, :copy_w] = src[:copy_h, :copy_w]
        return self._buffer

    # -- mutation --------------------------------------------------------------

    def resize(self, w: int, h: int) -> None:
        """Resize the window, recreating the buffer and preserving pixels."""
        self.width = w
        self.height = h
        # Force buffer recreation on next access
        old = self._buffer
        self._buffer = PixelCanvas(self.width, self.height, use_gpu=False)
        if old is not None:
            copy_h = min(old.height, self.height)
            copy_w = min(old.width, self.width)
            src = old.buffer
            dst = self._buffer.buffer
            dst[:copy_h, :copy_w] = src[:copy_h, :copy_w]

    def move(self, x: int, y: int) -> None:
        """Move the window to a new position."""
        self.x = x
        self.y = y
