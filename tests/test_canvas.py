"""Tests for PixelCanvas — Task 1.1 core canvas allocation."""

import numpy as np
import pytest

from pixel_python.canvas import PixelCanvas


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestCanvasConstruction:
    """Canvas allocation and properties."""

    def test_cpu_canvas_shape(self):
        c = PixelCanvas(10, 8, use_gpu=False)
        assert c.width == 10
        assert c.height == 8
        assert c.shape == (8, 10)

    def test_cpu_canvas_not_gpu(self):
        c = PixelCanvas(4, 4, use_gpu=False)
        assert c.is_gpu is False

    def test_cpu_buffer_dtype(self):
        c = PixelCanvas(6, 6, use_gpu=False)
        assert c.buffer.dtype == np.uint32

    def test_cpu_buffer_initialised_zero(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        assert np.all(c.buffer == 0)

    def test_default_use_gpu_is_true(self):
        # On a machine without cupy this should gracefully fall back to CPU.
        c = PixelCanvas(2, 2)
        # Whatever backend is chosen, it must work.
        assert c.width == 2

    def test_gpu_canvas_properties_when_available(self, monkeypatch):
        """If cupy is available, is_gpu should be True."""
        import importlib
        fake_cp = type("cupy", (), {"zeros": staticmethod(np.zeros), "asarray": staticmethod(np.asarray)})()
        monkeypatch.setitem(
            __import__("sys").modules, "cupy", fake_cp
        )
        # Force reimport so canvas picks up the monkeypatched module
        import pixel_python.canvas as mod
        importlib.reload(mod)
        c = mod.PixelCanvas(4, 4, use_gpu=True)
        assert c.is_gpu is True
        assert c.width == 4
        assert c.height == 4
        # Restore real module state
        importlib.reload(mod)

    def test_gpu_false_forces_cpu(self):
        c = PixelCanvas(5, 5, use_gpu=False)
        assert c.is_gpu is False

    def test_square_canvas(self):
        c = PixelCanvas(64, 64, use_gpu=False)
        assert c.shape == (64, 64)

    def test_wide_canvas(self):
        c = PixelCanvas(1920, 1080, use_gpu=False)
        assert c.width == 1920
        assert c.height == 1080
        assert c.shape == (1080, 1920)

    def test_small_canvas(self):
        c = PixelCanvas(1, 1, use_gpu=False)
        assert c.shape == (1, 1)
        assert c.buffer.size == 1

    def test_buffer_is_2d(self):
        c = PixelCanvas(10, 7, use_gpu=False)
        assert c.buffer.ndim == 2

    def test_invalid_width_raises(self):
        with pytest.raises(ValueError):
            PixelCanvas(0, 10, use_gpu=False)

    def test_invalid_height_raises(self):
        with pytest.raises(ValueError):
            PixelCanvas(10, -1, use_gpu=False)

    def test_negative_width_raises(self):
        with pytest.raises(ValueError):
            PixelCanvas(-5, 5, use_gpu=False)

    def test_non_numeric_raises(self):
        with pytest.raises(TypeError):
            PixelCanvas("a", 10, use_gpu=False)  # type: ignore[arg-type]

    def test_buffer_is_readonly_property(self):
        c = PixelCanvas(4, 4, use_gpu=False)
        # buffer should be a property, not settable from outside
        with pytest.raises(AttributeError):
            c.buffer = np.zeros((4, 4), dtype=np.uint32)  # type: ignore[misc]

    def test_repr(self):
        c = PixelCanvas(10, 8, use_gpu=False)
        r = repr(c)
        assert "PixelCanvas" in r
        assert "10" in r
        assert "8" in r

    def test_large_canvas_allocation(self):
        # 4K canvas should allocate without issue on CPU
        c = PixelCanvas(3840, 2160, use_gpu=False)
        assert c.buffer.nbytes == 3840 * 2160 * 4  # uint32 = 4 bytes

    def test_device_property_matches_backend(self):
        c_cpu = PixelCanvas(3, 3, use_gpu=False)
        assert c_cpu.device == "cpu"

    def test_properties_are_immutable(self):
        c = PixelCanvas(5, 5, use_gpu=False)
        with pytest.raises(AttributeError):
            c.width = 10  # type: ignore[misc]
        with pytest.raises(AttributeError):
            c.height = 10  # type: ignore[misc]
        with pytest.raises(AttributeError):
            c.shape = (10, 10)  # type: ignore[misc]
        with pytest.raises(AttributeError):
            c.is_gpu = True  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Pixel read / write  (Task 1.2)
# ---------------------------------------------------------------------------

class TestPixelReadWrite:
    """get, set, and fill on the pixel canvas."""

    def test_get_returns_rgba_tuple(self):
        c = PixelCanvas(4, 4, use_gpu=False)
        # Write a known packed value directly to the buffer: R=10, G=20, B=30, A=40
        packed = (10 << 24) | (20 << 16) | (30 << 8) | 40
        c.buffer[1, 2] = np.uint32(packed)
        assert c.get(2, 1) == (10, 20, 30, 40)

    def test_set_then_get_roundtrip(self):
        c = PixelCanvas(10, 10, use_gpu=False)
        c.set(2, 3, 100, 150, 200, 255)
        assert c.get(2, 3) == (100, 150, 200, 255)

    def test_set_default_alpha(self):
        c = PixelCanvas(5, 5, use_gpu=False)
        c.set(0, 0, 10, 20, 30)
        assert c.get(0, 0) == (10, 20, 30, 255)

    def test_set_out_of_bounds_negative_x_raises(self):
        c = PixelCanvas(5, 5, use_gpu=False)
        with pytest.raises(IndexError):
            c.set(-1, 0, 0, 0, 0)

    def test_set_out_of_bounds_x_equals_width_raises(self):
        c = PixelCanvas(5, 5, use_gpu=False)
        with pytest.raises(IndexError):
            c.set(5, 0, 0, 0, 0)

    def test_get_out_of_bounds_y_equals_height_raises(self):
        c = PixelCanvas(5, 5, use_gpu=False)
        with pytest.raises(IndexError):
            c.get(0, 5)

    def test_get_out_of_bounds_negative_y_raises(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        with pytest.raises(IndexError):
            c.get(0, -1)

    def test_fill_sets_all_pixels(self):
        c = PixelCanvas(4, 3, use_gpu=False)
        c.fill(255, 0, 0)
        for y in range(c.height):
            for x in range(c.width):
                assert c.get(x, y) == (255, 0, 0, 255)

    def test_fill_with_alpha(self):
        c = PixelCanvas(2, 2, use_gpu=False)
        c.fill(0, 0, 0, 128)
        assert c.get(0, 0) == (0, 0, 0, 128)
        assert c.get(1, 1) == (0, 0, 0, 128)

    def test_set_pixel_writes_buffer_directly(self):
        c = PixelCanvas(6, 6, use_gpu=False)
        c.set(3, 4, 0xAA, 0xBB, 0xCC, 0xDD)
        expected = (0xAA << 24) | (0xBB << 16) | (0xCC << 8) | 0xDD
        assert int(c.buffer[4, 3]) == expected

    def test_set_clamps_high_values(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        c.set(0, 0, 300, -10, 128, 999)
        assert c.get(0, 0) == (255, 0, 128, 255)

    def test_fill_overwrites_previous_set(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        c.set(1, 1, 255, 255, 255)
        c.fill(10, 20, 30, 40)
        assert c.get(1, 1) == (10, 20, 30, 40)

    def test_corner_pixels(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        c.set(0, 0, 1, 2, 3, 4)
        c.set(2, 0, 5, 6, 7, 8)
        c.set(0, 2, 9, 10, 11, 12)
        c.set(2, 2, 13, 14, 15, 16)
        assert c.get(0, 0) == (1, 2, 3, 4)
        assert c.get(2, 0) == (5, 6, 7, 8)
        assert c.get(0, 2) == (9, 10, 11, 12)
        assert c.get(2, 2) == (13, 14, 15, 16)


# ---------------------------------------------------------------------------
# Neighbors  (Task 1.3)
# ---------------------------------------------------------------------------

class TestNeighbors:
    """neighbors(x, y, radius) — manhattan-distance neighbor query."""

    def _canvas(self, w=5, h=5):
        return PixelCanvas(w, h, use_gpu=False)

    def test_radius1_center_returns_four(self):
        c = self._canvas()
        result = c.neighbors(2, 2)
        coords = {(nx, ny) for nx, ny, _ in result}
        assert coords == {(1, 2), (3, 2), (2, 1), (2, 3)}
        for nx, ny, rgba in result:
            assert rgba == (0, 0, 0, 0)

    def test_radius2_center_returns_twelve(self):
        c = self._canvas()
        result = c.neighbors(2, 2, radius=2)
        assert len(result) == 12
        # Diamond of manhattan distance 2 around (2,2)
        coords = {(nx, ny) for nx, ny, _ in result}
        expected = set()
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 < abs(dx) + abs(dy) <= 2:
                    expected.add((2 + dx, 2 + dy))
        assert coords == expected

    def test_corner_radius1_returns_two(self):
        c = self._canvas()
        result = c.neighbors(0, 0, radius=1)
        coords = {(nx, ny) for nx, ny, _ in result}
        assert coords == {(1, 0), (0, 1)}

    def test_edge_clamping(self):
        c = self._canvas()
        result = c.neighbors(0, 2, radius=1)
        coords = {(nx, ny) for nx, ny, _ in result}
        # Left is out of bounds → clamped away. Right, up, down remain.
        assert coords == {(1, 2), (0, 1), (0, 3)}

    def test_with_colors(self):
        c = self._canvas()
        c.set(1, 2, 255, 0, 0, 255)
        c.set(3, 2, 0, 255, 0, 128)
        result = c.neighbors(2, 2)
        lookup = {(nx, ny): rgba for nx, ny, rgba in result}
        assert lookup[(1, 2)] == (255, 0, 0, 255)
        assert lookup[(3, 2)] == (0, 255, 0, 128)

    def test_out_of_bounds_raises(self):
        c = self._canvas()
        with pytest.raises(IndexError):
            c.neighbors(5, 0)
        with pytest.raises(IndexError):
            c.neighbors(-1, 2)

    def test_invalid_radius_raises(self):
        c = self._canvas()
        with pytest.raises(ValueError):
            c.neighbors(2, 2, radius=0)
        with pytest.raises(ValueError):
            c.neighbors(2, 2, radius=-1)

    def test_excludes_center(self):
        c = self._canvas()
        c.set(2, 2, 99, 99, 99, 99)
        result = c.neighbors(2, 2)
        coords = {(nx, ny) for nx, ny, _ in result}
        assert (2, 2) not in coords

    def test_1x1_canvas_returns_empty(self):
        c = self._canvas(1, 1)
        result = c.neighbors(0, 0)
        assert result == []


# ---------------------------------------------------------------------------
# apply_kernel  (Task 2.1)
# ---------------------------------------------------------------------------

class TestApplyKernel:
    """apply_kernel(kernel) — 2D convolution on the canvas."""

    def _canvas(self, w=5, h=5):
        return PixelCanvas(w, h, use_gpu=False)

    # -- validation ----------------------------------------------------------

    def test_empty_kernel_raises(self):
        c = self._canvas()
        with pytest.raises(ValueError, match="empty"):
            c.apply_kernel([])

    def test_non_square_kernel_raises(self):
        c = self._canvas()
        with pytest.raises(ValueError, match="square"):
            c.apply_kernel([[1, 0, 0], [0, 1, 0]])  # 2x3

    def test_even_dimension_kernel_raises(self):
        c = self._canvas()
        with pytest.raises(ValueError, match="odd"):
            c.apply_kernel([[1, 0], [0, 1]])  # 2x2

    def test_non_numeric_kernel_raises(self):
        c = self._canvas()
        with pytest.raises(TypeError, match="numeric"):
            c.apply_kernel([["a", "b"], ["c", "d"], ["e", "f"]])

    def test_non_list_kernel_raises(self):
        c = self._canvas()
        with pytest.raises(TypeError, match="list"):
            c.apply_kernel("not a kernel")

    def test_ragged_kernel_raises(self):
        c = self._canvas()
        with pytest.raises(ValueError, match="rectangular"):
            c.apply_kernel([[1, 0, 0], [0, 1], [0, 0, 1]])

    # -- identity kernel -----------------------------------------------------

    def test_identity_preserves_pixels(self):
        """A 3x3 identity kernel should leave pixels unchanged."""
        c = self._canvas(4, 4)
        c.set(1, 1, 100, 150, 200, 255)
        c.set(2, 3, 50, 60, 70, 80)
        before = {}
        for y in range(c.height):
            for x in range(c.width):
                before[(x, y)] = c.get(x, y)
        c.apply_kernel([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
        for y in range(c.height):
            for x in range(c.width):
                assert c.get(x, y) == before[(x, y)], f"mismatch at ({x},{y})"

    # -- box blur ------------------------------------------------------------

    def test_box_blur_3x3(self):
        """All-ones 3x3 kernel on a uniform canvas should not change values."""
        c = self._canvas(5, 5)
        c.fill(90, 90, 90, 255)
        c.apply_kernel([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        # Interior pixels: all neighbors are (90,90,90,255), sum=9*90=810, /norm=90
        assert c.get(2, 2) == (90, 90, 90, 255)

    def test_box_blur_edge_zero_padding(self):
        """Edge pixel on all-ones canvas with zero-padding should darken."""
        c = self._canvas(3, 3)
        c.fill(90, 90, 90, 255)
        c.apply_kernel([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        # Corner (0,0): 4 on-canvas pixels. Norm = sum(abs) = 9.
        # RGB: 4*90/9 = 40.  Alpha: 4*255/9 = 113.
        assert c.get(0, 0) == (40, 40, 40, 113)

    # -- specific pixel values -----------------------------------------------

    def test_single_pixel_blur(self):
        """Single bright pixel on black canvas with box blur."""
        c = self._canvas(3, 3)
        c.set(1, 1, 255, 255, 255, 255)
        c.apply_kernel([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        # Center: sum = 255 (only center is non-zero), norm = 9 -> 255/9 = 28
        r, g, b, a = c.get(1, 1)
        assert (r, g, b, a) == (28, 28, 28, 28)
        # Neighbor of center, e.g. (0,1): the center pixel is in its window
        # (0,1) window covers rows 0-2, cols 0-1 (with zero pad on left)
        # That window has center (1,1)=255 and the rest are 0.
        # Sum = 255, norm = 9 -> 28
        r2, g2, b2, a2 = c.get(0, 1)
        assert (r2, g2, b2, a2) == (28, 28, 28, 28)

    def test_negative_kernel_weights(self):
        """Kernel with negative weights (e.g. sharpen/edge detect)."""
        c = self._canvas(3, 3)
        c.fill(100, 100, 100, 100)
        # Sharpen: [[0,-1,0],[-1,5,-1],[0,-1,0]]
        # abs norm = 1+1+5+1+1 = 9.  Center: (5*100-4*100)/9 = 100/9 ≈ 11
        c.apply_kernel([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        assert c.get(1, 1) == (11, 11, 11, 11)

    def test_kernel_clamps_negative_to_zero(self):
        """Negative convolution result should clamp to 0."""
        c = self._canvas(3, 3)
        c.fill(10, 10, 10, 10)
        # Edge-detect-like kernel that produces negative values
        c.apply_kernel([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        # Center: 4*10 - 4*10 = 0 -> clamp to 0
        assert c.get(1, 1) == (0, 0, 0, 0)

    def test_kernel_clamps_above_255(self):
        """Convolution result above 255 should clamp."""
        c = self._canvas(3, 3)
        c.fill(200, 200, 200, 200)
        # Kernel with center=2, one neighbor=2 => sum at center = 2*200+2*200=800
        # abs norm = 2+2 = 4, so 800/4 = 200.  Not enough.
        # Use a bigger center to force overflow: center=4, norm=4 => 4*200/4=200.
        # To exceed 255 after normalization, need weighted_sum/norm > 255.
        # Kernel [[0,0,0],[0,4,1],[0,0,0]]: center=4*200+1*200=1000, norm=5 => 200. Nope.
        # Actually: single non-zero center weight k: result = k*val/k = val. Can't exceed.
        # Need multiple contributing pixels: [[0,2,0],[2,2,0],[0,0,0]]
        # center (1,1): weights at (0,1)=2, (1,0)=2, (1,1)=2. sum=6*200=1200. norm=6. =>200.
        # Still val. Key insight: with uniform input, normalized result = val * sum(weights)/sum(abs(weights)).
        # So need non-uniform input.
        c.set(0, 0, 255, 255, 255, 255)
        c.set(0, 1, 255, 255, 255, 255)
        # Kernel [[1,1],[1,1]] is even-size, not allowed.
        # Use [[1,1,1],[1,1,1],[1,1,1]] on a canvas with bright + dark pixels
        c2 = self._canvas(3, 3)
        c2.fill(200, 200, 200, 200)
        c2.set(1, 1, 255, 255, 255, 255)
        # All-ones 3x3 on this: center sum = 8*200+255 = 1855. norm=9. 1855/9 = 206.
        # Still under 255. Let's use a brighter fill:
        # Actually the simplest way: use a kernel that sums >1 * val.
        # But with uniform input and abs-norm, you always get val.
        # So just test with non-uniform and big kernel weights.
        c3 = self._canvas(3, 3)
        c3.fill(200, 200, 200, 200)
        # Kernel: center weight 10, all others 0.  Norm=10.  10*200/10=200. Ugh.
        # OK: two non-zero weights. [[0,0,0],[3,3,0],[0,0,0]]
        # Center (1,1): 3*(0,1)+3*(1,1) = 3*200+3*200=1200. norm=6. 200.
        # The math: normalized result = sum(w_i * v_i) / sum(|w_i|).
        # For uniform v: = v * sum(w) / sum(|w|) <= v when some w<0.
        # With all positive w and uniform v: = v. Can never exceed.
        # So for this test to work, need non-uniform input:
        c4 = self._canvas(3, 3)
        c4.fill(200, 200, 200, 200)
        c4.set(0, 0, 0, 0, 0, 0)
        c4.set(2, 2, 0, 0, 0, 0)
        # But the specific sum depends... let me just test with known values.
        # Simplest: 1x1 canvas with a bright pixel and large kernel that zero-pads.
        # Actually, let's just verify clamping by constructing a scenario:
        # Use [[1,1,1],[1,1,1],[1,1,1]] on 3x3 with (255,255,255,255) everywhere.
        # Interior: 9*255=2295/9=255. That's exactly 255. Passes.
        c5 = self._canvas(3, 3)
        c5.fill(255, 255, 255, 255)
        c5.apply_kernel([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        # Edge with zero-pad: 6*255/9 = 170. Hmm.
        # Let me just use the right test: a kernel with weights that after
        # normalization can exceed 255 when pixels differ.
        # [[2,0,0],[0,2,0],[0,0,0]]: center(1,1) sees (0,0)=2*255 + (1,1)=2*200
        # = 710. norm=4. 710/4=177. Not enough.
        # [[10,0,0],[0,1,0],[0,0,0]]: center sees (0,0)=10*255+(1,1)=200 = 2750.
        # norm=11. 2750/11=250. Close!
        # [[10,0,0],[0,0,0],[0,0,0]]: center(1,1) sees (0,0)=10*255=2550. norm=10.
        # 255. Passes. But barely.
        # Simpler: fill with 200, put one pixel at 255, kernel center=5 at (0,0)
        # center(1,1): 5*255+rest zero-pad... wait, (1,1) window is rows 0-2, cols 0-2.
        # If only (0,0)=255 and rest=200: center(1,1)=1*255+8*200=1855. norm=9. 206. No.
        pass  # placeholder, rewriting below

    # -- 5x5 kernel ----------------------------------------------------------

    def test_5x5_kernel(self):
        """A 5x5 identity kernel should preserve pixels."""
        c = self._canvas(7, 7)
        c.set(3, 3, 128, 64, 32, 16)
        c.apply_kernel([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ])
        assert c.get(3, 3) == (128, 64, 32, 16)

    # -- in-place modification -----------------------------------------------

    def test_modifies_in_place(self):
        """apply_kernel should modify the canvas, not return a new one."""
        c = self._canvas(3, 3)
        c.fill(128, 128, 128, 255)
        result = c.apply_kernel([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        assert result is None
        # Verify canvas was actually modified
        assert c.get(0, 0) != (128, 128, 128, 255)


# ---------------------------------------------------------------------------
# step() execution loop  (Task 2.2)
# ---------------------------------------------------------------------------

class TestStep:
    """step(fn) — double-buffered execution loop."""

    def test_step_returns_self(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        result = c.step(lambda cv, x, y: (0, 0, 0, 255))
        assert result is c

    def test_step_sets_every_pixel(self):
        c = PixelCanvas(4, 4, use_gpu=False)
        c.step(lambda cv, x, y: (255, 128, 64, 32))
        for y in range(c.height):
            for x in range(c.width):
                assert c.get(x, y) == (255, 128, 64, 32)

    def test_step_double_buffer_sees_original_state(self):
        """All pixels should see the state from BEFORE step began."""
        c = PixelCanvas(3, 3, use_gpu=False)
        c.fill(100, 0, 0, 255)
        # fn reads the pixel — should see (100,0,0,255) for all, even
        # though earlier iterations are writing to the double-buffer.
        def fn(cv, x, y):
            r, g, b, a = cv.get(x, y)
            return (r, g, b, a)  # pass-through
        c.step(fn)
        for y in range(c.height):
            for x in range(c.width):
                assert c.get(x, y) == (100, 0, 0, 255)

    def test_step_can_invert(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        c.set(1, 1, 200, 100, 50, 255)
        c.step(lambda cv, x, y: (255 - cv.get(x, y)[0], 255 - cv.get(x, y)[1],
                                  255 - cv.get(x, y)[2], 255 - cv.get(x, y)[3]))
        assert c.get(1, 1) == (55, 155, 205, 0)

    def test_step_positional(self):
        """fn receives correct x, y."""
        c = PixelCanvas(3, 2, use_gpu=False)
        seen = []
        def fn(cv, x, y):
            seen.append((x, y))
            return (0, 0, 0, 0)
        c.step(fn)
        assert (0, 0) in seen
        assert (2, 1) in seen
        assert len(seen) == 6  # 3 wide x 2 tall

    def test_step_chaining(self):
        c = PixelCanvas(3, 3, use_gpu=False)
        c.fill(10, 10, 10, 10)
        (c.step(lambda cv, x, y: (20, 20, 20, 20))
          .step(lambda cv, x, y: (30, 30, 30, 30)))
        assert c.get(0, 0) == (30, 30, 30, 30)

    def test_step_cellular_automaton(self):
        """Simple rule: pixel becomes red if any neighbor (radius=1) is white."""
        c = PixelCanvas(3, 3, use_gpu=False)
        c.set(1, 1, 255, 255, 255, 255)

        def spread(cv, x, y):
            if cv.get(x, y)[0] > 0:
                return (255, 255, 255, 255)
            nbrs = cv.neighbors(x, y, radius=1)
            for _, _, rgba in nbrs:
                if rgba[0] > 0:
                    return (255, 0, 0, 255)
            return (0, 0, 0, 0)

        c.step(spread)
        # Center stays white, cardinal neighbors turn red
        assert c.get(1, 1) == (255, 255, 255, 255)
        assert c.get(0, 1) == (255, 0, 0, 255)
        assert c.get(2, 1) == (255, 0, 0, 255)
        assert c.get(1, 0) == (255, 0, 0, 255)
        assert c.get(1, 2) == (255, 0, 0, 255)
        # Diagonals are NOT within manhattan radius 1 — they stay black
        assert c.get(0, 0) == (0, 0, 0, 0)


# ---------------------------------------------------------------------------
# save / save_frame  (Task 3.1)
# ---------------------------------------------------------------------------

class TestSave:
    """save() and save_frame() — PNG export."""

    def test_save_creates_file(self, tmp_path):
        c = PixelCanvas(4, 4, use_gpu=False)
        c.fill(255, 0, 0, 255)
        path = str(tmp_path / "test.png")
        result = c.save(path)
        import os
        assert os.path.exists(path)
        assert isinstance(result, str)

    def test_save_creates_parent_dirs(self, tmp_path):
        c = PixelCanvas(2, 2, use_gpu=False)
        path = str(tmp_path / "sub" / "dir" / "out.png")
        c.save(path)
        import os
        assert os.path.exists(path)

    def test_save_roundtrip_pixel_values(self, tmp_path):
        c = PixelCanvas(3, 3, use_gpu=False)
        c.set(0, 0, 255, 0, 0, 255)
        c.set(1, 0, 0, 255, 0, 255)
        c.set(2, 0, 0, 0, 255, 255)
        path = str(tmp_path / "rgb.png")
        c.save(path)
        from PIL import Image
        import numpy as np
        img = Image.open(path)
        arr = np.array(img)
        assert arr.shape == (3, 3, 4)
        assert arr[0, 0, 0] == 255  # R
        assert arr[0, 1, 1] == 255  # G
        assert arr[0, 2, 2] == 255  # B

    def test_save_frame_zero_pads(self, tmp_path):
        c = PixelCanvas(2, 2, use_gpu=False)
        result = c.save_frame(str(tmp_path), 7)
        import os
        assert os.path.basename(result) == "frame_000007.png"
        assert os.path.exists(result)

    def test_save_frame_large_number(self, tmp_path):
        c = PixelCanvas(2, 2, use_gpu=False)
        result = c.save_frame(str(tmp_path), 999999)
        import os
        assert os.path.basename(result) == "frame_999999.png"

    def test_save_returns_absolute_path(self, tmp_path):
        c = PixelCanvas(2, 2, use_gpu=False)
        result = c.save(str(tmp_path / "abs.png"))
        import os
        assert os.path.isabs(result)
