#!/usr/bin/env python3
"""Lava lamp effect using CompositeProgram with noise and color cycling."""

import math
import tempfile

from pixel_python.canvas import PixelCanvas
from pixel_python.dsl import DSLProgramRunner, Uniforms, pixel_program
from pixel_python.program import CompositeProgram
from pixel_python.shaders import Noise


@pixel_program
def color_cycle(canvas, x, y, uniforms):
    """Smooth color cycling based on time and position."""
    t = uniforms["time"]
    # Normalized coordinates
    nx = x / canvas.width
    ny = y / canvas.height

    # Create swirling color pattern
    angle = math.sin(nx * 6.28 + t * 2) + math.cos(ny * 6.28 + t * 1.5)
    r = int(128 + 127 * math.sin(angle + t * 3))
    g = int(128 + 127 * math.sin(angle + t * 2 + 2.094))
    b = int(128 + 127 * math.sin(angle + t * 2.5 + 4.189))

    return (r, g, b, 255)


@pixel_program
def blob(canvas, x, y, uniforms):
    """Moving blob that creates the lava lamp 'blob' effect."""
    t = uniforms["time"]
    cx = canvas.width / 2 + math.sin(t * 0.7) * canvas.width * 0.25
    cy = canvas.height / 2 + math.cos(t * 0.5) * canvas.height * 0.25

    dx = x - cx
    dy = y - cy
    dist = math.sqrt(dx * dx + dy * dy)
    radius = canvas.width * 0.3

    if dist < radius:
        intensity = 1.0 - (dist / radius)
        v = int(255 * intensity * intensity)
        return (v, int(v * 0.3), int(v * 0.8), 200)
    return (0, 0, 0, 0)


def main():
    width, height = 128, 128
    canvas = PixelCanvas(width, height, use_gpu=False)

    # Layer: color cycle + blob + noise
    comp = CompositeProgram()
    comp.add(color_cycle(), "normal")
    comp.add(blob(), "alpha")
    comp.add(Noise(seed=42, grayscale=True), "alpha")

    output_dir = tempfile.mkdtemp(prefix="lava_lamp_")
    print(f"Rendering 30 frames to {output_dir}/")

    runner = DSLProgramRunner(
        canvas, comp,
        frames=30,
        save_every=1,
    )
    paths = runner.run(output_dir=output_dir)

    print(f"Saved {len(paths)} frames:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()
