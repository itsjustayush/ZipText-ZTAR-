"""Bzip2 compression codec."""

import bz2
from ziptext.codecs.base import Codec, CodecRegistry


@CodecRegistry.register
class Bz2Codec(Codec):
    """bzip2 Burrows-Wheeler block-sorting compression codec."""

    def __init__(self, compresslevel: int = 9):
        self.compresslevel = compresslevel

    @property
    def name(self) -> str:
        return "bz2"

    def encode(self, data: bytes) -> bytes:
        return bz2.compress(data, compresslevel=self.compresslevel)

    def decode(self, data: bytes) -> bytes:
        return bz2.decompress(data)
