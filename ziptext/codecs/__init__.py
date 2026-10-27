"""Compression codecs package for Zip Text."""

from ziptext.codecs.base import Codec, CodecRegistry
from ziptext.codecs.raw import RawCodec
from ziptext.codecs.zlib_codec import ZlibCodec
from ziptext.codecs.bz2_codec import Bz2Codec
from ziptext.codecs.lzma_codec import LzmaCodec
from ziptext.codecs.lz4_codec import Lz4Codec, HAS_LZ4

__all__ = [
    "Codec",
    "CodecRegistry",
    "RawCodec",
    "ZlibCodec",
    "Bz2Codec",
    "LzmaCodec",
    "Lz4Codec",
    "HAS_LZ4",
]
