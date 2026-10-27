# Zip Text (ZTAR) Model Summary — v0.1.0

**Version Tag:** `v0.1.0`  
**Status:** Runnable Research Prototype  
**Date:** October 2026  
**Primary Engine:** Python 3.9+ (`ziptext-lab`)

---

## 1. Overview & Framework Definition

**Zip Text Adaptive Representation (ZTAR)** is a storage-independent system designed to represent digital files as compact, reversible textual data while prioritizing compression efficiency, fast reconstruction, and low memory usage.

### Optimization Target
$$\min_{\mathcal R} \left( S_{\mathcal R} + \lambda D_{\mathcal R} + \mu M_{\mathcal R} \right)$$

Where:
- $S_{\mathcal R}$ = Total representation size (including headers, indices, and Base85 text serialization overhead).
- $D_{\mathcal R}$ = Decoding latency.
- $M_{\mathcal R}$ = Peak working memory (RSS).
- $\lambda, \mu$ = Optimization weights balancing speed and memory bounds.

For lossless mode, the strict preservation invariant is:
$$\operatorname{Decode}(\operatorname{Encode}(X)) = X$$

---

## 2. Architectural Pipeline

1. **Input File Intake**: Arbitrary binary data, media files, or plain text.
2. **Chunk Partitioning**: Slices input into bounded chunks ($C_{\text{size}} \in \{256\text{ KiB}, 1024\text{ KiB}\}$).
3. **Adaptive Transformation Engine**:
   - Tests candidate compression algorithms: `raw`, `zlib`, `bz2`, `lzma`, `lz4`.
   - Computes candidate serialized text length under Base85 encoding.
   - Dynamically selects the smallest serialized representation per chunk.
4. **Structured Container Serialization (`.ztxt`)**:
   - Manifest header with metadata and whole-file SHA-256.
   - Chunk index and independently decodable chunk blocks.
   - Chunk-level SHA-256 checksums.
5. **Lossless Decoder & Verification**:
   - Reads container line-by-line with bounded RAM.
   - Decompresses and verifies each chunk against its chunk digest.
   - Validates running whole-file SHA-256 before publishing target output.

---

## 3. Operating Modes

- **Zip Text Exact (Default)**: Strict lossless byte-for-byte reconstruction with whole-file and chunk SHA-256 validation.
- **Zip Text Media (Roadmap)**: Format-aware transformations for visual/auditory media assets.
- **Zip Text Compact (Roadmap)**: Explicit lossy compression mode when users accept reduced fidelity for maximum compactness.

---

## 4. Benchmark Validation in v0.1.0

- **108 / 108 Exact Round Trips Verified**: 100% byte-for-byte fidelity across 9 synthetic fixtures.
- **35 Passing Unit Tests**: Codecs, chunk boundaries, tamper resistance, and CLI execution.
- **Detailed Findings**: Refer to [`FINDINGS.md`](file:///e:/Projects/ZipText(ZTAR)/reports/v0/v0.1.0/FINDINGS.md) and [`matrix_results.csv`](file:///e:/Projects/ZipText(ZTAR)/reports/v0/v0.1.0/matrix_results.csv).
