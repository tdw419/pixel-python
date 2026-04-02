"""Tests for pixel_python.shaders and pixel_python.game_of_life."""

import pytest

from pixel_python.canvas import PixelCanvas
from pixel_python.game_of_life import ConwayLife
from pixel_python.program import ProgramRunner
from pixel_python.shaders import Gradient, Noise, SolidColor


# ── SolidColor ───────────────────────────────────────────────────

class TestSolidColor:
    def test_returns_constant_color(self):
        s = SolidColor(128, 64, 32)
        canvas = PixelCanvas(4, 4, use_gpu=False)
        assert s.update(canvas, 0, 0) == (128, 64, 32, 255)
        assert s.update(canvas, 3, 3) == (128, 64, 32, 255)

    def test_custom_alpha(self):
        s = SolidColor(255, 0, 0, 128)
        canvas = PixelCanvas(2, 2, use_gpu=False)
        assert s.update(canvas, 0, 0) == (255, 0, 0, 128)

    def test_is_pixel_program(self):
        from pixel_python.program import PixelProgram
        s = SolidColor(0, 0, 0)
        assert isinstance(s, PixelProgram)


# ── Gradient ─────────────────────────────────────────────────────

class TestGradient:
    def test_horizontal_gradient(self):
        g = Gradient("horizontal", (0, 0, 0, 255), (255, 255, 255, 255))
        canvas = PixelCanvas(10, 1, use_gpu=False)
        # Left edge should be black
        assert g.update(canvas, 0, 0) == (0, 0, 0, 255)
        # Right edge should be white
        assert g.update(canvas, 9, 0) == (255, 255, 255, 255)
        # Middle should be ~127
        mid = g.update(canvas, 5, 0)
        assert 100 < mid[0] < 155

    def test_vertical_gradient(self):
        g = Gradient("vertical", (0, 0, 0, 255), (255, 0, 0, 255))
        canvas = PixelCanvas(1, 10, use_gpu=False)
        top = g.update(canvas, 0, 0)
        bot = g.update(canvas, 0, 9)
        assert top == (0, 0, 0, 255)
        assert bot == (255, 0, 0, 255)

    def test_invalid_direction(self):
        with pytest.raises(ValueError, match="direction"):
            Gradient("diagonal")


# ── Noise ────────────────────────────────────────────────────────

class TestNoise:
    def test_grayscale_noise_range(self):
        n = Noise(seed=42, grayscale=True)
        canvas = PixelCanvas(10, 10, use_gpu=False)
        for x in range(10):
            for y in range(10):
                r, g, b, a = n.update(canvas, x, y)
                assert r == g == b  # grayscale
                assert 0 <= r <= 255
                assert a == 255

    def test_seed_reproducibility(self):
        n1 = Noise(seed=123)
        n2 = Noise(seed=123)
        canvas = PixelCanvas(5, 5, use_gpu=False)
        for x in range(5):
            for y in range(5):
                assert n1.update(canvas, x, y) == n2.update(canvas, x, y)

    def test_different_seeds_differ(self):
        n1 = Noise(seed=1)
        n2 = Noise(seed=2)
        canvas = PixelCanvas(5, 5, use_gpu=False)
        different = False
        for x in range(5):
            for y in range(5):
                if n1.update(canvas, x, y) != n2.update(canvas, x, y):
                    different = True
                    break
        assert different

    def test_color_noise(self):
        n = Noise(seed=42, grayscale=False)
        canvas = PixelCanvas(10, 10, use_gpu=False)
        # At least one pixel should have different R and G (not grayscale)
        found_color = False
        for x in range(10):
            for y in range(10):
                r, g, b, _ = n.update(canvas, x, y)
                if r != g or g != b:
                    found_color = True
                    break
        assert found_color


# ── ConwayLife ───────────────────────────────────────────────────

class TestConwayLife:
    def _set_cell(self, canvas, x, y, alive=True):
        """Helper to set a cell alive (white) or dead (black)."""
        color = (255, 255, 255, 255) if alive else (0, 0, 0, 255)
        canvas.set(x, y, *color)

    def test_blinker_oscillates(self):
        """Classic blinker: 3-wide horizontal line oscillates to vertical."""
        canvas = PixelCanvas(5, 5, use_gpu=False)
        life = ConwayLife(threshold=63.75)

        # Set up blinker: row 2, cols 1-3
        self._set_cell(canvas, 1, 2)
        self._set_cell(canvas, 2, 2)
        self._set_cell(canvas, 3, 2)

        # Run one step
        runner = ProgramRunner(canvas, life, frames=1)
        runner.run()

        # After 1 step: should be vertical — (2,1), (2,2), (2,3)
        assert canvas.get(2, 1) == (255, 255, 255, 255)
        assert canvas.get(2, 2) == (255, 255, 255, 255)
        assert canvas.get(2, 3) == (255, 255, 255, 255)
        # (1,2) should now be dead
        assert canvas.get(1, 2) == (0, 0, 0, 255)

        # Run another step — should return to horizontal
        runner2 = ProgramRunner(canvas, life, frames=1)
        runner2.run()

        assert canvas.get(1, 2) == (255, 255, 255, 255)
        assert canvas.get(2, 2) == (255, 255, 255, 255)
        assert canvas.get(3, 2) == (255, 255, 255, 255)
        assert canvas.get(2, 1) == (0, 0, 0, 255)

    def test_dead_cell_with_no_neighbors_stays_dead(self):
        canvas = PixelCanvas(3, 3, use_gpu=False)
        # All black
        life = ConwayLife()
        runner = ProgramRunner(canvas, life, frames=1)
        runner.run()
        # Still all black
        for y in range(3):
            for x in range(3):
                assert canvas.get(x, y) == (0, 0, 0, 255)

    def test_block_still_life(self):
        """A 2x2 block is a still life — should not change."""
        canvas = PixelCanvas(4, 4, use_gpu=False)
        life = ConwayLife(threshold=63.75)

        self._set_cell(canvas, 1, 1)
        self._set_cell(canvas, 1, 2)
        self._set_cell(canvas, 2, 1)
        self._set_cell(canvas, 2, 2)

        runner = ProgramRunner(canvas, life, frames=1)
        runner.run()

        # Block should be unchanged
        assert canvas.get(1, 1) == (255, 255, 255, 255)
        assert canvas.get(1, 2) == (255, 255, 255, 255)
        assert canvas.get(2, 1) == (255, 255, 255, 255)
        assert canvas.get(2, 2) == (255, 255, 255, 255)
