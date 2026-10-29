"""Tests for .ztxt container format, serialization, and stream parsing."""

import io
import json
import pytest
from ziptext.container import (
    ChunkHeader,
    ContainerFormatError,
    ContainerManifest,
    ContainerReader,
    ContainerWriter,
)
from ziptext.utils import compute_sha256


def test_manifest_serialization():
    manifest = ContainerManifest(
        version="0.1.0",
        filename="test.dat",
        file_size=1048576,
        file_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        chunk_size=262144,
        total_chunks=4,
        policy="auto",
        default_encoding="base85",
        created_at="2026-10-27T10:00:00Z",
    )
    json_str = manifest.to_json()
    assert "0.1.0" in json_str
    assert "test.dat" in json_str

    restored = ContainerManifest.from_dict(json.loads(json_str))
    assert restored.filename == manifest.filename
    assert restored.file_size == manifest.file_size
    assert restored.total_chunks == manifest.total_chunks


def test_chunk_header_serialization():
    header = ChunkHeader(
        index=0,
        raw_size=5000,
        compressed_size=1200,
        codec="lzma",
        text_encoding="base85",
        chunk_sha256="abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234",
    )
    line = header.to_header_line()
    assert line.startswith("-----BEGIN CHUNK 0")
    assert "raw_size=5000" in line
    assert "compressed_size=1200" in line
    assert "codec=lzma" in line

    parsed = ChunkHeader.from_header_line(line)
    assert parsed.index == 0
    assert parsed.raw_size == 5000
    assert parsed.compressed_size == 1200
    assert parsed.codec == "lzma"
    assert parsed.chunk_sha256 == header.chunk_sha256


def test_container_writer_reader_stream():
    buf = io.StringIO()
    manifest = ContainerManifest(
        version="0.1.0",
        filename="stream.bin",
        file_size=200,
        file_sha256="mock_hash",
        chunk_size=100,
        total_chunks=2,
        policy="raw",
    )
    writer = ContainerWriter(buf, manifest)

    chunk0_raw = b"A" * 100
    chunk1_raw = b"B" * 100
    writer.write_chunk(
        index=0,
        raw_size=100,
        compressed_bytes=chunk0_raw,
        codec_name="raw",
        text_encoding="base85",
        raw_sha256=compute_sha256(chunk0_raw),
    )
    writer.write_chunk(
        index=1,
        raw_size=100,
        compressed_bytes=chunk1_raw,
        codec_name="raw",
        text_encoding="base85",
        raw_sha256=compute_sha256(chunk1_raw),
    )
    writer.close()

    serialized = buf.getvalue()
    in_buf = io.StringIO(serialized)
    reader = ContainerReader(in_buf)

    assert reader.manifest.filename == "stream.bin"
    assert reader.manifest.total_chunks == 2

    chunks_read = list(reader.iter_chunks())
    assert len(chunks_read) == 2
    assert chunks_read[0][0].index == 0
    assert chunks_read[0][1] == chunk0_raw
    assert chunks_read[1][0].index == 1
    assert chunks_read[1][1] == chunk1_raw


def test_container_invalid_magic():
    bad_data = "THIS IS NOT A ZIPTEXT CONTAINER\n"
    with pytest.raises(ContainerFormatError, match="Invalid container magic"):
        ContainerReader(io.StringIO(bad_data))


def test_container_truncated_file():
    buf = io.StringIO()
    manifest = ContainerManifest(
        version="0.1.0",
        filename="trunc.bin",
        file_size=100,
        file_sha256="abc",
        chunk_size=100,
        total_chunks=1,
        policy="raw",
    )
    writer = ContainerWriter(buf, manifest)
    # Write header without chunk
    serialized = buf.getvalue()

    with pytest.raises(ContainerFormatError, match="Total chunks mismatch"):
        reader = ContainerReader(io.StringIO(serialized))
        list(reader.iter_chunks())


def test_container_corrupt_manifest():
    bad_data = (
        "-----BEGIN ZIPTEXT CONTAINER v0.1.0-----\n"
        "{INVALID JSON HERE\n"
        "-----END MANIFEST-----\n"
    )
    with pytest.raises(ContainerFormatError, match="Corrupted manifest JSON"):
        ContainerReader(io.StringIO(bad_data))
