# Incident Report: ERR-008 — Corruption Test Mutated Manifest Instead of Payload

**Incident ID:** `ERR-008`  
**Date Logged:** 2026-10-27  
**Severity:** P2 (Test Harness Logic Flaw)  
**Component:** `tests/test_corruption.py` (`test_corrupt_chunk_payload`)  
**Status:** **RESOLVED** in `v0.1.0`

---

## 1. Description
The test `test_corrupt_chunk_payload` was designed to verify that tampered Base85 chunk payloads trigger chunk-level checksum integrity failures. Instead, the container parser threw:
```python
ValueError: Invalid manifest line: ...
```

## 2. Root Cause
The test fixture mutation logic naively selected a random line from the first 10 lines of the container file. Because lines 1–10 contain JSON manifest header keys (such as `chunk_size` and `file_sha256`), modifying them invalidated the manifest syntax instead of testing payload chunk checksum verification.

## 3. Fix Applied
Updated `test_corrupt_chunk_payload` to identify the line index containing `-----BEGIN CHUNK` and only mutate text lines strictly within the chunk payload body.

## 4. Prevention
Distinguished separate tests for:
1. `test_corrupt_manifest_header` (verifies header tampering detection)
2. `test_corrupt_chunk_payload` (verifies chunk-level CRC/SHA-256 detection)
