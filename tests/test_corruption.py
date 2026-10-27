"""Tests for tamper and corruption detection in .ztxt containers."""

import re
import pytest
from ziptext.container import ContainerFormatError, IntegrityError
from ziptext.engine import ZipTextEngine


def test_corrupt_chunk_payload(temp_dir, sample_text_file):
    engine = ZipTextEngine()
    ztxt = temp_dir / "corrupted_payload.ztxt"
    rec = temp_dir / "rec_corrupted.txt"
    engine.encode_file(sample_text_file, ztxt, codec="zlib", chunk_size=16384)

    # Modify a character in the chunk body text
    content = ztxt.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find a payload line (after BEGIN CHUNK 0 and before END CHUNK 0)
    mutated = False
    in_chunk = False
    for i, line in enumerate(lines):
        if line.startswith("-----BEGIN CHUNK"):
            in_chunk = True
            continue
        if in_chunk and not line.startswith("-----") and len(line) > 10:
            char = "Z" if line[5] != "Z" else "A"
            lines[i] = line[:5] + char + line[6:]
            mutated = True
            break

    assert mutated, "Failed to find candidate payload line"
    ztxt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises((IntegrityError, ContainerFormatError)):
        engine.decode_file(ztxt, rec)


def test_corrupt_chunk_header_checksum(temp_dir, sample_text_file):
    engine = ZipTextEngine()
    ztxt = temp_dir / "corrupted_checksum.ztxt"
    rec = temp_dir / "rec_bad_checksum.txt"
    engine.encode_file(sample_text_file, ztxt, codec="raw")

    content = ztxt.read_text(encoding="utf-8")
    # Mutate sha256 in chunk header line
    tampered = re.sub(r"sha256=[0-9a-f]{64}", "sha256=" + "0" * 64, content)
    ztxt.write_text(tampered, encoding="utf-8")

    with pytest.raises(IntegrityError, match="Chunk 0 SHA-256 mismatch"):
        engine.decode_file(ztxt, rec)


def test_corrupt_whole_file_hash(temp_dir, sample_text_file):
    engine = ZipTextEngine()
    ztxt = temp_dir / "bad_file_hash.ztxt"
    rec = temp_dir / "rec_bad_file_hash.txt"
    engine.encode_file(sample_text_file, ztxt, codec="raw")

    content = ztxt.read_text(encoding="utf-8")
    # Mutate file_sha256 in manifest
    tampered = re.sub(r'"file_sha256": "[0-9a-f]{64}"', '"file_sha256": "' + "f" * 64 + '"', content)
    ztxt.write_text(tampered, encoding="utf-8")

    with pytest.raises(IntegrityError, match="Whole-file SHA-256 mismatch"):
        engine.decode_file(ztxt, rec)


def test_missing_chunk(temp_dir, sample_text_file):
    engine = ZipTextEngine()
    ztxt = temp_dir / "missing_chunk.ztxt"
    rec = temp_dir / "rec_missing.txt"
    # Create multi-chunk file
    engine.encode_file(sample_text_file, ztxt, codec="raw", chunk_size=8192)

    content = ztxt.read_text(encoding="utf-8")
    # Remove CHUNK 1 entirely
    pattern = re.compile(r"-----BEGIN CHUNK 1 .*?-----END CHUNK 1-----\n", re.DOTALL)
    tampered = pattern.sub("", content)
    ztxt.write_text(tampered, encoding="utf-8")

    with pytest.raises(ContainerFormatError):
        engine.decode_file(ztxt, rec)
