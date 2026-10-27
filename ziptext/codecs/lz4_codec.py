"""LZ4 high-speed compression codec (optional dependency)."""

from ziptext.codecs.base import Codec, CodecRegistry

try:
    import lz4.frame  # type: ignore

    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False


if HAS_LZ4:
    @CodecRegistry.register
    class Lz4Codec(Codec):
        """LZ4 frame compression codec."""

        def __init__(self, compression_level: int = 0):
            self.compression_level = compression_level

        @property
        def name(self) -> str:
            return "lz4"

        def encode(self, data: bytes) -> bytes:
            return lz4.frame.compress(data, compression_level=self.compression_level)

        def decode(self, data: bytes) -> bytes:
            return lz4.frame.decompress(data)
else:
    class Lz4Codec(Codec):  # type: ignore
        """Placeholder when lz4 is not installed."""

        @property
        def name(self) -> str:
            return "lz4"

        def encode(self, data: bytes) -> bytes:
            raise RuntimeError("LZ4 is not installed. Install via `pip install lz4`.")

        def decode(self, data: bytes) -> bytes:
            raise RuntimeError("LZ4 is not installed. Install via `pip install lz4`.")
