"""Pytest fixtures and test helpers for Zip Text."""

import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test artifacts and auto-cleanup."""
    with tempfile.TemporaryDirectory(prefix="ziptext_test_") as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample repetitive text file."""
    p = temp_dir / "sample.txt"
    content = "Zip Text Adaptive Representation (ZTAR) test file line.\n" * 1000
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture
def sample_binary_file(temp_dir):
    """Create a sample binary file."""
    p = temp_dir / "sample.bin"
    # Mixed pattern: compressible header followed by random data
    data = (b"ZTAR_HEADER" * 100) + bytes(i % 256 for i in range(10000))
    p.write_bytes(data)
    return p
