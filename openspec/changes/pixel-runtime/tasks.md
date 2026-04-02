# Tasks: Pixel Runtime Core

## 1. Core Canvas
- [x] 1.1 Create pixel_python/canvas.py with PixelCanvas class. Constructor takes width, height, use_gpu=True. Allocates a 2D uint32 array via cupy if available else numpy. Properties: width, height, shape, is_gpu.
- [x] 1.2 Implement pixel read/write. get(x, y) returns RGBA tuple. set(x, y, r, g, b, a=255) packs RGBA into uint32. Out-of-bounds raises IndexError. fill(r, g, b, a=255) fills entire canvas.
- [x] 1.3 Implement neighbors(x, y, radius=1) returning list of (nx, ny, rgba) tuples for all cells within manhattan distance radius. Handles edge clamping.

## 2. Spatial Operations
- [x] 2.1 Implement apply_kernel(kernel) that convolves a 2D kernel array over the canvas. Kernel is a list of lists of numbers. Output pixel is weighted sum of neighbors normalized. Modifies canvas in-place.
- [x] 2.2 Implement step(fn) execution loop. fn(canvas, x, y) returns RGBA tuple. step iterates every pixel, calls fn, writes result to double buffer, then swaps. Returns self for chaining.

## 3. Output and Tests
- [x] 3.1 Implement save(path) that exports buffer to PNG via Pillow. Auto-creates parent dirs. save_frame(path, frame_number) zero-pads frame number into filename.
- [x] 3.2 Write tests in tests/test_canvas.py covering: canvas creation with GPU and CPU fallback, pixel get/set roundtrip, fill, neighbors, kernel application, step function with double-buffering, PNG export. Minimum 20 tests.
