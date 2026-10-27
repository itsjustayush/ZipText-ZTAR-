"""Zip Text - Zip Text Adaptive Representation (ZTAR) Lab Prototype."""

__version__ = "0.2.0"

from ziptext.container import (
    ContainerManifest,
    ContainerReader,
    ContainerWriter,
    IntegrityError,
    ZipTextError,
)
from ziptext.engine import DecodeResult, EncodeResult, ZipTextEngine

__all__ = [
    "__version__",
    "ZipTextEngine",
    "EncodeResult",
    "DecodeResult",
    "ContainerManifest",
    "ContainerReader",
    "ContainerWriter",
    "ZipTextError",
    "IntegrityError",
]
