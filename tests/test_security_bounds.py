"""Security and boundary tests for ZipText container and engine."""

import hashlib
import io
import json
import tempfile
from pathlib import Path
import pytest

from ziptext import ZipTextEngine
from ziptext.container import (
    ContainerFormatError,
    ContainerManifest,
    ContainerReader,
    ContainerWriter,
    IntegrityError,
    MAX_DECLARED_CHUNK_SIZE,
    MAX_DECOMPRESSION_EXPANSION_RATIO,
    MAX_TOTAL_CHUNKS,
)


def test_manifest_chunk_size_bounds():
    """Verify manifest rejects chunk_size exceeding MAX_DECLARED_CHUNK_SIZE."""
    malicious_dict = {
        "version": "0.3.0",
        "filename": "payload.bin",
        "file_size": 100,
        "file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "chunk_size": MAX_DECLARED_CHUNK_SIZE + 1,
        "total_chunks": 1,
        "policy": "auto",
        "profile": "text",
    }
    with pytest.raises(ContainerFormatError, match="exceeds maximum allowable"):
        ContainerManifest.from_dict(malicious_dict)


def test_manifest_total_chunks_bounds():
    """Verify manifest rejects total_chunks exceeding MAX_TOTAL_CHUNKS."""
    malicious_dict = {
        "version": "0.3.0",
        "filename": "payload.bin",
        "file_size": 100,
        "file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "chunk_size": 1024,
        "total_chunks": MAX_TOTAL_CHUNKS + 1,
        "policy": "auto",
        "profile": "text",
    }
    with pytest.raises(ContainerFormatError, match="exceeds maximum allowable"):
        ContainerManifest.from_dict(malicious_dict)


def test_directory_traversal_sanitization():
    """Verify decode_file prevents directory traversal when output_path is not specified."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        container_file = tmp_path / "attack.ztxt"

        payload = b"root:x:0:0::"
        payload_sha256 = hashlib.sha256(payload).hexdigest()

        manifest = ContainerManifest(
            version="0.3.0",
            filename="../../etc/passwd",
            file_size=len(payload),
            file_sha256=payload_sha256,
            chunk_size=1024,
            total_chunks=1,
            policy="raw",
            profile="text",
        )

        with open(container_file, "w", encoding="utf-8") as f:
            writer = ContainerWriter(f, manifest=manifest, profile="text")
            writer.write_chunk(payload, codec="raw")
            writer.close()

        engine = ZipTextEngine()
        result = engine.decode_file(container_file)

        # Output file must be recovered_passwd inside tmp_path, NOT escaping outside
        assert result.output_path.parent == tmp_path.resolve()
        assert result.output_path.name == "recovered_passwd"
        assert result.output_path.exists()
