"""Synthetic test corpus generator for Zip Text benchmarking."""

import io
import math
import os
import random
import struct
from pathlib import Path
from typing import Dict, List, Optional, Union
from PIL import Image, ImageDraw


def generate_repetitive_text(target_bytes: int = 2 * 1024 * 1024) -> bytes:
    """Generate highly repetitive prose text with predictable patterns."""
    sample = (
        "The Zip Text Adaptive Representation (ZTAR) framework evaluates compression efficiency, "
        "reconstruction guarantees, bounded memory usage, and portable container serialization. "
        "Every chunk undergoes structure-aware transformation and integrity verification via SHA-256 digests. "
        "Lossless mode guarantees exact byte-for-byte fidelity across diverse binary and text formats.\n"
    ).encode("utf-8")

    repeats = (target_bytes + len(sample) - 1) // len(sample)
    full = (sample * repeats)[:target_bytes]
    return full


def generate_source_like_text(target_bytes: int = 2 * 1024 * 1024) -> bytes:
    """Generate structured source-code-like text containing functions, types, and comments."""
    block = (
        "// ZipText Adaptive Representation Chunk Transformer\n"
        "export interface ChunkDescriptor {\n"
        "    readonly index: number;\n"
        "    readonly rawSize: number;\n"
        "    readonly compressedSize: number;\n"
        "    readonly codec: 'raw' | 'zlib' | 'bz2' | 'lzma' | 'lz4';\n"
        "    readonly checksum: string;\n"
        "}\n\n"
        "export async function processChunk(buffer: Uint8Array, config: Record<string, unknown>): Promise<ChunkDescriptor> {\n"
        "    const digest = await crypto.subtle.digest('SHA-256', buffer);\n"
        "    const hash = Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('');\n"
        "    return {\n"
        "        index: Number(config.index || 0),\n"
        "        rawSize: buffer.byteLength,\n"
        "        compressedSize: buffer.byteLength,\n"
        "        codec: 'raw',\n"
        "        checksum: hash\n"
        "    };\n"
        "}\n\n"
    ).encode("utf-8")

    repeats = (target_bytes + len(block) - 1) // len(block)
    return (block * repeats)[:target_bytes]


def generate_uncompressed_ppm(width: int = 768, height: int = 768) -> bytes:
    """Generate uncompressed PPM (P6 binary format) image with repeating color gradients."""
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    pixel_data = bytearray(width * height * 3)
    idx = 0
    for y in range(height):
        r_val = (y * 255) // height
        for x in range(width):
            g_val = (x * 255) // width
            b_val = ((x + y) * 255) // (width + height)
            pixel_data[idx] = r_val
            pixel_data[idx + 1] = g_val
            pixel_data[idx + 2] = b_val
            idx += 3
    return header + bytes(pixel_data)


def generate_synthetic_pdf(target_size: int = 8900) -> bytes:
    """Generate a syntactically valid minimal PDF-1.4 document."""
    content_stream = (
        "BT /F1 24 Tf 72 712 Td (Zip Text ZTAR Research Prototype Report) Tj ET\n"
        "BT /F1 12 Tf 72 670 Td (Exact byte-for-byte lossless verification test) Tj ET\n"
    )
    # Pad content stream with structured PDF comments to reach target size
    pad_len = max(0, target_size - 1200)
    padding = ("% " + "A" * 60 + "\n") * (pad_len // 63)
    stream_data = content_stream + padding
    stream_len = len(stream_data.encode("ascii"))

    pdf = (
        f"%PDF-1.4\n"
        f"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        f"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        f"4 0 obj << /Length {stream_len} >>\n"
        f"stream\n{stream_data}\nendstream\nendobj\n"
        f"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        f"xref\n0 6\n0000000000 65535 f \n"
        f"0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000242 00000 n \n"
        f"0000000450 00000 n \n"
        f"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n540\n%%EOF\n"
    ).encode("ascii")

    # If needed, trim or pad to exact size
    if len(pdf) < target_size:
        pdf += b"\n" + b"%" * (target_size - len(pdf) - 1) + b"\n"
    return pdf[:target_size]


def generate_gradient_jpeg(width: int = 640, height: int = 480) -> bytes:
    """Generate a smooth gradient JPEG image (~41.6 KiB)."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(255 * (y / height))
        g = int(128 * (1.0 - y / height))
        b = int(255 * math.sin(y / height * math.pi))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82)
    return buf.getvalue()


def generate_noisy_jpeg(width: int = 640, height: int = 480) -> bytes:
    """Generate a high-frequency noisy JPEG image (~198.8 KiB)."""
    rng = random.Random(42)
    noise_bytes = bytearray(rng.getrandbits(8) for _ in range(width * height * 3))
    img = Image.frombytes("RGB", (width, height), bytes(noise_bytes))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def generate_synthetic_png(width: int = 512, height: int = 512) -> bytes:
    """Generate a structured PNG image with colored shapes (~50 KiB)."""
    img = Image.new("RGB", (width, height), color=(240, 244, 248))
    draw = ImageDraw.Draw(img)
    for i in range(20):
        x0 = (i * 25) % (width - 120)
        y0 = (i * 30) % (height - 120)
        x1 = x0 + 80
        y1 = y0 + 80
        draw.rectangle([x0, y0, x1, y1], outline=(i * 12 % 255, 100, 200), width=3)
        draw.ellipse([x0 + 10, y0 + 10, x1 - 10, y1 - 10], fill=(200, i * 10 % 255, 150))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _build_mp4_box(box_type: bytes, payload: bytes) -> bytes:
    """Construct an ISO-BMFF box (4-byte size + 4-byte fourcc + payload)."""
    size = len(payload) + 8
    return struct.pack(">I4s", size, box_type) + payload


def generate_synthetic_mp4(target_size: int = 309657) -> bytes:
    """Generate a structurally valid ISO-BMFF MP4 container file (~302.4 KiB)."""
    # ftyp box (Major brand: isom, minor: 512, compatible: isom, iso2, mp41)
    ftyp_payload = b"isom" + struct.pack(">I", 512) + b"isomiso2mp41"
    ftyp = _build_mp4_box(b"ftyp", ftyp_payload)

    # moov minimal box hierarchy
    mvhd_payload = b"\x00" * 100  # Movie header box mock
    mvhd = _build_mp4_box(b"mvhd", mvhd_payload)

    tkhd = _build_mp4_box(b"tkhd", b"\x00" * 84)
    mdhd = _build_mp4_box(b"mdhd", b"\x00" * 24)
    hdlr = _build_mp4_box(b"hdlr", b"\x00" * 4 + b"vide" + b"\x00" * 16)
    stsd = _build_mp4_box(b"stsd", b"\x00" * 8)
    stts = _build_mp4_box(b"stts", b"\x00" * 8)
    stsc = _build_mp4_box(b"stsc", b"\x00" * 8)
    stsz = _build_mp4_box(b"stsz", b"\x00" * 12)
    stco = _build_mp4_box(b"stco", b"\x00" * 8)
    stbl = _build_mp4_box(b"stbl", stsd + stts + stsc + stsz + stco)
    minf = _build_mp4_box(b"minf", stbl)
    mdia = _build_mp4_box(b"mdia", mdhd + hdlr + minf)
    trak = _build_mp4_box(b"trak", tkhd + mdia)
    moov = _build_mp4_box(b"moov", mvhd + trak)

    current_size = len(ftyp) + len(moov)
    mdat_header_size = 8
    needed_mdat_payload = max(0, target_size - current_size - mdat_header_size)

    # Deterministic pseudo-random video/audio sample frames
    rng = random.Random(1337)
    mdat_payload = bytearray(rng.getrandbits(8) for _ in range(needed_mdat_payload))
    mdat = _build_mp4_box(b"mdat", bytes(mdat_payload))

    full_mp4 = ftyp + moov + mdat
    if len(full_mp4) < target_size:
        pad = target_size - len(full_mp4)
        free = _build_mp4_box(b"free", b"\x00" * max(0, pad - 8))
        full_mp4 += free
    return full_mp4[:target_size]


def generate_random_binary(size: int = 1048576) -> bytes:
    """Generate high-entropy pseudo-random binary data (1.00 MiB)."""
    rng = random.Random(2026)
    return bytearray(rng.getrandbits(8) for _ in range(size))


def generate_corpus(output_dir: Union[str, Path], scale_mb: float = 4.0) -> Dict[str, Path]:
    """Generate the complete 9-file test corpus."""
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    fixtures: Dict[str, bytes] = {
        "repetitive_text.txt": generate_repetitive_text(2 * 1024 * 1024),
        "source_like.txt": generate_source_like_text(2 * 1024 * 1024),
        "uncompressed.ppm": generate_uncompressed_ppm(768, 768),
        "synthetic.pdf": generate_synthetic_pdf(8900),
        "gradient.jpg": generate_gradient_jpeg(640, 480),
        "noisy.jpg": generate_noisy_jpeg(640, 480),
        "synthetic.mp4": generate_synthetic_mp4(309657),
        "random.bin": generate_random_binary(1048576),
        "synthetic.png": generate_synthetic_png(512, 512),
    }

    created_paths: Dict[str, Path] = {}
    for filename, data in fixtures.items():
        file_path = out_dir / filename
        with open(file_path, "wb") as f:
            f.write(data)
        created_paths[filename] = file_path

    return created_paths
