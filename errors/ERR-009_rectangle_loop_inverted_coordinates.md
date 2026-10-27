# Incident Report: ERR-009 — Rectangle Loop Crossing Midpoint Coordinates

**Incident ID:** `ERR-009`  
**Date Logged:** 2026-10-27  
**Severity:** P1 (Test Generator Crash)  
**Component:** `fixtures/make_all_categories.py`  
**Status:** **RESOLVED** in `v0.2.0`

---

## 1. Description
During execution of `python fixtures/make_all_categories.py`, generation failed with:
```python
ValueError: x1 must be greater than or equal to x0
  File "fixtures/make_all_categories.py", line 45, in <module>
    d.rectangle([i * 5, i * 5, 190 - i * 5, 190 - i * 5], outline=(i * 8 % 255, 100, 200))
  File "PIL/ImageDraw.py", line 396, in rectangle
    self.draw.draw_rectangle(xy, ink, 0, width)
```

## 2. Root Cause
In `for i in range(30):`, when $i \ge 20$:
- $x_0 = i \times 5 = 100$
- $x_1 = 190 - (i \times 5) = 90$
Since $x_1 (90) < x_0 (100)$, Pillow's drawing kernel threw a `ValueError`.

## 3. Fix Applied
Constrained loop bound to `for i in range(18):`, ensuring $i \times 5 < 190 - i \times 5$ for all iterations (at $i=17$, $x_0=85$, $x_1=105$).

## 4. Prevention
Ran end-to-end integration test `tests/test_all_categories.py` across all generated image assets.
