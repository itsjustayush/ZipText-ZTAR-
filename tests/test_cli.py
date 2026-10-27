"""Tests for Zip Text command line interface."""

import pytest
from ziptext.cli import main


def test_cli_fixtures_command(temp_dir):
    out_dir = temp_dir / "cli_fixtures"
    ret = main(["fixtures", "--output", str(out_dir), "--size-mb", "1"])
    assert ret == 0
    assert out_dir.exists()
    assert (out_dir / "repetitive_text.txt").exists()


def test_cli_encode_decode_flow(temp_dir, sample_text_file):
    ztxt_path = temp_dir / "cli_encoded.ztxt"
    recovered_path = temp_dir / "cli_recovered.txt"

    # Encode
    ret_enc = main([
        "encode",
        str(sample_text_file),
        str(ztxt_path),
        "--codec", "zlib",
        "--chunk-size", "16384",
    ])
    assert ret_enc == 0
    assert ztxt_path.exists()

    # Verify
    ret_verify = main(["verify", str(ztxt_path)])
    assert ret_verify == 0

    # Info
    ret_info = main(["info", str(ztxt_path)])
    assert ret_info == 0

    # Decode
    ret_dec = main(["decode", str(ztxt_path), str(recovered_path)])
    assert ret_dec == 0
    assert recovered_path.exists()
    assert recovered_path.read_bytes() == sample_text_file.read_bytes()


def test_cli_invalid_arguments(temp_dir):
    # Missing input file
    ret = main(["encode", "non_existent_file.bin", str(temp_dir / "out.ztxt")])
    assert ret != 0

    # Non-existent container
    ret_dec = main(["decode", "non_existent.ztxt", str(temp_dir / "out.bin")])
    assert ret_dec != 0
