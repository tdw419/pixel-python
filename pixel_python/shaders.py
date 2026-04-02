"""Library of basic shader-like pixel programs."""

from __future__ import annotations

import random
from typing import Optional

import numpy as np

from .program import PixelProgram


RGBA = tuple[int, int, int, int]


class SolidColor(PixelProgram):
    """Returns a constant color for every pixel."""

    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.color = (r, g, b, a)

    def update(self, canvas, x: int, y: int) -> RGBA:
        return self.color


class Gradient(PixelProgram):
    """Linear color gradient across the canvas."""

    def __init__(
        self,
        direction: str = "horizontal",
        start_color: RGBA = (0, 0, 0, 255),
        end_color: RGBA = (255, 255, 255, 255),
    ):
        if direction not in ("horizontal", "vertical"):
            raise ValueError(f"direction must be 'horizontal' or 'vertical', got {direction!r}")
        self.direction = direction
        self.start_color = start_color
        self.end_color = end_color

    @staticmethod
    def _lerp(a: int, b: int, t: float) -> int:
        return int(a + (b - a) * t)

    def update(self, canvas, x: int, y: int) -> RGBA:
        if self.direction == "horizontal":
            t = x / max(canvas.width - 1, 1)
        else:
            t = y / max(canvas.height - 1, 1)
        return tuple(
            self._lerp(s, e, t) for s, e in zip(self.start_color, self.end_color)
        )


class Noise(PixelProgram):
    """Per-pixel random noise, optionally seeded for reproducibility."""

    def __init__(self, seed: Optional[int] = None, grayscale: bool = True):
        self._rng = random.Random(seed)
        self.grayscale = grayscale

    def update(self, canvas, x: int, y: int) -> RGBA:
        if self.grayscale:
            v = self._rng.randint(0, 255)
            return (v, v, v, 255)
        return (
            self._rng.randint(0, 255),
            self._rng.randint(0, 255),
            self._rng.randint(0, 255),
            255,
        )


class TextureLookup(PixelProgram):
    """Load an image and sample it pixel-by-pixel onto the canvas."""

    def __init__(self, texture_path: str):
        try:
            from PIL import Image
        except ImportError as exc:
            raise ImportError("Pillow required for TextureLookup: pip install Pillow") from exc
        self.image = Image.open(texture_path).convert("RGBA")
        self.img_w, self.img_h = self.image.size
        self._pixels = self.image.load()

    def update(self, canvas, x: int, y: int) -> RGBA:
        # Map canvas coords to texture coords
        tx = int(x * (self.img_w - 1) / max(canvas.width - 1, 1))
        ty = int(y * (self.img_h - 1) / max(canvas.height - 1, 1))
        r, g, b, a = self._pixels[tx, ty]
        return (r, g, b, a)
