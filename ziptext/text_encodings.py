"""Text encoding adapters for converting binary data into text format."""

import base64
from typing import Callable, Dict, Tuple


def _encode_base85(data: bytes) -> str:
    return base64.b85encode(data).decode("ascii")


def _decode_base85(text: str) -> bytes:
    # Strip any potential whitespace/newlines introduced by formatting
    clean_text = "".join(text.split())
    return base64.b85decode(clean_text.encode("ascii"))


def _encode_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _decode_base64(text: str) -> bytes:
    clean_text = "".join(text.split())
    return base64.b64decode(clean_text.encode("ascii"))


_ENCODERS: Dict[str, Tuple[Callable[[bytes], str], Callable[[str], bytes]]] = {
    "base85": (_encode_base85, _decode_base85),
    "base64": (_encode_base64, _decode_base64),
}


def encode_text(data: bytes, encoding: str = "base85") -> str:
    """Encode bytes into textual representation."""
    key = encoding.lower()
    if key not in _ENCODERS:
        supported = ", ".join(_ENCODERS.keys())
        raise ValueError(f"Unsupported text encoding '{encoding}'. Supported: {supported}")
    return _ENCODERS[key][0](data)


def decode_text(text: str, encoding: str = "base85") -> bytes:
    """Decode textual representation back into bytes."""
    key = encoding.lower()
    if key not in _ENCODERS:
        supported = ", ".join(_ENCODERS.keys())
        raise ValueError(f"Unsupported text encoding '{encoding}'. Supported: {supported}")
    return _ENCODERS[key][1](text)


def get_available_encodings() -> list[str]:
    """Get list of supported text encodings."""
    return sorted(list(_ENCODERS.keys()))
