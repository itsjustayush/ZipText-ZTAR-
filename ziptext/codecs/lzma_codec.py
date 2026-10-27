"""LZMA/XZ compression codec."""

import lzma
from ziptext.codecs.base import Codec, CodecRegistry


@CodecRegistry.register
class LzmaCodec(Codec):
    """LZMA2 / XZ high-ratio compression codec."""

    def __init__(self, preset: int = 6):
        self.preset = preset

    @property
    def name(self) -> str:
        return "lzma"

    def encode(self, data: bytes) -> bytes:
        return lzma.compress(data, preset=self.preset)

    def decode(self, data: bytes) -> bytes:
        return lzma.decompress(data)
