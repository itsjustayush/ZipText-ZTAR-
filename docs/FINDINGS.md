# Zip Text (ZTAR) Lab v0.1.0 — Initial Research Findings

**Author:** Zip Text Research Team  
**Evaluation Date:** October 2026  
**Artifacts:** [`matrix_results.json`](file:///e:/Projects/ZipText(ZTAR)/results/matrix/matrix_results.json), [`matrix_results.csv`](file:///e:/Projects/ZipText(ZTAR)/results/matrix/matrix_results.csv)

---

## 1. Executive Summary

Zip Text Lab v0.1.0 establishes the empirical baseline for the **Zip Text Adaptive Representation (ZTAR)** framework. ZTAR evaluates how diverse digital assets can be represented as structured, reversible text containers (`.ztxt`) with bounded memory consumption and strict mathematical fidelity.

### Verification Milestone
- **108 / 108 Exact Round Trips**: Every single encoded and reconstructed file matched its original byte-for-byte with identical SHA-256 digests.
- **35 Unit Tests Passed**: Full coverage across codecs, chunk boundaries, tamper detection, and CLI flows.
- **Test Matrix Dimensions**: 9 media types $\times$ 6 encoding policies (`raw`, `zlib`, `bz2`, `lzma`, `lz4`, `auto`) $\times$ 2 chunk sizes (256 KiB, 1 MiB).

---

## 2. Benchmark Results & Data Analysis

The table below summarizes results using the **Adaptive (`auto`) policy** at the **1 MiB chunk size** with **Base85 text encoding**:

| Test File | Format | Original Size | Encoded `.ztxt` Size | Size Delta | Active Codec | Preservation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`repetitive_text.txt`** | Text | 2.00 MiB | 2.18 KiB | **-99.9%** | `lzma` | Exact SHA-256 |
| **`source_like.txt`** | Code | 2.00 MiB | 2.53 KiB | **-99.9%** | `lzma` | Exact SHA-256 |
| **`uncompressed.ppm`** | Image | 1.69 MiB | 125.44 KiB | **-92.7%** | `lzma` | Exact SHA-256 |
| **`synthetic.pdf`** | Document | 8.69 KiB | 1.14 KiB | **-86.9%** | `zlib` | Exact SHA-256 |
| **`gradient.jpg`** | Media | 10.13 KiB | 12.87 KiB | **+27.0%** | `auto/zlib` | Exact SHA-256 |
| **`synthetic.png`** | Media | 6.22 KiB | 7.82 KiB | **+25.7%** | `auto/zlib` | Exact SHA-256 |
| **`synthetic.mp4`** | Video | 302.40 KiB | 388.37 KiB | **+28.4%** | `auto/zlib` | Exact SHA-256 |
| **`noisy.jpg`** | Media | 352.94 KiB | 453.30 KiB | **+28.4%** | `auto/raw` | Exact SHA-256 |
| **`random.bin`** | Binary | 1.00 MiB | 1.28 MiB | **+28.3%** | `auto/raw` | Exact SHA-256 |

---

## 3. Key Observations & Interpretation

### 3.1. Structure-Aware Redundancy Elimination
Files with significant internal redundancy (such as repetitive prose, structured code templates, and uncompressed pixel maps) experience massive size reductions:
- Text and source code shrank by **99.9%**, compressing 2 MiB down to ~2 KiB.
- The uncompressed 768$\times$768 RGB image (`uncompressed.ppm`) dropped by **92.7%**, demonstrating that spatial pixel continuity is effectively captured by stream compressors prior to text serialization.

### 3.2. The Cost of Reversible Text Serialization
When data is already compressed (e.g. JPEG, PNG, MP4) or has maximum Shannon entropy (e.g. `random.bin`), standard compression algorithms cannot reduce entropy further.
In such cases:
- The adaptive policy identifies that compression yields negligible or negative gains and switches to `raw` pass-through.
- Base85 encoding maps 4 binary bytes into 5 printable ASCII characters (a theoretical minimum expansion of $1.25\times$, or $+25\%$).
- Accounting for container metadata (manifest JSON, chunk headers, chunk checksums, line breaks), the total file expansion on incompressible assets settles at **$+28.3\%$ to $+28.5\%$**.
- **Crucial Rule Established**: If the destination environment natively supports raw binary containers, text encoding can be omitted to avoid this $+25\%$ inflation.

### 3.3. Chunk Size Dynamics (256 KiB vs 1024 KiB)
- **1024 KiB chunks** yielded superior compression on larger files (`repetitive_text.txt` achieved 2.18 KiB at 1024 KiB vs 6.33 KiB at 256 KiB) because LZMA dictionary history is maintained across longer continuous streams.
- **256 KiB chunks** reduced working memory footprint and decreased per-chunk latency, making it optimal for resource-constrained or streaming-first environments.

---

## 4. Current Limitations

1. **Framework, Not Yet an Original Codec**:
   v0.1.0 is an adaptive container and evaluation orchestrator using established codecs (`zlib`, `bz2`, `lzma`, `lz4`). It does not yet incorporate custom mathematical frequency or transform representations.
2. **Text Overhead on Pre-Compressed Media**:
   Representing already-compressed media (MP4, JPEG) in text inevitably incurs Base85 expansion.
3. **No Encryption**:
   Base85 and Base64 are data serialization encodings, not cryptographic primitives.
4. **Independent Chunks vs Global Dictionary**:
   Because chunks are decodable independently, cross-chunk redundancy is not shared in v0.1.0.

---

## 5. Next Research Directions & Roadmap

1. **Cross-Chunk Deduplication (Content-Defined Chunking)**:
   Implement rolling hash chunking (e.g. Rabin or FastCDC) to detect and deduplicate identical blocks across multi-file corpora.
2. **Novel Mathematical Representations**:
   Research context-mixing, predictive arithmetic coding, and lightweight transform-domain representations specifically targeted at structured datasets.
3. **Hybrid Binary/Text Container Profiles**:
   Introduce a native binary container profile (`.zbin`) alongside the portable text container (`.ztxt`) to eliminate the Base85 expansion overhead when raw binary transport is viable.
4. **Real-World Empirical Baselines**:
   Expand the benchmark harness to evaluate multi-gigabyte heterogeneous real-world corpora (Linux tarballs, PDF libraries, game assets).
