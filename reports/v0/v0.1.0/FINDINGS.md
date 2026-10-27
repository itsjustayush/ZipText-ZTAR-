# Zip Text (ZTAR) Research Findings — v0.1.0

**Version Tag:** `v0.1.0`  
**Execution Date:** October 2026  
**Artifacts Attached:** [`matrix_results.json`](file:///e:/Projects/ZipText(ZTAR)/reports/v0/v0.1.0/matrix_results.json), [`matrix_results.csv`](file:///e:/Projects/ZipText(ZTAR)/reports/v0/v0.1.0/matrix_results.csv)

---

## 1. Experimental Setup

The benchmark harness evaluated 9 diverse synthetic fixtures representing distinct digital media characteristics:
- Repetitive text (2.00 MiB)
- Source-like code text (2.00 MiB)
- Uncompressed PPM image (1.69 MiB, 768$\times$768 RGB)
- Synthetic PDF document (8.69 KiB)
- Synthetic PNG image (6.22 KiB)
- Gradient JPEG image (10.13 KiB)
- Noisy JPEG image (352.94 KiB)
- Synthetic MP4 video container (302.40 KiB)
- Random high-entropy binary (1.00 MiB)

Each fixture was evaluated across:
- **6 Encoding Policies**: `raw`, `zlib`, `bz2`, `lzma`, `lz4`, `auto` (adaptive selection)
- **2 Chunk Sizes**: `256 KiB` and `1024 KiB`
- **Total Test Cases**: $9 \times 6 \times 2 = 108$ test runs.

---

## 2. Experimental Results (1 MiB Chunk Size, Auto Policy, Base85)

| Test File | Original Size | Encoded `.ztxt` Size | Size Delta | Selected Codec | Reconstruction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`repetitive_text.txt`** | 2.00 MiB | 2.18 KiB | **-99.9%** | `lzma` | Verified Byte-Exact |
| **`source_like.txt`** | 2.00 MiB | 2.53 KiB | **-99.9%** | `lzma` | Verified Byte-Exact |
| **`uncompressed.ppm`** | 1.69 MiB | 125.44 KiB | **-92.7%** | `lzma` | Verified Byte-Exact |
| **`synthetic.pdf`** | 8.69 KiB | 1.14 KiB | **-86.9%** | `zlib` | Verified Byte-Exact |
| **`synthetic.png`** | 6.22 KiB | 7.82 KiB | **+25.7%** | `auto/zlib` | Verified Byte-Exact |
| **`gradient.jpg`** | 10.13 KiB | 12.87 KiB | **+27.0%** | `auto/zlib` | Verified Byte-Exact |
| **`synthetic.mp4`** | 302.40 KiB | 388.37 KiB | **+28.4%** | `auto/zlib` | Verified Byte-Exact |
| **`noisy.jpg`** | 352.94 KiB | 453.30 KiB | **+28.4%** | `auto/raw` | Verified Byte-Exact |
| **`random.bin`** | 1.00 MiB | 1.28 MiB | **+28.3%** | `auto/raw` | Verified Byte-Exact |

---

## 3. Analysis & Key Insights

1. **Massive Compression on Redundant Data**:
   Prose, repetitive structured code, and uncompressed pixel representations reduced by 86% to 99.9%. Spatial correlation in uncompressed images is effectively compressed prior to text serialization.
2. **The Base85 Text Expansion Cost**:
   For assets that are already compressed (JPEG, PNG, MP4) or incompressible (random binary), compression yields negative return. The adaptive policy safely selects `raw` pass-through, resulting in a predictable $+28.3\%$ to $+28.5\%$ expansion (Base85 transforms 4 binary bytes to 5 ASCII chars = $+25\%$, plus container metadata and checksums).
3. **Chunk Size Trade-Offs**:
   - `1024 KiB` chunks achieve superior compression ratios for larger files due to wider LZMA dictionary context.
   - `256 KiB` chunks maintain significantly lower working memory footprint and lower per-chunk decoding latency.

---

## 4. Roadmap to v0.2.0 & Beyond

1. **Deduplication Engine**: Rolling hash chunking (FastCDC) to eliminate duplicate chunks across files.
2. **Binary Container Format (`.zbin`)**: Provide zero-overhead binary packaging when text serialization is not required.
3. **Novel Mathematical Representations**: Experiment with context-mixing and specialized frequency-domain integer transforms.
