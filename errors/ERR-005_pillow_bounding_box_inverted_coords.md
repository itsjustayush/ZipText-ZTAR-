# Incident Report: ERR-005 — Inverted Pillow Bounding Box Coordinates

**Incident ID:** `ERR-005`  
**Date Logged:** 2026-10-27  
**Severity:** P1 (Synthetic Fixture Generation Crash)  
**Component:** `ziptext/fixtures.py` (`generate_synthetic_png`)  
**Status:** **RESOLVED** in `v0.1.0`

---

## 1. Description
When executing synthetic PNG image generation via Pillow, execution crashed with:
```python
ValueError: y1 must be greater than or equal to y0
  File "PIL/ImageDraw.py", line 282, in rectangle
    self.draw.draw_rectangle(xy, ink, 0, width)
```

## 2. Root Cause
In `generate_synthetic_png`, rectangle coordinates were computed with a formula where iteration index caused $y_1 < y_0$ when the loop index crossed the midpoint of the image canvas. Pillow strictly validates that $[x_0, y_0, x_1, y_1]$ satisfies $x_1 \ge x_0$ and $y_1 \ge y_0$.

## 3. Fix Applied
Replaced the symmetric nested loop with positive ordered bounding box coordinates:
```python
d.rectangle([x, y, x + w, y + h], fill=...)
```
ensuring $x_1 \ge x_0$ and $y_1 \ge y_0$ across all iterations.

## 4. Prevention
Added explicit coordinate assertions and unit test `test_fixtures.py` to verify all image generators output valid PNG buffers.
