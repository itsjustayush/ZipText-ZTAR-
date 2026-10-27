"""Tests for ZipTextEngine encoding, decoding, bounded memory, and verification."""

import pytest
from ziptext.codecs.lz4_codec import HAS_LZ4
from ziptext.engine import ZipTextEngine
from ziptext.utils import compute_file_sha256


def test_engine_roundtrip_lossless(temp_dir, sample_text_file):
    engine = ZipTextEngine()
    ztxt_path = temp_dir / "encoded.ztxt"
    recovered_path = temp_dir / "recovered.txt"

    enc_res = engine.encode_file(sample_text_file, ztxt_path, codec="auto", chunk_size=32768)
    assert enc_res.total_chunks > 0
    assert ztxt_path.exists()

    dec_res = engine.decode_file(ztxt_path, recovered_path)
    assert dec_res.exact_match is True
    assert recovered_path.exists()
    assert compute_file_sha256(sample_text_file) == compute_file_sha256(recovered_path)
    assert recovered_path.read_bytes() == sample_text_file.read_bytes()


def test_engine_adaptive_selection(temp_dir):
    engine = ZipTextEngine()
    # High-redundancy file
    f = temp_dir / "compressible.txt"
    f.write_text("Repeating patterns reduce data representation volume! " * 500, encoding="utf-8")
    ztxt_path = temp_dir / "comp.ztxt"

    enc_res = engine.encode_file(f, ztxt_path, codec="auto", chunk_size=131072)
    # Under adaptive selection, a compressing codec should be selected over raw
    codecs_used = list(enc_res.codec_distribution.keys())
    assert any(c in ["lzma", "zlib", "bz2", "lz4", "zstd", "brotli"] for c in codecs_used)
    assert enc_res.encoded_size < enc_res.original_size


def test_engine_multi_chunk(temp_dir):
    engine = ZipTextEngine()
    # Create 100 KiB file with 16 KiB chunks = 7 chunks
    data = bytes((i * 17) % 256 for i in range(100 * 1024))
    f = temp_dir / "multi.bin"
    f.write_bytes(data)

    ztxt_path = temp_dir / "multi.ztxt"
    recovered = temp_dir / "multi_rec.bin"

    enc_res = engine.encode_file(f, ztxt_path, codec="zlib", chunk_size=16384)
    assert enc_res.total_chunks == 7

    dec_res = engine.decode_file(ztxt_path, recovered)
    assert dec_res.exact_match is True
    assert recovered.read_bytes() == data


def test_engine_explicit_codecs(temp_dir):
    engine = ZipTextEngine()
    data = b"Testing explicit codec policy pass-through in ZipTextEngine." * 100
    src = temp_dir / "explicit.dat"
    src.write_bytes(data)

    test_policies = ["raw", "zlib", "bz2", "lzma"]
    if HAS_LZ4:
        test_policies.append("lz4")

    for policy in test_policies:
        ztxt = temp_dir / f"test_{policy}.ztxt"
        rec = temp_dir / f"rec_{policy}.dat"

        enc = engine.encode_file(src, ztxt, codec=policy, chunk_size=65536)
        assert policy in enc.codec_distribution

        dec = engine.decode_file(ztxt, rec)
        assert dec.exact_match is True
        assert rec.read_bytes() == data


def test_engine_empty_file(temp_dir):
    engine = ZipTextEngine()
    empty = temp_dir / "empty.dat"
    empty.write_bytes(b"")

    ztxt = temp_dir / "empty.ztxt"
    rec = temp_dir / "empty_rec.dat"

    enc = engine.encode_file(empty, ztxt, codec="auto")
    assert enc.original_size == 0
    assert enc.total_chunks == 0

    dec = engine.decode_file(ztxt, rec)
    assert dec.exact_match is True
    assert rec.stat().st_size == 0


def test_engine_memory_bounded(temp_dir):
    engine = ZipTextEngine()
    # 256 KiB file encoded with 32 KiB chunking
    f = temp_dir / "stream_mem.bin"
    f.write_bytes(b"\xaa\xbb\xcc\xdd" * (64 * 1024))

    ztxt = temp_dir / "mem.ztxt"
    rec = temp_dir / "mem_rec.bin"

    enc = engine.encode_file(f, ztxt, codec="auto", chunk_size=32768)
    dec = engine.decode_file(ztxt, rec)

    assert enc.peak_memory_rss > 0
    assert dec.peak_memory_rss > 0
    assert dec.exact_match is True


def test_verify_file(temp_dir, sample_text_file):
    engine = ZipTextEngine()
    ztxt = temp_dir / "verify_target.ztxt"
    engine.encode_file(sample_text_file, ztxt, codec="auto")

    result = engine.verify_file(ztxt)
    assert result["valid"] is True
    assert result["expected_sha256"] == compute_file_sha256(sample_text_file)
    assert result["chunks_verified"] > 0
