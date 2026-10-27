# Incident Report: ERR-004 — Missing 'Optional' Import in cli.py

**Incident ID:** `ERR-004`  
**Date Logged:** 2026-10-27  
**Severity:** P3 (Typing Import Oversight)  
**Component:** `ziptext/cli.py`  
**Status:** **RESOLVED** in `v0.1.0`

---

## 1. Description
CLI startup failed with:
```python
NameError: name 'Optional' is not defined in ziptext/cli.py
```

## 2. Root Cause
`Optional[List[str]]` was used in `build_parser` without importing `Optional` from `typing`.

## 3. Fix Applied
Added `Optional` to `from typing import Optional` in `ziptext/cli.py`.

## 4. Prevention
All CLI invocations (`fixtures`, `encode`, `decode`, `matrix`, `verify`, `info`, `classify`) are exercised in unit test `tests/test_cli.py`.
