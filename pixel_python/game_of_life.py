"""Conway's Game of Life as a PixelProgram."""

from __future__ import annotations

from .program import PixelProgram


class ConwayLife(PixelProgram):
    """Canonical Conway's Game of Life cellular automaton.

    A cell is "alive" if its brightness (mean of RGB) exceeds *threshold*.
    Standard rules:
        - Alive cell with 2 or 3 live neighbors survives.
        - Dead cell with exactly 3 live neighbors becomes alive.
        - All other cells die.

    Living cells render white (255,255,255,255); dead cells black (0,0,0,255).
    """

    def __init__(self, threshold: float = 63.75):
        """threshold: brightness threshold (0-255) for considering a cell alive.
        Default 63.75 (= 255 * 0.25) means a pixel with average >63.75 is alive.
        """
        self.threshold = threshold

    def _is_alive(self, canvas, x: int, y: int) -> bool:
        r, g, b, _ = canvas.get(x, y)
        return (r + g + b) / 3.0 > self.threshold

    def _count_neighbors(self, canvas, x: int, y: int) -> int:
        count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                    if self._is_alive(canvas, nx, ny):
                        count += 1
        return count

    def update(self, canvas, x: int, y: int) -> tuple[int, int, int, int]:
        alive = self._is_alive(canvas, x, y)
        n = self._count_neighbors(canvas, x, y)

        if alive and n in (2, 3):
            return (255, 255, 255, 255)
        elif not alive and n == 3:
            return (255, 255, 255, 255)
        else:
            return (0, 0, 0, 255)
