"""Tests for pixel_python.program — PixelProgram, CompositeProgram, ProgramRunner."""

import os
import tempfile
from pathlib import Path

import pytest

from pixel_python.canvas import PixelCanvas
from pixel_python.program import (
    CompositeProgram,
    PixelProgram,
    ProgramRunner,
    _BLEND_MODES,
)


# ── Helpers ──────────────────────────────────────────────────────

class SolidColor(PixelProgram):
    """Simple program that returns a fixed color."""
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r, self.g, self.b, self.a = r, g, b, a

    def update(self, canvas, x: int, y: int):
        return (self.r, self.g, self.b, self.a)


class PositionColor(PixelProgram):
    """Color based on position — useful for gradient-like effects."""
    def update(self, canvas, x: int, y: int):
        r = (x * 255) // max(canvas.width - 1, 1)
        g = (y * 255) // max(canvas.height - 1, 1)
        return (r, g, 128, 255)


class CountingProgram(PixelProgram):
    """Tracks how many times update/setup/teardown are called."""
    update_calls = 0
    setup_calls = 0
    teardown_calls = 0

    def update(self, canvas, x: int, y: int):
        CountingProgram.update_calls += 1
        return (255, 0, 0, 255)

    def setup(self, canvas):
        CountingProgram.setup_calls += 1

    def teardown(self, canvas):
        CountingProgram.teardown_calls += 1


# ── PixelProgram base ────────────────────────────────────────────

class TestPixelProgramBase:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError, match="abstract"):
            PixelProgram()

    def test_subclass_works(self):
        prog = SolidColor(100, 200, 50)
        canvas = PixelCanvas(4, 4, use_gpu=False)
        rgba = prog.update(canvas, 0, 0)
        assert rgba == (100, 200, 50, 255)

    def test_name_defaults_to_class_name(self):
        prog = SolidColor(0, 0, 0)
        assert prog.name == "SolidColor"

    def test_setup_teardown_default_noop(self):
        prog = SolidColor(0, 0, 0)
        canvas = PixelCanvas(2, 2, use_gpu=False)
        prog.setup(canvas)   # should not raise
        prog.teardown(canvas)


# ── CompositeProgram ────────────────────────────────────────────

class TestCompositeProgram:
    def test_empty_composite_returns_transparent(self):
        comp = CompositeProgram()
        canvas = PixelCanvas(2, 2, use_gpu=False)
        result = comp.update(canvas, 0, 0)
        assert result == (0, 0, 0, 0)

    def test_single_layer_normal(self):
        comp = CompositeProgram()
        comp.add(SolidColor(255, 0, 0), "normal")
        canvas = PixelCanvas(2, 2, use_gpu=False)
        result = comp.update(canvas, 0, 0)
        assert result == (255, 0, 0, 255)

    def test_two_layers_normal(self):
        comp = CompositeProgram()
        comp.add(SolidColor(255, 0, 0), "normal")
        comp.add(SolidColor(0, 255, 0), "normal")
        canvas = PixelCanvas(2, 2, use_gpu=False)
        # Normal blend overwrites, so last layer wins
        result = comp.update(canvas, 0, 0)
        assert result == (0, 255, 0, 255)

    def test_additive_blend(self):
        comp = CompositeProgram()
        comp.add(SolidColor(100, 50, 25), "add")
        comp.add(SolidColor(50, 100, 25), "add")
        canvas = PixelCanvas(2, 2, use_gpu=False)
        result = comp.update(canvas, 0, 0)
        assert result == (150, 150, 50, 255)

    def test_multiply_blend(self):
        comp = CompositeProgram()
        # Start with a solid base via normal, then multiply over it
        comp.add(SolidColor(200, 100, 50), "normal")
        comp.add(SolidColor(255, 128, 255), "multiply")
        canvas = PixelCanvas(2, 2, use_gpu=False)
        result = comp.update(canvas, 0, 0)
        # Normal sets (200,100,50,255), then multiply (255,128,255) * (200,100,50) / 255
        assert result[0] == 200 * 255 // 255  # = 200
        assert result[1] == 100 * 128 // 255  # = 50
        assert result[2] == 50 * 255 // 255   # = 50

    def test_alpha_blend(self):
        comp = CompositeProgram()
        comp.add(SolidColor(0, 0, 0, 255), "normal")  # base: opaque black
        comp.add(SolidColor(255, 0, 0, 128), "alpha")  # 50% red over black
        canvas = PixelCanvas(2, 2, use_gpu=False)
        result = comp.update(canvas, 0, 0)
        assert result[0] == 128  # half red
        assert result[1] == 0
        assert result[2] == 0

    def test_invalid_blend_mode_raises(self):
        comp = CompositeProgram()
        with pytest.raises(ValueError, match="unknown blend mode"):
            comp.add(SolidColor(0, 0, 0), "invalid")

    def test_constructor_with_programs(self):
        comp = CompositeProgram([
            (SolidColor(255, 0, 0), "normal"),
            (SolidColor(0, 255, 0), "add"),
        ])
        canvas = PixelCanvas(2, 2, use_gpu=False)
        result = comp.update(canvas, 0, 0)
        assert result == (255, 255, 0, 255)  # normal sets red (255,0,0), add green (0,255,0) = (255,255,0)

    def test_setup_teardown_propagates(self):
        p1 = CountingProgram()
        CountingProgram.setup_calls = 0
        CountingProgram.teardown_calls = 0
        comp = CompositeProgram([(p1, "normal")])
        canvas = PixelCanvas(2, 2, use_gpu=False)
        comp.setup(canvas)
        comp.teardown(canvas)
        assert CountingProgram.setup_calls == 1
        assert CountingProgram.teardown_calls == 1


# ── ProgramRunner ────────────────────────────────────────────────

class TestProgramRunner:
    def test_single_frame(self):
        canvas = PixelCanvas(4, 4, use_gpu=False)
        prog = SolidColor(255, 0, 0)
        runner = ProgramRunner(canvas, prog, frames=1)
        paths = runner.run()
        assert paths == []
        # Canvas should be all red now
        assert canvas.get(0, 0) == (255, 0, 0, 255)
        assert canvas.get(3, 3) == (255, 0, 0, 255)

    def test_multiple_frames(self):
        canvas = PixelCanvas(2, 2, use_gpu=False)
        prog = SolidColor(100, 200, 50)
        runner = ProgramRunner(canvas, prog, frames=3)
        runner.run()
        # Still solid after 3 frames
        assert canvas.get(0, 0) == (100, 200, 50, 255)

    def test_on_frame_callback(self):
        frames_seen = []

        def on_frame(canvas, frame_num):
            frames_seen.append(frame_num)

        canvas = PixelCanvas(2, 2, use_gpu=False)
        prog = SolidColor(0, 0, 0)
        runner = ProgramRunner(canvas, prog, frames=5, on_frame=on_frame)
        runner.run()
        assert frames_seen == [1, 2, 3, 4, 5]

    def test_auto_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            canvas = PixelCanvas(4, 4, use_gpu=False)
            prog = SolidColor(255, 0, 0)
            runner = ProgramRunner(canvas, prog, frames=10, save_every=5)
            paths = runner.run(output_dir=tmpdir)
            assert len(paths) == 2
            for p in paths:
                assert Path(p).exists()
                assert p.endswith(".png")

    def test_setup_and_teardown_called(self):
        CountingProgram.setup_calls = 0
        CountingProgram.teardown_calls = 0

        canvas = PixelCanvas(2, 2, use_gpu=False)
        prog = CountingProgram()
        runner = ProgramRunner(canvas, prog, frames=2)
        runner.run()

        assert CountingProgram.setup_calls == 1
        assert CountingProgram.teardown_calls == 1

    def test_teardown_called_on_error(self):
        CountingProgram.teardown_calls = 0

        class FailProgram(PixelProgram):
            def update(self, canvas, x, y):
                raise RuntimeError("boom")

        canvas = PixelCanvas(2, 2, use_gpu=False)

        class TeardownTracker(PixelProgram):
            torn_down = False
            def update(self, canvas, x, y):
                raise RuntimeError("boom")
            def teardown(self, canvas):
                TeardownTracker.torn_down = True

        prog = TeardownTracker()
        runner = ProgramRunner(canvas, prog, frames=1)
        with pytest.raises(RuntimeError):
            runner.run()
        assert TeardownTracker.torn_down

    def test_invalid_frames_raises(self):
        canvas = PixelCanvas(2, 2, use_gpu=False)
        with pytest.raises(ValueError, match="frames"):
            ProgramRunner(canvas, SolidColor(0, 0, 0), frames=0)

    def test_position_program_produces_gradient(self):
        canvas = PixelCanvas(8, 8, use_gpu=False)
        prog = PositionColor()
        runner = ProgramRunner(canvas, prog, frames=1)
        runner.run()
        # Top-left should be dark, bottom-right should be bright
        tl = canvas.get(0, 0)
        br = canvas.get(7, 7)
        assert tl[0] < br[0]  # R increases with x
        assert tl[1] < br[1]  # G increases with y
