# Incident Report: ERR-001 — Extension Mismatch in Manual Decoding

**Incident ID:** `ERR-001`  
**Date Logged:** 2026-10-27  
**Severity:** P2 (User Experience / File Type Confusion)  
**Component:** `ziptext/engine.py` & `ziptext/container.py`  
**Status:** **RESOLVED** in `v0.1.1` & `v0.2.0`

---

## 1. Description & User Observation
During manual CLI testing, the user encoded `countries.json` into a container `manualtest1.ztxt`. Later, the user attempted to decode the container into an image path:
```bash
python -m ziptext decode manualtest1.ztxt recoveredtestimg.jpg
```
The user then compared hashes of `recoveredtestimg.jpg` with the original image `resources/testimg.jpg`.
- **Result:** Hash check returned `False`.
- **User Symptom:** The file `recoveredtestimg.jpg` could not be opened by VS Code's image viewer ("An error occurred while loading the image").

---

## 2. Root Cause Analysis
1. **Container Content vs. Output Filename:**
   `manualtest1.ztxt` was an encoded package of `countries.json` (size: 8,538 bytes).
   The decoder faithfully and losslessly wrote the exact 8,538 JSON bytes into the destination path specified by the user: `recoveredtestimg.jpg`.
2. **Hash Comparison Mismatch:**
   The user compared the SHA-256 of `recoveredtestimg.jpg` (which contained JSON text) against `resources/testimg.jpg` (a 72,598 byte JPEG photo). The hashes obviously differed.
3. **IDE Viewer Inability:**
   VS Code attempted to parse `recoveredtestimg.jpg` using its image viewer engine. Because the file was pure ASCII/JSON text, the JPEG decoder rejected it as invalid image data.

---

## 3. Corrective Actions Applied
1. **Container Manifest Metadata:**
   The container header was enhanced to explicitly store `original_filename` alongside `file_sha256`.
2. **Automatic Output Naming:**
   Made destination path optional in `python -m ziptext decode <input> [output]`. If omitted, the engine automatically extracts the file using its authentic original filename and extension (`recovered_<original_filename>`).
3. **Mismatched Extension Detection:**
   If a user explicitly provides an output filename whose extension conflicts with the container's original file extension, the engine emits a clear warning:
   ```
   [WARNING] Extension Mismatch Detected! Container original file is '.json', but output requested '.jpg'.
   ```
4. **Deep Media Validation:**
   Integrated `MediaValidator.validate()`, which runs after every decode to verify that recovered images, videos, audio, documents, and code parse properly with standard system tools.
