# Incident Report: ERR-011 — Missing TextEncodingRegistry Symbol

**Incident ID:** `ERR-011`  
**Date Logged:** 2026-10-27  
**Severity:** P3 (Typing / Class Reference Mismatch)  
**Component:** `ziptext/benchmarks/four_tier_eval.py`  
**Status:** **RESOLVED** in `v0.2.0`

---

## 1. Description
During execution of the new Canterbury Corpus benchmark runner:
```python
ImportError: cannot import name 'TextEncodingRegistry' from 'ziptext.text_encodings'
```

## 2. Root Cause
`ziptext/text_encodings.py` defines procedural functions `encode_text` and `decode_text` rather than a class named `TextEncodingRegistry`. The evaluation module mistakenly attempted to import the non-existent class.

## 3. Fix Applied
Updated `ziptext/benchmarks/four_tier_eval.py`:
```python
from ziptext.text_encodings import encode_text
text_payload = encode_text(best_comp_bytes, "base85")
```

## 4. Prevention
Ran unit tests across `ziptext.benchmarks` package to verify all symbol imports resolve without exception.
