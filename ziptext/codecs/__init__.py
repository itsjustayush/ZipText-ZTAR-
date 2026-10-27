"""Compression codecs package for Zip Text."""

from ziptext.codecs.base import Codec, CodecRegistry
from ziptext.codecs.raw import RawCodec
from ziptext.codecs.zlib_codec import ZlibCodec
from ziptext.codecs.bz2_codec import Bz2Codec
from ziptext.codecs.lzma_codec import LzmaCodec
from ziptext.codecs.lz4_codec import Lz4Codec, HAS_LZ4
from ziptext.codecs.zstd_codec import ZstdCodec, HAS_ZSTD
from ziptext.codecs.brotli_codec import BrotliCodec, HAS_BROTLI

__all__ = [
    "Codec",
    "CodecRegistry",
    "RawCodec",
    "ZlibCodec",
    "Bz2Codec",
    "LzmaCodec",
    "Lz4Codec",
    "HAS_LZ4",
    "ZstdCodec",
    "HAS_ZSTD",
    "BrotliCodec",
    "HAS_BROTLI",
]
