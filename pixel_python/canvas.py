"""PixelCanvas — a 2D RGBA pixel buffer backed by cupy (GPU) or numpy (CPU)."""

from __future__ import annotations

import numpy as np

try:
    import cupy as cp

    _CUPY_AVAILABLE = True
except ImportError:
    cp = None  # type: ignore[assignment]
    _CUPY_AVAILABLE = False


def _positive_int(value: object, name: str) -> int:
    """Coerce *value* to a positive int or raise."""
    try:
        v = int(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}") from exc
    if v <= 0:
        raise ValueError(f"{name} must be > 0, got {v}")
    return v


def _clamp(v: int) -> int:
    """Clamp *v* to the range 0-255."""
    return int(max(0, min(255, v)))


def _pack_rgba(r: int, g: int, b: int, a: int) -> int:
    """Pack four channels into a single uint32 as ``(R<<24 | G<<16 | B<<8 | A)``."""
    return (_clamp(r) << 24) | (_clamp(g) << 16) | (_clamp(b) << 8) | _clamp(a)


def _unpack_rgba(value: int) -> tuple[int, int, int, int]:
    """Unpack a uint32 into ``(R, G, B, A)``."""
    r = (value >> 24) & 0xFF
    g = (value >> 16) & 0xFF
    b = (value >> 8) & 0xFF
    a = value & 0xFF
    return (r, g, b, a)


class PixelCanvas:
    """2-D pixel canvas stored as a uint32 array (packed RGBA).

    Parameters
    ----------
    width : int
        Number of columns (must be > 0).
    height : int
        Number of rows (must be > 0).
    use_gpu : bool
        If *True* (default), try to allocate on GPU via cupy.  Falls back
        to numpy when cupy is unavailable.
    """

    __slots__ = (
        "_width",
        "_height",
        "_is_gpu",
        "_buffer",
    )

    def __init__(self, width: int, height: int, *, use_gpu: bool = True) -> None:
        self._width: int = _positive_int(width, "width")
        self._height: int = _positive_int(height, "height")

        if use_gpu and _CUPY_AVAILABLE and cp is not None:
            self._buffer = cp.zeros((self._height, self._width), dtype=np.uint32)
            self._is_gpu: bool = True
        else:
            self._buffer = np.zeros((self._height, self._width), dtype=np.uint32)
            self._is_gpu = False

    # -- read-only properties ------------------------------------------------

    @property
    def width(self) -> int:
        """Canvas width in pixels (columns)."""
        return self._width

    @property
    def height(self) -> int:
        """Canvas height in pixels (rows)."""
        return self._height

    @property
    def shape(self) -> tuple[int, int]:
        """Buffer shape as ``(height, width)``."""
        return (self._height, self._width)

    @property
    def is_gpu(self) -> bool:
        """``True`` when the backing array lives on the GPU."""
        return self._is_gpu

    @property
    def buffer(self):  # noqa: ANN201 — returns ndarray | cp.ndarray
        """The underlying uint32 buffer (read-only from outside)."""
        return self._buffer

    @property
    def device(self) -> str:
        """Human-readable device name."""
        if self._is_gpu:
            return "gpu"
        return "cpu"

    # -- pixel read / write ---------------------------------------------------

    def get(self, x: int, y: int) -> tuple[int, int, int, int]:
        """Return the RGBA values at ``(x, y)`` as a 4-tuple of ints 0-255.

        Raises ``IndexError`` when the coordinates are outside the canvas.
        """
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            raise IndexError(
                f"({x}, {y}) out of bounds for canvas "
                f"({self._width}x{self._height})"
            )
        value = int(self._buffer[y, x])
        return _unpack_rgba(value)

    def set(self, x: int, y: int, r: int, g: int, b: int, a: int = 255) -> None:
        """Pack ``(r, g, b, a)`` into a single uint32 and write at ``(x, y)``.

        Channels are clamped to 0-255.  Raises ``IndexError`` when the
        coordinates are outside the canvas.
        """
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            raise IndexError(
                f"({x}, {y}) out of bounds for canvas "
                f"({self._width}x{self._height})"
            )
        self._buffer[y, x] = np.uint32(int(_pack_rgba(r, g, b, a)))

    def fill(self, r: int, g: int, b: int, a: int = 255) -> None:
        """Fill every pixel with the same RGBA colour."""
        packed = int(_pack_rgba(r, g, b, a))
        self._buffer.fill(np.uint32(packed))

    def neighbors(
        self, x: int, y: int, radius: int = 1
    ) -> list[tuple[int, int, tuple[int, int, int, int]]]:
        """Return neighbours within *radius* manhattan distance of ``(x, y)``.

        Each element in the returned list is ``(nx, ny, (r, g, b, a))``.
        The center cell ``(x, y)`` is **excluded**.  Coordinates that would
        fall outside the canvas are silently clamped (and de-duplicated).

        Raises ``IndexError`` if ``(x, y)`` is out of bounds.
        Raises ``ValueError`` if *radius* < 1.
        """
        if radius < 1:
            raise ValueError(f"radius must be >= 1, got {radius}")
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            raise IndexError(
                f"({x}, {y}) out of bounds for canvas "
                f"({self._width}x{self._height})"
            )

        seen: set[tuple[int, int]] = set()
        result: list[tuple[int, int, tuple[int, int, int, int]]] = []

        for dy in range(-radius, radius + 1):
            remaining = radius - abs(dy)
            for dx in range(-remaining, remaining + 1):
                nx = x + dx
                ny = y + dy
                # Clamp to canvas bounds
                if nx < 0 or nx >= self._width or ny < 0 or ny >= self._height:
                    continue
                if (nx, ny) == (x, y):
                    continue
                if (nx, ny) in seen:
                    continue
                seen.add((nx, ny))
                result.append((nx, ny, self.get(nx, ny)))

        return result

    # -- spatial operations ---------------------------------------------------

    def apply_kernel(self, kernel: list[list[int | float]]) -> None:
        """Convolve *kernel* over the canvas in-place.

        The kernel must be a non-empty, square, odd-sized list-of-lists of
        numbers.  Out-of-bounds pixels are treated as ``(0, 0, 0, 0)``
        (zero-padding).  The weighted sum of each channel is normalized by
        the sum of absolute kernel weights, then clamped to ``[0, 255]``.

        Raises
        ------
        TypeError
            If *kernel* is not a ``list`` or contains non-numeric elements.
        ValueError
            If *kernel* is empty, ragged, non-square, or has even dimension.
        """
        # --- validation ------------------------------------------------------
        if not isinstance(kernel, list):
            raise TypeError("kernel must be a list")
        if len(kernel) == 0:
            raise ValueError("kernel must not be empty")
        if not all(isinstance(row, list) for row in kernel):
            raise TypeError("kernel rows must be lists")
        row_len = len(kernel[0])
        for row in kernel:
            if len(row) != row_len:
                raise ValueError("kernel must be rectangular")
        # Check numeric before square so non-numeric kernels are caught first
        for row in kernel:
            for val in row:
                if not isinstance(val, (int, float)):
                    raise TypeError("kernel elements must be numeric")
        if row_len != len(kernel):
            raise ValueError("kernel must be square")
        if row_len % 2 == 0:
            raise ValueError("kernel dimension must be odd")

        # --- prepare ---------------------------------------------------------
        karr = np.array(kernel, dtype=np.float64)
        size = karr.shape[0]
        half = size // 2
        norm = float(np.abs(karr).sum())
        if norm == 0:
            return  # all-zero kernel → no change

        src = self._buffer.copy()  # read from original
        h, w = self._height, self._width

        # --- convolve --------------------------------------------------------
        for y in range(h):
            for x in range(w):
                sums = [0.0, 0.0, 0.0, 0.0]
                for ky in range(size):
                    sy = y + ky - half
                    for kx in range(size):
                        sx = x + kx - half
                        weight = karr[ky, kx]
                        if weight == 0:
                            continue
                        if 0 <= sx < w and 0 <= sy < h:
                            pixel = int(src[sy, sx])
                            sums[0] += weight * ((pixel >> 24) & 0xFF)
                            sums[1] += weight * ((pixel >> 16) & 0xFF)
                            sums[2] += weight * ((pixel >> 8) & 0xFF)
                            sums[3] += weight * (pixel & 0xFF)
                        # else: zero-padding → contribution is 0

                self._buffer[y, x] = np.uint32(
                    _pack_rgba(
                        _clamp(int(sums[0] / norm)),
                        _clamp(int(sums[1] / norm)),
                        _clamp(int(sums[2] / norm)),
                        _clamp(int(sums[3] / norm)),
                    )
                )

    # -- execution loop -------------------------------------------------------

    def step(
        self,
        fn: "callable[[PixelCanvas, int, int], tuple[int, int, int, int]]",  # noqa: F821
    ) -> "PixelCanvas":
        """Evaluate *fn* at every pixel and swap in the results.

        *fn(canvas, x, y)* must return an ``(r, g, b, a)`` tuple.  A
        fresh double-buffer is allocated, populated from the return
        values, then replaces ``self._buffer`` atomically so that
        every pixel sees the same input state.

        Returns ``self`` for chaining.
        """
        xp = cp if (self._is_gpu and cp is not None) else np
        new_buf = xp.empty_like(self._buffer)
        for y in range(self._height):
            for x in range(self._width):
                r, g, b, a = fn(self, x, y)
                new_buf[y, x] = xp.uint32(int(_pack_rgba(r, g, b, a)))
        self._buffer = new_buf
        return self

    # -- output ---------------------------------------------------------------

    def save(self, path: str) -> str:
        """Export the canvas to a PNG file.

        Creates parent directories automatically.  Returns the absolute
        path of the written file.
        """
        from pathlib import Path

        try:
            from PIL import Image
        except ImportError as exc:
            raise ImportError(
                "Pillow is required for PNG export: pip install Pillow"
            ) from exc

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        # Move to CPU if needed, unpack RGBA → (H, W, 4) uint8
        buf = self._buffer
        if self._is_gpu and cp is not None:
            buf = cp.asnumpy(buf)
        arr = np.zeros((self._height, self._width, 4), dtype=np.uint8)
        raw = np.asarray(buf)
        arr[:, :, 0] = (raw >> 24) & 0xFF  # R
        arr[:, :, 1] = (raw >> 16) & 0xFF  # G
        arr[:, :, 2] = (raw >> 8) & 0xFF   # B
        arr[:, :, 3] = raw & 0xFF           # A

        img = Image.fromarray(arr, mode="RGBA")
        img.save(str(p))
        return str(p.resolve())

    def save_frame(self, directory: str, frame_number: int) -> str:
        """Save frame with zero-padded filename.

        ``save_frame("output/", 42)`` writes ``output/frame_000042.png``.
        Returns the absolute path.
        """
        from pathlib import Path

        d = Path(directory)
        d.mkdir(parents=True, exist_ok=True)
        filename = f"frame_{frame_number:06d}.png"
        return self.save(str(d / filename))

    # -- dunder helpers -------------------------------------------------------

    def __repr__(self) -> str:
        backend = "gpu" if self._is_gpu else "cpu"
        return f"PixelCanvas(width={self._width}, height={self._height}, device={backend})"
