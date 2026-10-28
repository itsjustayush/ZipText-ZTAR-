# Incident Report: ERR-015 — Cloudflare Wrangler Monorepo Workspace & Assets Deploy Failure

- **Incident ID**: `ERR-015`
- **Severity**: **P2 (Medium)**
- **Subsystem**: Deployment / Cloudflare CI/CD / Wrangler 4
- **Status**: **RESOLVED**
- **Date**: 2026-10-28

---

## 1. Incident Summary

Following the successful build of the documentation website, Cloudflare's deployment stage executed `npx wrangler deploy` at the repository root. Wrangler 4.154.0 halted deployment with two cascading errors:

```text
2026-10-28T12:46:55.136Z Executing user deploy command: npx wrangler deploy
2026-10-28T12:47:09.698Z ✘ [ERROR] The Cloudflare application detection logic has been run in the root of a workspace instead of targeting a specific project. Change your working directory to one of the applications in the workspace and try again.
2026-10-28T12:47:09.811Z Failed: error occurred while running deploy command
```

---

## 2. Root Cause Analysis

1. **Wrangler Monorepo Detection**: The root `package.json` had `"workspaces": ["web"]`. Wrangler 4 detects the presence of npm workspaces at the invocation root and requires explicit project targeting (or running from inside the app directory).
2. **Missing Static Assets Binding**: In modern Cloudflare deployments invoking `wrangler deploy`, static sites require explicit asset directory configuration (`[assets] directory = "web/dist"`) in `wrangler.toml` in addition to `pages_build_output_dir`. Without this block, Wrangler assumes a Worker script (`src/index.ts`) is missing.

---

## 3. Resolution Applied

1. **Removed `workspaces` from Root `package.json`**:
   Because `prebuild` and `build` scripts already use `--prefix web` (`npm --prefix web install && npm --prefix web run build`), npm workspaces was redundant and triggered Wrangler's root workspace check.
2. **Added `[assets]` Block in [wrangler.toml](file:///e:/Projects/ZipText(ZTAR)/wrangler.toml)**:
   ```toml
   name = "ziptext"
   compatibility_date = "2024-01-01"
   pages_build_output_dir = "web/dist"

   [assets]
   directory = "web/dist"
   ```
3. **Verification**:
   Executed `npx wrangler deploy --dry-run` from repository root:
   - Successfully read all 8 static assets from `web\dist`.
   - Exited with code 0.
