"""Tests for compression codecs and codec registry."""

import pytest
from ziptext.codecs.base import CodecRegistry
from ziptext.codecs.bz2_codec import Bz2Codec
from ziptext.codecs.lz4_codec import HAS_LZ4, Lz4Codec
from ziptext.codecs.lzma_codec import LzmaCodec
from ziptext.codecs.raw import RawCodec
from ziptext.codecs.zlib_codec import ZlibCodec


def test_raw_codec():
    codec = RawCodec()
    assert codec.name == "raw"
    data = b"Hello, ZTAR lossless world! 1234567890"
    encoded = codec.encode(data)
    assert encoded == data
    decoded = codec.decode(encoded)
    assert decoded == data


def test_zlib_codec():
    codec = ZlibCodec()
    assert codec.name == "zlib"
    data = b"Repetitive string repetitive string repetitive string!" * 50
    compressed = codec.encode(data)
    assert len(compressed) < len(data)
    restored = codec.decode(compressed)
    assert restored == data


def test_bz2_codec():
    codec = Bz2Codec()
    assert codec.name == "bz2"
    data = b"Bzip2 Burrows Wheeler compression block test!" * 50
    compressed = codec.encode(data)
    assert len(compressed) < len(data)
    restored = codec.decode(compressed)
    assert restored == data


def test_lzma_codec():
    codec = LzmaCodec()
    assert codec.name == "lzma"
    data = b"LZMA2 XZ high ratio stream test sequence!" * 50
    compressed = codec.encode(data)
    assert len(compressed) < len(data)
    restored = codec.decode(compressed)
    assert restored == data


def test_lz4_codec():
    if not HAS_LZ4:
        pytest.skip("LZ4 library not installed in environment")
    codec = Lz4Codec()
    assert codec.name == "lz4"
    data = b"LZ4 fast frame compression test sequence!" * 50
    compressed = codec.encode(data)
    restored = codec.decode(compressed)
    assert restored == data


def test_codec_registry_lookup():
    codecs = CodecRegistry.available_codecs()
    assert "raw" in codecs
    assert "zlib" in codecs
    assert "bz2" in codecs
    assert "lzma" in codecs

    raw_inst = CodecRegistry.get("raw")
    assert isinstance(raw_inst, RawCodec)

    with pytest.raises(ValueError, match="not found"):
        CodecRegistry.get("non_existent_codec")


def test_codec_empty_bytes():
    codecs_to_test = ["raw", "zlib", "bz2", "lzma"]
    if HAS_LZ4:
        codecs_to_test.append("lz4")

    for name in codecs_to_test:
        c = CodecRegistry.get(name)
        compressed = c.encode(b"")
        decompressed = c.decode(compressed)
        assert decompressed == b"", f"Failed for codec {name}"


def test_codec_single_byte():
    codecs_to_test = ["raw", "zlib", "bz2", "lzma"]
    if HAS_LZ4:
        codecs_to_test.append("lz4")

    single = b"\x42"
    for name in codecs_to_test:
        c = CodecRegistry.get(name)
        compressed = c.encode(single)
        decompressed = c.decode(compressed)
        assert decompressed == single, f"Failed for codec {name}"
