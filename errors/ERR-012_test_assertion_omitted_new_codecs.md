# Incident Report: ERR-012 — Test Assertion Omitted Newly Added Codecs

**Incident ID:** `ERR-012`  
**Date Logged:** 2026-10-27  
**Severity:** P2 (Unit Test Regression / Assertion Staleness)  
**Component:** `tests/test_engine.py` (`test_engine_adaptive_selection`)  
**Status:** **RESOLVED** in `v0.2.0`

---

## 1. Description
After adding `zstd` and `brotli` codecs to `CodecRegistry`, running the full pytest suite failed with:
```python
FAILED tests/test_engine.py::test_engine_adaptive_selection - assert False
```

## 2. Root Cause
In `test_engine_adaptive_selection`, a repetitive text file was encoded using `codec="auto"`. Because Brotli achieves higher compression ratio than standard dictionary algorithms on repetitive text, `auto` policy appropriately selected `brotli`. However, the unit test assertion was hardcoded to an obsolete list of historical codecs:
```python
assert any(c in ["lzma", "zlib", "bz2", "lz4"] for c in codecs_used)
```
Since `codecs_used` was `['brotli']`, the assertion failed even though the compression engine made the mathematically superior choice.

## 3. Fix Applied
Updated `tests/test_engine.py` to include all registered non-raw codecs:
```python
assert any(c in ["lzma", "zlib", "bz2", "lz4", "zstd", "brotli"] for c in codecs_used)
```

## 4. Prevention
Dynamic tests now assert that `raw` is not selected on high-redundancy data rather than enumerating an exhaustive list of active compressors.
