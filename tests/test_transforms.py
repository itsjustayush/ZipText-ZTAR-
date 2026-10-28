"""Comprehensive tests for ASPD mathematical transforms and composite codecs."""

import os
import pytest
from ziptext.codecs.base import CodecRegistry
from ziptext.engine import ZipTextEngine
from ziptext.transforms.aspd import (
    ASPDTransform,
    TRANSFORM_REGISTRY,
    apply_transform,
    deinterleave,
    delta_decode,
    delta_encode,
    interleave,
    invert_transform,
    plane_delta_decode,
    plane_delta_encode,
)
from ziptext.transforms.entropy import compute_shannon_entropy


def test_shannon_entropy_bounds():
    """Verify entropy bounds and properties."""
    assert compute_shannon_entropy(b"") == 0.0
    # Single repeating byte -> entropy is exactly 0
    assert compute_shannon_entropy(b"\x00" * 1000) == 0.0
    # Equal distribution of all 256 bytes -> entropy approaches 8.0
    full_alphabet = bytes(range(256)) * 4
    ent = compute_shannon_entropy(full_alphabet)
    assert pytest.approx(ent, 0.001) == 8.0


@pytest.mark.parametrize("t_name", list(TRANSFORM_REGISTRY.keys()))
def test_all_aspd_transforms_bijective_invertibility(t_name):
    """Verify that every registered transform is strictly bijective and reversible."""
    # Test on arbitrary random bytes
    raw_random = os.urandom(1024)
    enc = apply_transform(raw_random, t_name)
    dec = invert_transform(enc, t_name)
    assert dec == raw_random, f"Bijective failure in {t_name} on random bytes"

    # Test on structured wave data
    structured = bytes(int(128 + 127 * (i % 64) / 64) for i in range(2048))
    enc_s = apply_transform(structured, t_name)
    dec_s = invert_transform(enc_s, t_name)
    assert dec_s == structured, f"Bijective failure in {t_name} on structured data"


def test_delta_and_plane_deinterleaving():
    """Test manual delta and plane deinterleaving operations."""
    data = b"\x10\x20\x12\x22\x15\x25\x18\x28"
    deint = deinterleave(data, stride=2)
    assert deint == b"\x10\x12\x15\x18\x20\x22\x25\x28"
    reconstructed = interleave(deint, stride=2)
    assert reconstructed == data

    # Plane delta
    pd_enc = plane_delta_encode(data, stride=2)
    pd_dec = plane_delta_decode(pd_enc, stride=2)
    assert pd_dec == data


def test_composite_codec_registry():
    """Verify CodecRegistry dynamically produces CompositeCodec."""
    codec = CodecRegistry.get("zlib+pdelta2")
    assert codec.name == "zlib+pdelta2"

    raw = b"Structured telemetry data repeating sequence test!" * 50
    compressed = codec.encode(raw)
    decompressed = codec.decode(compressed)
    assert decompressed == raw

    # Check is_available
    assert CodecRegistry.is_available("zlib+pdelta2") is True
    assert CodecRegistry.is_available("brotli+pdelta4") is True
    assert CodecRegistry.is_available("zlib+nonexistent_filter") is False


def test_engine_roundtrip_with_composite_codec(temp_dir):
    """Verify end-to-end container encode/decode with composite transforms in both profiles."""
    engine = ZipTextEngine()
    test_file = temp_dir / "sample_signal.bin"
    # Create sinusoidal 16-bit PCM waveform within signed 16-bit range (-32768 to 32767)
    raw_signal = bytearray()
    for i in range(10000):
        val = int(500 * (i % 50))
        raw_signal.extend(val.to_bytes(2, "little", signed=True))
    test_file.write_bytes(raw_signal)

    # 1. Text container (.ztxt) with composite codec
    ztxt_path = temp_dir / "signal.ztxt"
    rec_txt_path = temp_dir / "recovered_from_txt.bin"
    enc_res = engine.encode_file(test_file, ztxt_path, codec="zlib+pdelta2")
    assert enc_res.encoded_size < len(raw_signal)
    dec_res = engine.decode_file(ztxt_path, rec_txt_path)
    assert dec_res.exact_match is True
    assert rec_txt_path.read_bytes() == bytes(raw_signal)

    # 2. Binary container (.zbin) with adaptive codec (which will choose ASPD)
    zbin_path = temp_dir / "signal.zbin"
    rec_bin_path = temp_dir / "recovered_from_bin.bin"
    enc_bin_res = engine.encode_file(test_file, zbin_path, codec="auto")
    dec_bin_res = engine.decode_file(zbin_path, rec_bin_path)
    assert dec_bin_res.exact_match is True
    assert rec_bin_path.read_bytes() == bytes(raw_signal)
