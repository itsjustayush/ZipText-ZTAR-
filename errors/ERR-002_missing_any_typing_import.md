# Incident Report: ERR-002 — Missing 'Any' Import in engine.py

**Incident ID:** `ERR-002`  
**Date Logged:** 2026-10-27  
**Severity:** P3 (Typing Import Oversight)  
**Component:** `ziptext/engine.py`  
**Status:** **RESOLVED** in `v0.1.0`

---

## 1. Description
During initial testing of `ziptext/engine.py`, Python raised:
```python
NameError: name 'Any' is not defined in ziptext/engine.py
```

## 2. Root Cause
In dataclass definitions for `EncodeResult` and `DecodeResult`, `Any` was used in type hints, but `typing` only imported `Dict, List, Optional, Tuple, Union`.

## 3. Fix Applied
Added `Any` to `from typing import Any, Dict, List, Optional, Tuple, Union` in `ziptext/engine.py`.

## 4. Prevention
Configured static analysis tests (`flake8`/`pytest`) to verify all modules load without unhandled `NameError`.
