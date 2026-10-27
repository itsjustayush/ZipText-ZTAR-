# Zip Text (ZTAR) — Reports Registry

This directory stores all historical and active benchmark reports, model summaries, and experimental evaluation findings for the Zip Text Adaptive Representation (ZTAR) engine.

---

## Directory Hierarchy & Versioning Standard

Reports are organized strictly by **major version folders** (`v0`, `v1`, `v2`, `v3`, ...), and subdivided into **semantic patch/release folders** (`v<major>.<minor>.<patch>`):

```
reports/
├── README.md                      # Reports registry, schema definitions & conventions
└── v0/                            # Major version: v0.x.x (Research Prototypes & Baselines)
    └── v0.1.0/                    # Patch release: v0.1.0 (Initial baseline prototype)
        ├── SUMMARY.md             # Theoretical model summary & framework status
        ├── FINDINGS.md            # Empirical findings & analysis for this release
        ├── matrix_results.json    # Complete JSON dataset for all test matrix cases
        └── matrix_results.csv     # Spreadsheet-friendly CSV matrix report
```

### Future Versions Structure:
- `v0/`: Prototype lab phase (v0.1.0 baseline, v0.2.0 cross-chunk deduplication, v0.3.0 binary containers).
- `v1/`: First production release with integrated novel transform representations.
- `v2/`: Distributed & streaming cluster profiles.
- `v3/`: Advanced neural/context-mixing transform engines.

---

## Standard Artifacts in Each Version Folder

Every patch release folder must contain:
1. `SUMMARY.md`: High-level executive overview, architectural changes, and optimization target weights ($\lambda, \mu$).
2. `FINDINGS.md`: Comprehensive qualitative and quantitative interpretation of benchmark results.
3. `matrix_results.json`: Full machine-readable dataset of every test combination.
4. `matrix_results.csv`: Standardized tabular format for spreadsheet and statistical analysis.

---

## Active Releases

| Version | Release Date | Exact Round-Trips | Unit Tests | Notes |
| :--- | :--- | :--- | :--- | :--- |
| [`v0.1.0`](file:///e:/Projects/ZipText(ZTAR)/reports/v0/v0.1.0/) | 2026-10-27 | **108 / 108** | **35 Passed** | Initial baseline across 9 media types, 6 codecs, 2 chunk sizes |
