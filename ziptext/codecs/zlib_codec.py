"""Zlib compression codec."""

import zlib
from ziptext.codecs.base import Codec, CodecRegistry


@CodecRegistry.register
class ZlibCodec(Codec):
    """DEFLATE/zlib compression codec."""

    def __init__(self, level: int = 6):
        self.level = level

    @property
    def name(self) -> str:
        return "zlib"

    def encode(self, data: bytes) -> bytes:
        return zlib.compress(data, level=self.level)

    def decode(self, data: bytes) -> bytes:
        return zlib.decompress(data)
