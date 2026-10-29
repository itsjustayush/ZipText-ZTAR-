# ZTAR Container Format v1 Wire Specification
**Version:** 1.0 (Implementing ZTAR Profile 0.3.0)  
**Status:** Standards-Track Specification  
**Authors:** ZipText Research & Engineering Team  
**Date:** October 2026  

---

## 1. Abstract & Scope

The **Zip Text Adaptive Representation (ZTAR)** specification defines a dual-profile, chunked, lossless container format designed for safe data transport, auditable interchange, and adaptive compression orchestration.

ZTAR provides two companion serialization profiles:
1. **Portable Text Profile (`.ztxt`)**: A human-readable, ASCII-armored (RFC 1924 Base85) container intended for text-restricted environments such as JSON payloads, message queues, API webhooks, and auditable storage manifests.
2. **High-Performance Binary Profile (`.zbin`)**: A low-overhead binary container designed for streaming dense media, sensor waveforms, and high-throughput network transport with zero text expansion.

---

## 2. Fundamental Invariants

All conformant ZTAR implementations MUST uphold the following invariants:

1. **Strict Bit-for-Bit Identity**:
   $$\operatorname{Decode}(\operatorname{Encode}(X)) \equiv X$$
   Every decoded byte stream MUST cryptographically match the original input:
   $$\operatorname{SHA-256}(\operatorname{Decoded}) = \operatorname{SHA-256}(\operatorname{Original})$$
2. **Chunk-Level Integrity Verification**:
   Each chunk payload MUST be validated against its declared cryptographic hash prior to staging or concatenation.
3. **Atomic Reconstruction**:
   Implementations MUST decode into temporary staging files and perform atomic replacement only after the complete file size and whole-file SHA-256 checksum have verified.
4. **Bounded Memory Execution**:
   Sequential decoders MUST operate within bounded memory windows proportional to the declared `chunk_size` rather than buffering unbounded inputs into memory.

---

## 3. Container Profiles & Wire Formats

### 3.1 Portable Text Profile (`.ztxt`)

The `.ztxt` profile is an ASCII 7-bit clean document structured as follows:

```
-----BEGIN ZIPTEXT CONTAINER v0.3.0-----
{"version":"0.3.0","filename":"data.csv","file_size":1048576,...}
-----END MANIFEST-----
-----BEGIN CHUNK 0 raw_size=1048576 compressed_size=241500 codec=brotli encoding=base85 sha256=e3b0c442...-----
s4IAAAAAAAAA+2Xw02gAQBqD0m1V8k...
[wrapped at 76 characters per line]
...
-----END CHUNK 0-----
-----END ZIPTEXT CONTAINER-----
```

#### Framing Rules:
1. **Magic Header Line**:
   `-----BEGIN ZIPTEXT CONTAINER v{version}-----`  
   Conformant parsers MUST verify the version string against supported versions (`0.1.0`, `0.2.0`, `0.3.0`).
2. **Manifest Block**:
   Begins on the line immediately following the magic header and terminates with `-----END MANIFEST-----`. Contains a valid UTF-8 JSON object (minified or formatted).
3. **Chunk Header Line**:
   `-----BEGIN CHUNK {index} raw_size={R} compressed_size={C} codec={codec} encoding={encoding} sha256={H}-----`
   - `index`: 0-indexed contiguous integer sequence (`0, 1, 2, ...`). Any gap or duplicate MUST raise a `ContainerFormatError`.
   - `raw_size`: Uncompressed chunk size in bytes (MUST be $\le 64\text{ MiB}$).
   - `compressed_size`: Byte length of compressed payload before Base85 armoring.
   - `codec`: Codec identifier string (e.g. `brotli`, `zstd+pdelta2`, `raw`).
   - `encoding`: Text serialization armor (`base85` or `base64`).
   - `sha256`: Hexadecimal SHA-256 checksum of the uncompressed `raw_size` bytes.
4. **Armored Chunk Payload**:
   Base85 encoded text wrapped at 76 characters per line (`\n` line delimiters).
5. **Chunk Trailer Line**:
   `-----END CHUNK {index}-----`
6. **Container Trailer Line**:
   `-----END ZIPTEXT CONTAINER-----`

---

### 3.2 High-Performance Binary Profile (`.zbin`)

The `.zbin` profile eliminates text serialization overhead by storing binary compressed chunks directly.

#### Binary Layout:

| Offset / Field | Type | Description |
| :--- | :--- | :--- |
| `0x00..0x06` | `ASCII[7]` | Magic header: `ZBIN03\n` |
| `0x07..0x0A` | `uint32_be` | Manifest length in bytes ($L_M$) |
| `0x0B..0x0B+L_M` | `UTF-8` | JSON Manifest payload |
| **Repeated Chunks** | | Contiguous binary chunk records |
| `Trailer` | `ASCII[8]` | Magic trailer: `ENDBIN03` |

#### Binary Chunk Record Layout:

| Field | Size | Type | Value / Constraint |
| :--- | :--- | :--- | :--- |
| `chunk_magic` | 4 bytes | `bytes[4]` | `CHK\x00` |
| `index` | 4 bytes | `uint32_be` | Contiguous chunk sequence (0, 1, 2...) |
| `raw_size` | 4 bytes | `uint32_be` | Uncompressed byte count ($\le 64\text{ MiB}$) |
| `comp_size` | 4 bytes | `uint32_be` | Compressed payload byte count ($\le 64\text{ MiB}$) |
| `codec_len` | 1 byte | `uint8` | Length of codec string ($L_C$) |
| `codec_name` | $L_C$ bytes | `UTF-8` | Codec identifier (e.g., `brotli`, `zstd+plane4`) |
| `sha256_digest`| 32 bytes | `bytes[32]` | Raw binary SHA-256 digest of uncompressed chunk |
| `payload` | `comp_size` | `bytes` | Raw compressed byte payload |

---

## 4. Manifest Schema Definition

The container manifest describes the overall file properties and encoding policy:

```json
{
  "version": "0.3.0",
  "filename": "dataset.csv",
  "file_size": 10485760,
  "file_sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
  "chunk_size": 1048576,
  "total_chunks": 10,
  "policy": "auto",
  "default_encoding": "base85",
  "profile": "text",
  "created_at": "2026-10-29T21:00:00+00:00"
}
```

### Field Definitions & Limits:
* **`version`** (`string`): ZTAR format version. Supported: `"0.1.0"`, `"0.2.0"`, `"0.3.0"`.
* **`filename`** (`string`): Advisory filename. Decoders MUST sanitize this path (using basename only) to prevent directory traversal.
* **`file_size`** (`integer`): Expected total uncompressed file size in bytes ($0 \le S \le 2^{63}-1$).
* **`file_sha256`** (`string`): 64-character lowercase hex digest of the complete uncompressed file.
* **`chunk_size`** (`integer`): Standard chunk size in bytes ($1 \le C \le 67,108,864$ [64 MiB]).
* **`total_chunks`** (`integer`): Total number of chunks in the container ($0 \le N \le 1,000,000$).
* **`policy`** (`string`): Compression policy or codec directive (`"auto"`, `"brotli"`, `"zstd"`, etc.).
* **`default_encoding`** (`string`): Text encoding profile (`"base85"`, `"none"`).
* **`profile`** (`string`): Container profile (`"text"` or `"binary"`).
* **`created_at`** (`string`): ISO 8601 UTC creation timestamp.

---

## 5. Codec and Preconditioning Transform Registry

ZTAR separates **preconditioning filters** from **entropy encoders** using composite syntax: `{base_codec}+{transform}`.

### 5.1 Base Codecs
| Codec | Provider | Description |
| :--- | :--- | :--- |
| `brotli` | RFC 7932 | High-compression 2nd-order context modeling |
| `zstd` | RFC 8878 | High-throughput finite-state entropy (FSE) compression |
| `lzma` | LZMA2 / XZ | High-ratio dictionary Markov-chain compression |
| `zlib` | RFC 1951 | Standard Deflate baseline |
| `bz2` | Burrows-Wheeler | BWT block-sorting compression |
| `lz4` | Fast LZ | Ultra-high speed real-time codec |
| `raw` | Identity | Pass-through for high-entropy incompressible media |

### 5.2 Adaptive Structured Preconditioning & Deinterleaving (ASPD)
ASPD transforms are reversible, bijective byte reorganizations evaluated before compression:

| Transform | Stride / Width | Application Domain |
| :--- | :--- | :--- |
| `plane2` | 2 bytes | Deinterleave high/low byte planes (16-bit PCM / 16-bit integers) |
| `plane4` | 4 bytes | Deinterleave 4 byte planes (32-bit float/int, RGBA telemetry) |
| `delta1` | 1 byte | Byte-level stride-1 differential ($x_i - x_{i-1} \pmod{256}$) |
| `delta2` | 2 bytes | 16-bit word-level stride-2 differential |
| `delta4` | 4 bytes | 32-bit word-level stride-4 differential |
| `pdelta2` | 2 bytes | Planar deinterleaving followed by stride-1 intra-plane delta |
| `pdelta4` | 4 bytes | 4-way planar deinterleaving followed by intra-plane delta |

---

## 6. Security Model & Resource Limits

To protect systems against malicious archives and decompression denial-of-service, all ZTAR decoders MUST enforce:

1. **Path Traversal Sanitization**:
   Implementations MUST strip path delimiters (`/`, `\`, `..`) from `manifest.filename` when saving recovered files:
   ```python
   safe_filename = Path(manifest.filename).name
   ```
2. **Chunk Size Guard**:
   Containers declaring `raw_size > 67,108,864` (64 MiB) MUST be rejected before memory allocation.
3. **Decompression Expansion Limit**:
   If a compressed chunk expands by more than `100,000x`, the decoder MUST terminate and raise `IntegrityError` to prevent decompression bombs.
4. **Chunk Count Limit**:
   Declared `total_chunks` exceeding `1,000,000` MUST be rejected with `ContainerFormatError`.
5. **Cryptographic Verification**:
   Decode operations MUST write to `.ztmp` temporary files and execute atomic rename only after verifying total written bytes and whole-file SHA-256.
