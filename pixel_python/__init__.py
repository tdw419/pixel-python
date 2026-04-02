"""pixel-python -- composable pixel programs and compute pipelines."""

from .canvas import PixelCanvas
from .compute import (
    ComputePipeline,
    ComputeProgram,
    ComputeRunner,
    compute_program,
)
from .dsl import DSLProgramRunner, Uniforms, pixel_program
from .program import CompositeProgram, PixelProgram, ProgramRunner

__all__ = [
    # Pixel rendering
    "PixelCanvas",
    "PixelProgram",
    "CompositeProgram",
    "ProgramRunner",
    "DSLProgramRunner",
    "Uniforms",
    "pixel_program",
    # Compute pipeline
    "ComputeProgram",
    "ComputePipeline",
    "ComputeRunner",
    "compute_program",
]
