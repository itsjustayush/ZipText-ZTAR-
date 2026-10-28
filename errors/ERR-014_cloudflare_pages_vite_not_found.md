# Incident Report: ERR-014 — Cloudflare Pages Monorepo Build Failure (`vite: not found`)

- **Incident ID**: `ERR-014`
- **Severity**: **P2 (Medium)**
- **Subsystem**: Deployment / Cloudflare Pages CI/CD / Monorepo Dependencies
- **Status**: **RESOLVED**
- **Date**: 2026-10-28

---

## 1. Incident Summary

During the initial deployment of the ZipText documentation website to Cloudflare Pages, Cloudflare's build container cloned the repository, initialized the build environment, and executed `bun install` followed by `pip install .` at the repository root. When it subsequently executed the configured user build command `npm run build` (which invoked `npm --prefix web run build`), the build abruptly aborted with:

```text
2026-10-28T11:17:04.485Z Executing user build command: npm run build
2026-10-28T11:17:04.887Z > build
2026-10-28T11:17:04.887Z > npm --prefix web run build
2026-10-28T11:17:05.051Z > web@0.0.0 build
2026-10-28T11:17:05.051Z > vite build
2026-10-28T11:17:05.055Z sh: 1: vite: not found
2026-10-28T11:17:05.083Z Failed: error occurred while running build command
```

---

## 2. Root Cause Analysis

1. **Monorepo Directory Isolation**: The project repository contains both the Python library at the root (`pyproject.toml`) and the modern React documentation website inside the `web/` subdirectory (`web/package.json`).
2. **Missing Workspace Definition in Root `package.json`**:
   The root `package.json` only declared scripts without declaring `workspaces: ["web"]`. Consequently, when Cloudflare's dependency detection ran `bun install` or `npm install` at the repo root, package managers treated the root as an isolated package with zero dependencies, omitting `web/node_modules`.
3. **Execution Failure**: When `npm --prefix web run build` triggered `vite build`, the shell could not locate the `vite` executable in `web/node_modules/.bin/`.

---

## 3. Resolution Applied

1. **Declared npm Workspaces**:
   Updated the root `package.json` to explicitly register `web` as a workspace:
   ```json
   {
     "name": "ziptext-repo",
     "private": true,
     "workspaces": [
       "web"
     ],
     "scripts": {
       "prebuild": "npm --prefix web install",
       "build": "npm --prefix web install && npm --prefix web run build",
       "dev": "npm --prefix web run dev",
       "preview": "npm --prefix web run preview"
     }
   }
   ```
2. **Automated Prebuild Hook**:
   Added a `prebuild` lifecycle hook and chained `npm --prefix web install && npm --prefix web run build`. Regardless of whether Cloudflare runs the build from the repository root or from within the `web` workspace, all web dependencies are guaranteed to be installed before `vite build` executes.
3. **Tested & Verified**:
   Ran `npm run build` from root; verified both `prebuild` and `build` succeed, transforming 1,968 modules into `web/dist` in 25.12s.

---

## 4. Cloudflare Pages Configuration Guide

For deployment in the Cloudflare Pages Dashboard:
- **Build command**: `npm run build`
- **Build output directory**: `web/dist` (or set **Root directory** to `web` with output `dist`)
- **Environment variables**: `NODE_VERSION = 20`
