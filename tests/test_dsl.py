"""Tests for pixel_python.dsl — @pixel_program decorator and Uniforms."""

import time

import pytest

from pixel_python.canvas import PixelCanvas
from pixel_python.dsl import DSLProgramRunner, Uniforms, pixel_program
from pixel_python.program import PixelProgram


# ── Uniforms ─────────────────────────────────────────────────────

class TestUniforms:
    def test_builtin_defaults(self):
        u = Uniforms()
        assert u["time"] == 0.0
        assert u["frame"] == 0
        assert u["resolution"] == (0, 0)

    def test_custom_uniforms(self):
        u = Uniforms(speed=2.5, color="red")
        assert u["speed"] == 2.5
        assert u["color"] == "red"

    def test_set_and_get(self):
        u = Uniforms()
        u.set("my_var", 42)
        assert u["my_var"] == 42
        assert u.get("missing", "default") == "default"

    def test_update_builtins(self):
        u = Uniforms()
        u.update_builtins(time=1.5, frame=3, resolution=(10, 20))
        assert u["time"] == 1.5
        assert u["frame"] == 3
        assert u["resolution"] == (10, 20)

    def test_contains(self):
        u = Uniforms(x=1)
        assert "time" in u
        assert "x" in u
        assert "missing" not in u

    def test_keys(self):
        u = Uniforms(x=1)
        assert u.keys() == {"time", "frame", "resolution", "x"}


# ── @pixel_program decorator ────────────────────────────────────

class TestPixelProgramDecorator:
    def test_basic_decorator(self):
        @pixel_program
        def red(canvas, x, y):
            return (255, 0, 0, 255)

        prog = red()
        canvas = PixelCanvas(4, 4, use_gpu=False)
        assert prog.update(canvas, 0, 0) == (255, 0, 0, 255)

    def test_decorator_is_pixel_program(self):
        @pixel_program
        def blue(canvas, x, y):
            return (0, 0, 255, 255)

        prog = blue()
        assert isinstance(prog, PixelProgram)

    def test_decorator_preserves_name(self):
        @pixel_program
        def my_cool_effect(canvas, x, y):
            return (0, 0, 0, 255)

        assert my_cool_effect.__name__ == "my_cool_effect"
        assert my_cool_effect().name == "my_cool_effect"

    def test_decorator_with_uniforms(self):
        @pixel_program
        def timed(canvas, x, y, uniforms):
            t = uniforms["time"]
            r = int(min(255, t * 100))
            return (r, 0, 0, 255)

        u = Uniforms()
        u.update_builtins(time=2.0)
        prog = timed(uniforms=u)
        canvas = PixelCanvas(2, 2, use_gpu=False)
        result = prog.update(canvas, 0, 0)
        assert result[0] == 200  # 2.0 * 100

    def test_decorator_without_uniforms_arg(self):
        """Functions with 3 args (canvas, x, y) should still work."""
        @pixel_program
        def simple(canvas, x, y):
            return (128, 128, 128, 255)

        prog = simple()
        canvas = PixelCanvas(2, 2, use_gpu=False)
        assert prog.update(canvas, 0, 0) == (128, 128, 128, 255)


# ── DSLProgramRunner ─────────────────────────────────────────────

class TestDSLProgramRunner:
    def test_uniforms_injected(self):
        @pixel_program
        def timed(canvas, x, y, uniforms):
            # Access frame uniform
            return (uniforms["frame"], 0, 0, 255)

        canvas = PixelCanvas(2, 2, use_gpu=False)
        prog = timed()
        runner = DSLProgramRunner(canvas, prog, frames=3)
        runner.run()

        # After 3 frames, last frame should have value 3 in red channel
        r, g, b, a = canvas.get(0, 0)
        assert r == 3

    def test_time_uniform_advances(self):
        times_seen = []

        @pixel_program
        def timer_prog(canvas, x, y, uniforms):
            if x == 0 and y == 0:
                times_seen.append(uniforms["time"])
            return (0, 0, 0, 255)

        canvas = PixelCanvas(2, 2, use_gpu=False)
        prog = timer_prog()
        runner = DSLProgramRunner(canvas, prog, frames=3)
        runner.run()

        # Time should advance across frames
        assert len(times_seen) == 3
        assert times_seen[0] <= times_seen[1] <= times_seen[2]
