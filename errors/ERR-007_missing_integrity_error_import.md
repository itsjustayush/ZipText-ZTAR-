# Incident Report: ERR-007 — Missing IntegrityError Import in cli.py

**Incident ID:** `ERR-007`  
**Date Logged:** 2026-10-27  
**Severity:** P2 (CLI Exception Handling Crash)  
**Component:** `ziptext/cli.py` (`cmd_verify`)  
**Status:** **RESOLVED** in `v0.1.0`

---

## 1. Description
During unit tests for CLI corruption detection (`test_cli_verify_corrupted`), the command crashed with an uncaught `NameError` rather than returning exit code 1:
```python
NameError: name 'IntegrityError' is not defined
  File "ziptext/cli.py", line 185, in cmd_verify
    except IntegrityError as e:
```

## 2. Root Cause
`IntegrityError` was raised from `ziptext/container.py`, but `cli.py` attempted to catch it without importing it from `ziptext.container`.

## 3. Fix Applied
Updated imports in `ziptext/cli.py`:
```python
from ziptext.container import IntegrityError
```

## 4. Prevention
Unit tests in `tests/test_cli.py` explicitly test corrupt files to verify `IntegrityError` is properly caught and mapped to a clean user-facing error message with exit code 1.
