# Zip Text (ZTAR) — v0.3.0 ASPD Benchmark & Information-Theoretic Evaluation

**Date:** October 2026  
**Version:** `v0.3.0`  
**Test Harness:** Automated Python Benchmark Suite & Canterbury Corpus Evaluator

---

## 1. Information-Theoretic Foundations

The Shannon entropy limit of a discrete memoryless source $X$ is defined as:
$$H(X) = -\sum_{i=0}^{255} p(x_i) \log_2 p(x_i) \quad \text{[bits/byte]}$$

For multi-byte physical signals (such as 16-bit acoustic waves or 24-bit color rasters), symbol occurrences are heavily correlated with adjacent samples. Standard dictionary algorithms operate on individual byte sequences, failing to bridge multi-byte strides.

### The ASPD Solution:
1. **Stride Differentials ($\text{Delta}_k$):** Replaces raw values with finite differences $d_i = (x_i - x_{i-k}) \bmod 256$, collapsing smooth waveforms into Laplacian distributions centered tightly at zero.
2. **Byte-Plane Deinterleaving ($\text{Plane}_k$):** Transposes interleaved multi-byte streams into independent significance planes:
   $$\text{Plane}_0 = [x_0, x_k, x_{2k}, \dots], \quad \text{Plane}_1 = [x_1, x_{k+1}, x_{2k+1}, \dots]$$
   Isolates high-order sign/magnitude bits (which exhibit near-zero entropy) from lower-order noise bits.

---

## 2. Empirical Entropy Measurements

| Asset / Corpus | Raw 0-Order Entropy | Post-Transform Entropy | Optimal Transform | Entropy Delta ($\Delta H$) |
| :--- | :---: | :---: | :---: | :---: |
| **`audio.wav` (16-bit PCM)** | 7.703 bpb | **6.409 bpb** | `delta2` / `pdelta2` | **-1.294 bpb (-16.8%)** |
| **`graphic.bmp` (24-bit RGB)**| 2.538 bpb | **1.392 bpb** | `delta3` | **-1.146 bpb (-45.2%)** |
| **`sample_signal.bin` (Wave)**| 7.214 bpb | **3.891 bpb** | `pdelta2` | **-3.323 bpb (-46.1%)** |
| **`alice29.txt` (English)** | 4.568 bpb | 5.064 bpb (Rejected) | `none` (Gated) | $0.000$ bpb (Safe) |
| **`kennedy.xls` (Spreadsheet)**| 3.573 bpb | 5.582 bpb (Rejected) | `none` (Gated) | $0.000$ bpb (Safe) |
| **`sports.csv` (CSV Data)** | 4.812 bpb | 5.120 bpb (Rejected) | `none` (Gated) | $0.000$ bpb (Safe) |

---

## 3. Comparative Compaction Benchmarks: v0.2.0 vs v0.3.0

All measurements reflect exact container files on disk (including headers, manifests, chunk checksums, and container framing):

| Dataset Item | Original Bytes | v0.2.0 Size (`.zbin`) | v0.3.0 Size (`.zbin`) | Relative Size Reduction | Winning Algorithm |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`audio.wav`** | 88,244 B | 4,527 B | **2,777 B** | **-38.65% smaller** | `brotli+pdelta2` |
| **`sample_signal.bin`** | 20,000 B | 2,148 B | **1,284 B** | **-40.22% smaller** | `zlib+pdelta2` |
| **`graphic.bmp`** | 120,054 B | 843 B | **843 B** | **0.00% (Identical)** | `brotli` |
| **`alice29.txt`** | 152,089 B | 46,750 B | **46,750 B** | **0.00% (Identical)** | `brotli` |
| **`kennedy.xls`** | 1,029,744 B | 130,412 B | **130,412 B** | **0.00% (Identical)** | `brotli` |
| **`sum` (SPARC binary)** | 38,240 B | 12,890 B | **12,890 B** | **0.00% (Identical)** | `brotli` |

### Key Takeaways:
1. **Major Gains on Signals:** On structured multi-byte signals, ASPD slashes container footprint by **38% to 40%** over the already optimized v0.2.0 baseline.
2. **Zero Degradation on General Text & Binaries:** For unstructured text, pre-compressed files, and databases, the dual-stage gating mechanism detects that differential transforms do not improve entropy or size, gracefully falling back to baseline `none`.
3. **100% Bitwise Reversible:** Every decoded output matches original SHA-256 digests bit-for-bit.
