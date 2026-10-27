"""Brotli high-density web text compression codec."""

from ziptext.codecs.base import Codec, CodecRegistry

try:
    import brotli  # type: ignore

    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False


if HAS_BROTLI:
    @CodecRegistry.register
    class BrotliCodec(Codec):
        """Brotli compression codec."""

        def __init__(self, quality: int = 11):
            self.quality = quality

        @property
        def name(self) -> str:
            return "brotli"

        def encode(self, data: bytes) -> bytes:
            return brotli.compress(data, quality=self.quality)

        def decode(self, data: bytes) -> bytes:
            return brotli.decompress(data)
else:
    class BrotliCodec(Codec):  # type: ignore
        """Placeholder when brotli is not installed."""

        @property
        def name(self) -> str:
            return "brotli"

        def encode(self, data: bytes) -> bytes:
            raise RuntimeError("Brotli is not installed. Install via `pip install brotli`.")

        def decode(self, data: bytes) -> bytes:
            raise RuntimeError("Brotli is not installed. Install via `pip install brotli`.")
