# Zip Text (ZTAR) — Incident & Error Register

This directory maintains a comprehensive, permanent record of every failure, bug, exception, and edge-case encountered during manual testing, AI-driven development, and automated test suite execution.

---

## 1. Error Taxonomy & Severity Levels

| Severity | Definition | SLA / Handling |
| :--- | :--- | :--- |
| **P0 — Critical** | Data corruption, unrecoverable data loss, or silent failure where decoded bytes differ from original without alert. | Immediate fix, blocker for any release. |
| **P1 — High** | Crash during encode/decode, unhandled exception in core pipeline, or inability to parse valid standard file formats. | Resolved within same minor release. |
| **P2 — Medium** | User experience trap, extension mismatch confusion, build configuration collision, or test harness flaw. | Resolved with defensive safeguards & alerts. |
| **P3 — Low** | Syntax formatting, typing import oversight, CLI argument omission, or platform-specific shell quirk. | Addressed immediately upon detection. |

---

## 2. Historical Incident Master Ledger

| Incident ID | Severity | Phase | Subsystem | Brief Summary | Status |
| :--- | :---: | :---: | :--- | :--- | :---: |
| [`ERR-001`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-001_extension_mismatch_failure.md) | **P2** | Manual Testing | Engine / Container | User decoded JSON container into `.jpg` filename; hash check failed & viewer broke. | **RESOLVED** |
| [`ERR-002`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-002_missing_any_typing_import.md) | **P3** | Unit Testing | Engine (`engine.py`) | `NameError: name 'Any' is not defined` during type evaluation. | **RESOLVED** |
| [`ERR-003`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-003_missing_union_typing_import.md) | **P3** | Unit Testing | Fixtures (`fixtures.py`) | `NameError: name 'Union' is not defined` during synthetic corpus generation. | **RESOLVED** |
| [`ERR-004`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-004_missing_optional_typing_import.md) | **P3** | CLI Testing | CLI (`cli.py`) | `NameError: name 'Optional' is not defined` during argument setup. | **RESOLVED** |
| [`ERR-005`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-005_pillow_bounding_box_inverted_coords.md) | **P1** | Synthetic Gen | Fixtures (`fixtures.py`) | `ValueError: y1 must be greater than or equal to y0` in Pillow draw. | **RESOLVED** |
| [`ERR-006`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-006_setuptools_flat_layout_collision.md) | **P2** | Environment | Packaging (`pyproject.toml`) | `setuptools` build collision with non-package `results/` folder. | **RESOLVED** |
| [`ERR-007`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-007_missing_integrity_error_import.md) | **P2** | CLI Testing | CLI (`cli.py`) | `NameError: name 'IntegrityError' is not defined` on tampered file. | **RESOLVED** |
| [`ERR-008`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-008_corrupt_payload_mutating_manifest.md) | **P2** | Integration | Tests (`test_corruption.py`)| Mutating manifest lines caused header parse error rather than chunk error. | **RESOLVED** |
| [`ERR-009`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-009_rectangle_loop_inverted_coordinates.md) | **P1** | Fixtures | Script (`make_all_categories.py`) | `ValueError: x1 must be greater than or equal to x0` when loop crossed center. | **RESOLVED** |
| [`ERR-010`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-010_powershell_operator_syntax_collision.md) | **P3** | Execution | PowerShell Shell | `&&` operator syntax error in Windows PowerShell; required `;`. | **RESOLVED** |
| [`ERR-011`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-011_missing_text_encoding_registry_import.md) | **P3** | Benchmarks | Harness (`four_tier_eval.py`) | `ImportError: cannot import name 'TextEncodingRegistry'` during benchmark run. | **RESOLVED** |
| [`ERR-012`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-012_test_assertion_omitted_new_codecs.md) | **P2** | Unit Testing | Test Suite (`test_engine.py`) | Assertion failed when `auto` mode chose superior newly added `brotli` codec. | **RESOLVED** |
| [`ERR-013`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-013_github_pre_receive_large_file_rejection.md) | **P2** | Deployment | Git VCS / GitHub Push | `resources/archive.zip` (423 MB) in unpushed commit history blocked push. | **RESOLVED** |
| [`ERR-014`](file:///e:/Projects/ZipText(ZTAR)/errors/ERR-014_cloudflare_pages_vite_not_found.md) | **P2** | Deployment | Cloudflare Pages CI/CD | `vite: not found` during build due to missing monorepo workspace dependencies. | **RESOLVED** |

---

## 3. Protocol for Adding New Errors

Whenever a test fails, an exception is thrown, or unexpected behavior is observed:
1. Assign the next sequential ID: `ERR-XXX`.
2. Create `errors/ERR-XXX_<descriptor>.md`.
3. Include:
   - **Incident Summary**
   - **Reproduction Steps**
   - **Exact Stack Trace / Error Output**
   - **Root Cause Analysis**
   - **Fix Applied**
   - **Regression Prevention & Testing Strategy**
4. Update this master table.
