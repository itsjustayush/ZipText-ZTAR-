# Incident Report: ERR-010 — PowerShell Statement Separator Syntax Collision

**Incident ID:** `ERR-010`  
**Date Logged:** 2026-10-27  
**Severity:** P3 (Shell Platform Environment Quirk)  
**Component:** Terminal Execution Environment (Windows PowerShell)  
**Status:** **RESOLVED** in `v0.2.0`

---

## 1. Description
Executing chained commands with `&&` failed in PowerShell:
```powershell
git add . && git commit -m "..."
ParserError: The token '&&' is not a valid statement separator in this version.
```

## 2. Root Cause
In Windows PowerShell (versions 5.1 and earlier), `&&` (conditional AND) is not supported as a pipeline statement separator; PowerShell uses `;` for sequential statements or requires PowerShell 7+ for `&&`.

## 3. Fix Applied
Used PowerShell-compliant statement separator `;`:
```powershell
git add . ; git commit -m "..."
```

## 4. Prevention
All automated scripts and command propositions target standard PowerShell syntax.
