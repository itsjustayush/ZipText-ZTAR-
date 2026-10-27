# Incident Report: ERR-006 — Setuptools Flat-Layout Discovery Collision

**Incident ID:** `ERR-006`  
**Date Logged:** 2026-10-27  
**Severity:** P2 (Packaging / Environment Build Failure)  
**Component:** `pyproject.toml`  
**Status:** **RESOLVED** in `v0.1.0`

---

## 1. Description
Running `pip install -e .` failed with setuptools error:
```
error: Multiple top-level packages discovered in a flat-layout: ['ziptext', 'results'].
Setuptools cannot determine which packages to install.
```

## 2. Root Cause
In a "flat-layout" Python project structure, Setuptools automatically considers every directory with or without an `__init__.py` as a potential package if not explicitly configured. When `results/` was created to store matrix outputs, Setuptools detected it alongside `ziptext/`.

## 3. Fix Applied
In `pyproject.toml`, explicitly configured package auto-discovery to restrict search only to `ziptext`:
```toml
[tool.setuptools.packages.find]
include = ["ziptext*"]
```

## 4. Prevention
Editable installs now consistently isolate `ziptext` code irrespective of any output or reports directory created in the root workspace.
