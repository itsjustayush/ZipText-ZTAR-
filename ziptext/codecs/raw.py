"""Raw codec (no compression pass-through)."""

from ziptext.codecs.base import Codec, CodecRegistry


@CodecRegistry.register
class RawCodec(Codec):
    """Pass-through codec storing uncompressed raw bytes."""

    @property
    def name(self) -> str:
        return "raw"

    def encode(self, data: bytes) -> bytes:
        return data

    def decode(self, data: bytes) -> bytes:
        return data
