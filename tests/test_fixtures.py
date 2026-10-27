"""Tests for synthetic fixtures generator and format validity."""

import pytest
from ziptext.fixtures import (
    generate_corpus,
    generate_synthetic_mp4,
    generate_uncompressed_ppm,
)


def test_generate_corpus(temp_dir):
    paths = generate_corpus(temp_dir)
    assert len(paths) == 9

    expected_files = [
        "repetitive_text.txt",
        "source_like.txt",
        "uncompressed.ppm",
        "synthetic.pdf",
        "gradient.jpg",
        "noisy.jpg",
        "synthetic.mp4",
        "random.bin",
        "synthetic.png",
    ]
    for expected in expected_files:
        assert expected in paths
        p = paths[expected]
        assert p.is_file()
        assert p.stat().st_size > 0


def test_ppm_validity():
    ppm_data = generate_uncompressed_ppm(100, 100)
    assert ppm_data.startswith(b"P6\n100 100\n255\n")
    expected_header_len = len(b"P6\n100 100\n255\n")
    assert len(ppm_data) == expected_header_len + (100 * 100 * 3)


def test_mp4_box_structure():
    mp4_bytes = generate_synthetic_mp4(10000)
    assert len(mp4_bytes) == 10000
    # Must start with ftyp box
    assert b"ftyp" in mp4_bytes[:16]
    # Must contain moov box
    assert b"moov" in mp4_bytes
    # Must contain mdat box
    assert b"mdat" in mp4_bytes
