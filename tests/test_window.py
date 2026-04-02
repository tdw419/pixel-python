"""Tests for Window dataclass (SEC-1)."""

from __future__ import annotations

import pytest

from pixel_python.window import Window


class TestWindowCreation:
    """1.1 — basic dataclass fields."""

    def test_defaults(self):
        w = Window(x=10, y=20, width=100, height=50)
        assert w.x == 10
        assert w.y == 20
        assert w.width == 100
        assert w.height == 50
        assert w.title == "Untitled"
        assert w.z_order == 0
        assert w.visible is True
        assert w.focused is False

    def test_custom_fields(self):
        w = Window(
            x=0, y=0, width=640, height=480,
            title="Editor", z_order=5, visible=False, focused=True,
        )
        assert w.title == "Editor"
        assert w.z_order == 5
        assert w.visible is False
        assert w.focused is True


class TestWindowBuffer:
    """1.2 — lazily-created PixelCanvas buffer."""

    def test_buffer_is_pixel_canvas(self):
        w = Window(x=0, y=0, width=80, height=60)
        buf = w.buffer
        from pixel_python.canvas import PixelCanvas
        assert isinstance(buf, PixelCanvas)

    def test_buffer_dimensions_match_window(self):
        w = Window(x=0, y=0, width=80, height=60)
        assert w.buffer.width == 80
        assert w.buffer.height == 60

    def test_buffer_uses_cpu(self):
        w = Window(x=0, y=0, width=80, height=60)
        assert w.buffer.is_gpu is False

    def test_buffer_lazy_created(self):
        w = Window(x=0, y=0, width=80, height=60)
        assert w._buffer is None
        _ = w.buffer
        assert w._buffer is not None

    def test_buffer_same_instance_on_repeat_access(self):
        w = Window(x=0, y=0, width=80, height=60)
        assert w.buffer is w.buffer


class TestWindowResize:
    """1.3 — resize recreates buffer, preserving pixels."""

    def test_resize_updates_dimensions(self):
        w = Window(x=0, y=0, width=100, height=100)
        w.resize(200, 150)
        assert w.width == 200
        assert w.height == 150

    def test_resize_recreates_buffer(self):
        w = Window(x=0, y=0, width=100, height=100)
        old_buf = w.buffer
        w.resize(200, 150)
        new_buf = w.buffer
        assert new_buf is not old_buf
        assert new_buf.width == 200
        assert new_buf.height == 150

    def test_resize_preserves_existing_pixels(self):
        w = Window(x=0, y=0, width=100, height=100)
        w.buffer.set(10, 10, 255, 0, 0, 255)
        w.resize(200, 200)
        r, g, b, a = w.buffer.get(10, 10)
        assert r == 255
        assert g == 0

    def test_resize_shrinks_buffer(self):
        w = Window(x=0, y=0, width=100, height=100)
        w.buffer.set(10, 10, 0, 255, 0, 255)
        w.resize(50, 50)
        r, g, b, a = w.buffer.get(10, 10)
        assert g == 255


class TestWindowMove:
    """1.4 — move updates position."""

    def test_move_updates_position(self):
        w = Window(x=10, y=20, width=100, height=100)
        w.move(30, 40)
        assert w.x == 30
        assert w.y == 40

    def test_move_does_not_affect_buffer(self):
        w = Window(x=0, y=0, width=80, height=60)
        buf = w.buffer
        w.move(50, 50)
        assert w.buffer is buf
