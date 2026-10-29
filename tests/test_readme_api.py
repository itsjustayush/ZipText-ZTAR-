"""Test that verifies the exact Python SDK examples in the README execute without errors."""

import hashlib
import tempfile
from pathlib import Path
import pytest

from ziptext import ZipTextEngine, ContainerWriter, ContainerReader


def test_readme_high_level_api():
    """Verify README line-by-line high-level SDK workflow."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        source_file = tmp_path / "report.pdf"
        # Write dummy PDF-like data
        sample_data = b"%PDF-1.4\n" + b"This is a sample document for ZipText SDK testing." * 500
        source_file.write_bytes(sample_data)

        # 1. High-level one-line roundtrip
        engine = ZipTextEngine(chunk_size_bytes=1048576, default_codec="auto")

        # Encode
        ztxt_file = tmp_path / "report.ztxt"
        res = engine.encode_file(source_file, ztxt_file, profile="text")
        assert res.original_size == len(sample_data)
        assert res.container_size > 0
        assert res.codec_used is not None

        # Decode with byte-for-byte SHA256 check
        recovered_file = tmp_path / "recovered_report.pdf"
        dec = engine.decode_file(ztxt_file, recovered_file)
        assert dec.exact_match is True
        assert recovered_file.read_bytes() == sample_data


def test_readme_streaming_writer():
    """Verify README streaming ContainerWriter snippet."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        stream_file = tmp_path / "large_stream.ztxt"

        raw_chunk1 = b"chunk data 1 " * 100
        raw_chunk2 = b"chunk data 2 " * 100
        total_data = raw_chunk1 + raw_chunk2
        sha256_hash = hashlib.sha256(total_data).hexdigest()

        # Streaming write
        with open(stream_file, "w", encoding="utf-8") as f:
            writer = ContainerWriter(f, original_filename="archive.tar", profile="text")
            writer.write_chunk(raw_chunk1, codec="zstd")
            writer.write_chunk(raw_chunk2, codec="zstd")
            writer.finalize(original_size=len(total_data), whole_file_hash=sha256_hash)

        # Verify readable and recoverable with ContainerReader
        with ContainerReader.open(stream_file) as reader:
            assert reader.manifest.filename == "archive.tar"
            assert reader.manifest.file_size == len(total_data)
            assert reader.manifest.file_sha256 == sha256_hash

            reconstructed = bytearray()
            for header, chunk_data in reader.iter_chunks():
                reconstructed.extend(chunk_data)

            assert bytes(reconstructed) == total_data
