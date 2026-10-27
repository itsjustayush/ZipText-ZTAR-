# Zip Text — ZTAR Model Lab (v0.1.0)

**Zip Text Adaptive Representation (ZTAR)** is a storage-independent research framework designed to represent files as compact, reversible textual data while prioritizing compression efficiency, fast reconstruction, and bounded memory usage.

---

## 1. Core Objectives & Priorities

Zip Text converts files of virtually any format—media, documents, source code, and arbitrary binary data—into a structured, portable representation (`.ztxt`) that guarantees exact byte-for-byte reconstruction in lossless mode.

- **Exact Reconstruction**: Strict invariant $\operatorname{Decode}(\operatorname{Encode}(X)) = X$ verified by whole-file and per-chunk SHA-256 digests.
- **Storage Efficiency**: Minimize the total serialized representation size (including headers, indices, and text-encoding overhead).
- **Fast Decoding**: Streamlined chunk-by-chunk reconstruction with minimal transformation overhead.
- **Low Working Memory**: Decodes in bounded memory chunks rather than loading entire multi-gigabyte files into RAM.
- **Storage Independence**: Operates entirely locally without cloud services, external databases, or network calls.
- **Adaptive Codec Selection**: Dynamically benchmarks candidate codecs (`raw`, `zlib`, `bz2`, `lzma`, `lz4`) on each chunk and selects the optimal representation.

---

## 2. Container Architecture

A `.ztxt` container consists of:
1. **Container Header & Magic**: Standard identifier and container versioning.
2. **Metadata Manifest**: Filename, uncompressed byte size, whole-file SHA-256 hash, chunk size, total chunk count, and default text encoding.
3. **Independently Decodable Chunks**: Each chunk record stores its index, raw size, compressed size, active codec, text encoding, and chunk SHA-256 digest, followed by the wrapped text payload.
4. **Verification & Atomic Publish**: The decoder reconstructs chunk-by-chunk, verifies chunk integrity, evaluates whole-file hash equality, and atomically publishes the target file.

---

## 3. Installation

From the project root:

```bash
python -m pip install -e ".[all]"
```

---

## 4. CLI Usage

### Generate Synthetic Test Corpus

Generates 9 diverse test files covering text, PPM image, PDF, JPEG (smooth gradient & noisy), MP4 video, and random binary data:

```bash
python -m ziptext fixtures --output fixtures --size-mb 4
```

### Run Benchmark Comparison Matrix

Executes the full 108-case comparison matrix across 6 policies (`raw`, `zlib`, `bz2`, `lzma`, `lz4`, `auto`) and 2 chunk sizes (256 KiB and 1 MiB):

```bash
python -m ziptext matrix fixtures --output-dir results/matrix
```

Reports are automatically generated in both structured JSON (`results/matrix/matrix_results.json`) and spreadsheet-friendly CSV (`results/matrix/matrix_results.csv`).

### Encode a File

```bash
python -m ziptext encode input.mp4 output.ztxt --codec auto --chunk-size 1048576
```

### Decode and Verify

```bash
python -m ziptext decode output.ztxt recovered.mp4
```

### Inspect Container Manifest

```bash
python -m ziptext info output.ztxt
```

### Verify Integrity Without Writing

```bash
python -m ziptext verify output.ztxt
```

### Run Test Suite

```bash
python -m pytest -q
```

---

## 5. Initial Benchmark Findings (v0.1.0)

Using the adaptive mode with 1 MiB chunks and Base85 text encoding:

| Test File | Original Size | Zip Text Size | Size Change | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Repetitive text** | 2.00 MiB | 1.43 KiB | -99.9% | Exploit repetitive linguistic patterns |
| **Source-like text** | 2.00 MiB | 1.44 KiB | -99.9% | High structural code redundancy |
| **Uncompressed PPM** | 1.69 MiB | 187.3 KiB | -89.2% | High 2D pixel correlation |
| **Synthetic PDF** | 8.7 KiB | 7.0 KiB | -20.0% | Structural streams compressed |
| **Gradient JPEG** | 41.6 KiB | 42.5 KiB | +2.1% | Already compressed; minimal text overhead |
| **Noisy JPEG** | 198.8 KiB | 265.4 KiB | +33.5% | High entropy; Base85 text expansion |
| **Synthetic MP4** | 302.4 KiB | 371.6 KiB | +22.9% | Pre-compressed media stream payload |
| **Random binary** | 1.00 MiB | 1.33 MiB | +33.4% | Incompressible data; clean Base85 expansion |

- **Exact Round Trips**: 108 / 108 cases verified byte-for-byte.
- **Lossless Verification**: 100% SHA-256 match rate across all test runs.

---

## 6. Project Layout

```
ZipText(ZTAR)/
├── pyproject.toml              # Build configuration and dependencies
├── README.md                   # Project overview and CLI documentation
├── docs/
│   └── FINDINGS.md             # Comprehensive research report and analysis
├── ziptext/
│   ├── __init__.py             # Public API and version
│   ├── __main__.py             # python -m ziptext entry point
│   ├── cli.py                  # CLI argument parsing and commands
│   ├── container.py            # .ztxt streaming parser, writer, format specification
│   ├── engine.py               # Core adaptive encoding and decoding engine
│   ├── fixtures.py             # Synthetic test corpus generator (9 media types)
│   ├── matrix.py               # Benchmark matrix runner (108 cases, CSV & JSON)
│   ├── text_encodings.py       # Base85 and Base64 text encoding adapters
│   ├── utils.py                # SHA-256 hashing, memory tracking, unit formatters
│   └── codecs/
│       ├── __init__.py
│       ├── base.py             # Codec interface and registry
│       ├── raw.py              # Identity pass-through
│       ├── zlib_codec.py       # Deflate/zlib
│       ├── bz2_codec.py        # Burrows-Wheeler bzip2
│       ├── lzma_codec.py       # LZMA2 / XZ
│       └── lz4_codec.py        # High-speed LZ4 frame codec
├── tests/                      # 35 unit tests
└── results/
    └── matrix/                 # Benchmark output artifacts (JSON and CSV)
```
