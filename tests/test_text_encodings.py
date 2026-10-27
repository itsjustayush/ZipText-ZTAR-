"""Tests for text encodings (Base85 and Base64)."""

import pytest
from ziptext.text_encodings import (
    decode_text,
    encode_text,
    get_available_encodings,
)


def test_base85_roundtrip():
    payloads = [
        b"Standard ASCII text",
        b"\x00\x01\x02\xfe\xff" * 20,
        bytes(range(256)),
    ]
    for p in payloads:
        txt = encode_text(p, "base85")
        assert isinstance(txt, str)
        restored = decode_text(txt, "base85")
        assert restored == p


def test_base64_roundtrip():
    payloads = [
        b"Standard ASCII text in Base64",
        b"\xaa\xbb\xcc\xdd\xee" * 15,
        bytes(range(128)),
    ]
    for p in payloads:
        txt = encode_text(p, "base64")
        assert isinstance(txt, str)
        restored = decode_text(txt, "base64")
        assert restored == p


def test_invalid_encoding_name():
    with pytest.raises(ValueError, match="Unsupported text encoding"):
        encode_text(b"abc", "hex_invalid")

    with pytest.raises(ValueError, match="Unsupported text encoding"):
        decode_text("abc", "hex_invalid")


def test_whitespace_resilience():
    data = b"Testing newline and whitespace resilience in Base85 decoding"
    encoded = encode_text(data, "base85")
    # Insert arbitrary spaces, newlines, and carriage returns
    noisy = f"  {encoded[:10]}\n\n  {encoded[10:25]}\r\n {encoded[25:]}  \n"
    restored = decode_text(noisy, "base85")
    assert restored == data
