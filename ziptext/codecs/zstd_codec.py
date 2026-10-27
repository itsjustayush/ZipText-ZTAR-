"""Zstandard high-performance compression codec."""

from ziptext.codecs.base import Codec, CodecRegistry

try:
    import zstandard as zstd  # type: ignore

    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


if HAS_ZSTD:
    @CodecRegistry.register
    class ZstdCodec(Codec):
        """Zstandard frame compression codec."""

        def __init__(self, level: int = 3):
            self.level = level
            self._compressor = zstd.ZstdCompressor(level=self.level)
            self._decompressor = zstd.ZstdDecompressor()

        @property
        def name(self) -> str:
            return "zstd"

        def encode(self, data: bytes) -> bytes:
            return self._compressor.compress(data)

        def decode(self, data: bytes) -> bytes:
            return self._decompressor.decompress(data)
else:
    class ZstdCodec(Codec):  # type: ignore
        """Placeholder when zstandard is not installed."""

        @property
        def name(self) -> str:
            return "zstd"

        def encode(self, data: bytes) -> bytes:
            raise RuntimeError("Zstandard is not installed. Install via `pip install zstandard`.")

        def decode(self, data: bytes) -> bytes:
            raise RuntimeError("Zstandard is not installed. Install via `pip install zstandard`.")
