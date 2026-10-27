# Incident Report: ERR-003 — Missing 'Union' Import in fixtures.py

**Incident ID:** `ERR-003`  
**Date Logged:** 2026-10-27  
**Severity:** P3 (Typing Import Oversight)  
**Component:** `ziptext/fixtures.py`  
**Status:** **RESOLVED** in `v0.1.0`

---

## 1. Description
During generation of synthetic benchmark fixtures, execution failed with:
```python
NameError: name 'Union' is not defined in ziptext/fixtures.py
```

## 2. Root Cause
In `generate_corpus(output_dir: Union[str, Path])`, `Union` was used as a type annotation, but `typing` only imported `Dict, List, Path`.

## 3. Fix Applied
Updated import statement in `ziptext/fixtures.py`:
```python
from typing import Dict, List, Union
```

## 4. Prevention
Verified all fixture generation scripts execute under clean Python processes before executing test suites.
