"""Integration test verifying exact round-trip reconstruction and standard media rendering for all file categories."""

import pytest
from pathlib import Path

from ziptext.engine import ZipTextEngine
from ziptext.utils import compute_file_sha256
from ziptext.validator import MediaValidator

CATEGORIES_DIR = Path("fixtures/all_categories")


@pytest.fixture(scope="module")
def all_category_files():
    if not CATEGORIES_DIR.exists():
        pytest.skip("fixtures/all_categories not generated")
    files = sorted([f for f in CATEGORIES_DIR.iterdir() if f.is_file()])
    assert len(files) >= 15, "Expected comprehensive suite of test files"
    return files


def test_roundtrip_all_categories_text_profile(all_category_files, tmp_path):
    """Test text profile (.ztxt) on every file type: SHA-256 exact match + valid standard media."""
    engine = ZipTextEngine()

    for src_file in all_category_files:
        container = tmp_path / f"{src_file.name}.ztxt"
        recovered = tmp_path / f"rec_{src_file.name}"

        # 1. Encode
        enc_res = engine.encode_file(
            input_path=src_file,
            output_path=container,
            codec="auto",
            profile="text",
        )
        assert container.exists()
        assert enc_res.encoded_size > 0

        # 2. Decode
        engine.decode_file(
            input_path=container,
            output_path=recovered,
        )
        assert recovered.exists()

        # 3. Exact byte-for-byte verification
        orig_hash = compute_file_sha256(src_file)
        rec_hash = compute_file_sha256(recovered)
        assert orig_hash == rec_hash, f"Hash mismatch on {src_file.name} in .ztxt"

        # 4. Standard media / document / parser verification
        val_rep = MediaValidator.validate(recovered)
        assert val_rep.is_valid, f"Media validation failed on {src_file.name}: {val_rep.details}"


def test_roundtrip_all_categories_binary_profile(all_category_files, tmp_path):
    """Test binary profile (.zbin) on every file type: zero bloat for media + byte-for-byte exact."""
    engine = ZipTextEngine()

    for src_file in all_category_files:
        container = tmp_path / f"{src_file.name}.zbin"
        recovered = tmp_path / f"rec_bin_{src_file.name}"

        # 1. Encode
        enc_res = engine.encode_file(
            input_path=src_file,
            output_path=container,
            codec="auto",
            profile="binary",
        )
        assert container.exists()

        # 2. Decode
        engine.decode_file(
            input_path=container,
            output_path=recovered,
        )
        assert recovered.exists()

        # 3. Exact byte-for-byte verification
        orig_hash = compute_file_sha256(src_file)
        rec_hash = compute_file_sha256(recovered)
        assert orig_hash == rec_hash, f"Hash mismatch on {src_file.name} in .zbin"

        # 4. Standard media / document / parser verification
        val_rep = MediaValidator.validate(recovered)
        assert val_rep.is_valid, f"Media validation failed on {src_file.name}: {val_rep.details}"
