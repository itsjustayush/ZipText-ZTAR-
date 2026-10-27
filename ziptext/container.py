"""Zip Text Container format specification, dual-profile streaming parser, and serializer.

Supports both:
1. Portable Text Container (.ztxt): Human-readable ASCII / Base85 format for text transport.
2. High-Performance Binary Container (.zbin): Zero-overhead binary format for media and dense data.
"""

import io
import json
import struct
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, TextIO, Tuple, Union

from ziptext.codecs.base import CodecRegistry
from ziptext.text_encodings import decode_text, encode_text
from ziptext.utils import compute_sha256

TEXT_MAGIC_START = "-----BEGIN ZIPTEXT CONTAINER v0.1.0-----"
TEXT_MAGIC_END = "-----END ZIPTEXT CONTAINER-----"
TEXT_MANIFEST_END = "-----END MANIFEST-----"
TEXT_CHUNK_START = "-----BEGIN CHUNK "
TEXT_CHUNK_END = "-----END CHUNK "

BIN_MAGIC_START = b"ZBIN01\n"
BIN_MAGIC_END = b"ENDBIN01"
BIN_CHUNK_MAGIC = b"CHK\x00"

LINE_WRAP_WIDTH = 76


class ZipTextError(Exception):
    """Base exception for Zip Text operations."""
    pass


class ContainerFormatError(ZipTextError):
    """Raised when container syntax or structure is invalid."""
    pass


class IntegrityError(ZipTextError):
    """Raised when hash verification fails (corruption or tampering)."""
    pass


@dataclass
class ContainerManifest:
    """Metadata manifest describing the encoded file."""
    version: str
    filename: str
    file_size: int
    file_sha256: str
    chunk_size: int
    total_chunks: int
    policy: str
    default_encoding: str = "base85"
    profile: str = "text"
    created_at: str = ""

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContainerManifest":
        return cls(
            version=data.get("version", "0.1.0"),
            filename=data.get("filename", "unknown"),
            file_size=int(data["file_size"]),
            file_sha256=data["file_sha256"],
            chunk_size=int(data["chunk_size"]),
            total_chunks=int(data["total_chunks"]),
            policy=data.get("policy", "auto"),
            default_encoding=data.get("default_encoding", "base85"),
            profile=data.get("profile", "text"),
            created_at=data.get("created_at", ""),
        )


@dataclass
class ChunkHeader:
    """Metadata describing an individual compressed chunk."""
    index: int
    raw_size: int
    compressed_size: int
    codec: str
    text_encoding: str
    chunk_sha256: str

    def to_header_line(self) -> str:
        return (
            f"{TEXT_CHUNK_START}{self.index} "
            f"raw_size={self.raw_size} "
            f"compressed_size={self.compressed_size} "
            f"codec={self.codec} "
            f"encoding={self.text_encoding} "
            f"sha256={self.chunk_sha256}-----"
        )

    @classmethod
    def from_header_line(cls, line: str) -> "ChunkHeader":
        line = line.strip()
        if not line.startswith(TEXT_CHUNK_START) or not line.endswith("-----"):
            raise ContainerFormatError(f"Malformed chunk header line: {line}")
        inner = line[len(TEXT_CHUNK_START):-len("-----")].strip()
        tokens = inner.split()
        if not tokens:
            raise ContainerFormatError(f"Empty chunk header tokens: {line}")
        index = int(tokens[0])
        params: Dict[str, str] = {}
        for token in tokens[1:]:
            if "=" in token:
                k, v = token.split("=", 1)
                params[k] = v

        required = ["raw_size", "compressed_size", "codec", "encoding", "sha256"]
        for req in required:
            if req not in params:
                raise ContainerFormatError(f"Missing required parameter '{req}' in chunk header: {line}")

        return cls(
            index=index,
            raw_size=int(params["raw_size"]),
            compressed_size=int(params["compressed_size"]),
            codec=params["codec"],
            text_encoding=params["encoding"],
            chunk_sha256=params["sha256"],
        )


# ============================================================================
# Streaming Writers (Text and Binary)
# ============================================================================

class ContainerWriter:
    """Universal streaming writer supporting both text (.ztxt) and binary (.zbin) containers."""

    def __init__(self, out_file: Union[TextIO, BinaryIO], manifest: ContainerManifest, profile: str = "text"):
        self.out = out_file
        self.manifest = manifest
        self.profile = profile
        self.manifest.profile = profile
        self._chunks_written = 0

        if self.profile == "binary":
            self._write_binary_header()
        else:
            self._write_text_header()

    def _write_text_header(self) -> None:
        self.out.write(TEXT_MAGIC_START + "\n")
        self.out.write(self.manifest.to_json() + "\n")
        self.out.write(TEXT_MANIFEST_END + "\n")

    def _write_binary_header(self) -> None:
        self.out.write(BIN_MAGIC_START)
        manifest_bytes = self.manifest.to_json().encode("utf-8")
        self.out.write(struct.pack(">I", len(manifest_bytes)))
        self.out.write(manifest_bytes)

    def write_chunk(
        self,
        index: int,
        raw_size: int,
        compressed_bytes: bytes,
        codec_name: str,
        text_encoding: str,
        raw_sha256: str,
    ) -> int:
        """Write an encoded chunk according to the active container profile."""
        if self.profile == "binary":
            return self._write_binary_chunk(
                index, raw_size, compressed_bytes, codec_name, raw_sha256
            )
        else:
            return self._write_text_chunk(
                index, raw_size, compressed_bytes, codec_name, text_encoding, raw_sha256
            )

    def _write_text_chunk(
        self,
        index: int,
        raw_size: int,
        compressed_bytes: bytes,
        codec_name: str,
        text_encoding: str,
        raw_sha256: str,
    ) -> int:
        encoded_text = encode_text(compressed_bytes, text_encoding)
        header = ChunkHeader(
            index=index,
            raw_size=raw_size,
            compressed_size=len(compressed_bytes),
            codec=codec_name,
            text_encoding=text_encoding,
            chunk_sha256=raw_sha256,
        )
        chars_written = 0
        h_line = header.to_header_line() + "\n"
        self.out.write(h_line)
        chars_written += len(h_line)

        for i in range(0, len(encoded_text), LINE_WRAP_WIDTH):
            line = encoded_text[i:i + LINE_WRAP_WIDTH] + "\n"
            self.out.write(line)
            chars_written += len(line)

        end_line = f"{TEXT_CHUNK_END}{index}-----\n"
        self.out.write(end_line)
        chars_written += len(end_line)

        self._chunks_written += 1
        return chars_written

    def _write_binary_chunk(
        self,
        index: int,
        raw_size: int,
        compressed_bytes: bytes,
        codec_name: str,
        raw_sha256: str,
    ) -> int:
        bytes_written = 0
        self.out.write(BIN_CHUNK_MAGIC)
        bytes_written += len(BIN_CHUNK_MAGIC)

        codec_bytes = codec_name.encode("utf-8")
        # Header block: index (4B), raw_size (4B), compressed_size (4B), codec_len (1B)
        hdr_pack = struct.pack(">IIIB", index, raw_size, len(compressed_bytes), len(codec_bytes))
        self.out.write(hdr_pack)
        bytes_written += len(hdr_pack)

        self.out.write(codec_bytes)
        bytes_written += len(codec_bytes)

        # 32 bytes raw SHA256 binary digest
        raw_digest = bytes.fromhex(raw_sha256)
        self.out.write(raw_digest)
        bytes_written += len(raw_digest)

        # Raw compressed payload (Zero text expansion!)
        self.out.write(compressed_bytes)
        bytes_written += len(compressed_bytes)

        self._chunks_written += 1
        return bytes_written

    def close(self) -> None:
        """Write container trailer."""
        if self.profile == "binary":
            self.out.write(BIN_MAGIC_END)
        else:
            self.out.write(TEXT_MAGIC_END + "\n")


# ============================================================================
# Streaming Readers (Text and Binary)
# ============================================================================

class ContainerReader:
    """Universal streaming reader capable of reading both .ztxt and .zbin containers."""

    def __init__(self, in_file: Union[TextIO, BinaryIO]):
        self.file = in_file
        # Check whether stream is text or binary
        if hasattr(in_file, "buffer"):
            # TextIOWrapper with underlying binary buffer
            peek = in_file.buffer.peek(16)[:16]
            self.is_binary = peek.startswith(BIN_MAGIC_START)
        elif hasattr(in_file, "read"):
            pos = in_file.tell() if hasattr(in_file, "tell") else 0
            # Read first line or magic bytes
            sample = in_file.read(16)
            if hasattr(in_file, "seek"):
                in_file.seek(pos)
            if isinstance(sample, bytes):
                self.is_binary = sample.startswith(BIN_MAGIC_START)
            else:
                self.is_binary = sample.startswith("ZBIN01")
        else:
            self.is_binary = False

        self.manifest = self._read_manifest()

    @classmethod
    def open(cls, file_path: Union[str, Path]) -> "ContainerReader":
        """Convenience method to open a container file in appropriate mode."""
        p = Path(file_path).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Container not found: {p}")
        with open(p, "rb") as test_f:
            magic = test_f.read(16)

        if magic.startswith(BIN_MAGIC_START):
            f = open(p, "rb")
        else:
            f = open(p, "r", encoding="utf-8")
        return cls(f)

    def __enter__(self) -> "ContainerReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        if hasattr(self.file, "close"):
            self.file.close()

    def _read_manifest(self) -> ContainerManifest:
        if self.is_binary:
            return self._read_binary_manifest()
        else:
            return self._read_text_manifest()

    def _read_text_manifest(self) -> ContainerManifest:
        first_line = self.file.readline()
        if not first_line:
            raise ContainerFormatError("Empty container file.")
        if first_line.strip() != TEXT_MAGIC_START:
            raise ContainerFormatError(
                f"Invalid container magic: expected '{TEXT_MAGIC_START}', got '{first_line.strip()}'"
            )

        json_lines: List[str] = []
        while True:
            line = self.file.readline()
            if not line:
                raise ContainerFormatError("Unexpected EOF while reading container manifest.")
            if line.strip() == TEXT_MANIFEST_END:
                break
            json_lines.append(line)

        manifest_str = "".join(json_lines).strip()
        try:
            data = json.loads(manifest_str)
            return ContainerManifest.from_dict(data)
        except Exception as e:
            raise ContainerFormatError(f"Corrupted manifest JSON: {e}") from e

    def _read_binary_manifest(self) -> ContainerManifest:
        magic = self.file.read(len(BIN_MAGIC_START))
        if magic != BIN_MAGIC_START:
            raise ContainerFormatError(f"Invalid binary container magic: {magic}")

        len_bytes = self.file.read(4)
        if len(len_bytes) < 4:
            raise ContainerFormatError("Premature EOF reading binary manifest length.")
        manifest_len = struct.unpack(">I", len_bytes)[0]
        json_bytes = self.file.read(manifest_len)
        try:
            data = json.loads(json_bytes.decode("utf-8"))
            return ContainerManifest.from_dict(data)
        except Exception as e:
            raise ContainerFormatError(f"Corrupted binary manifest JSON: {e}") from e

    def iter_chunks(self) -> Iterator[Tuple[ChunkHeader, bytes]]:
        """Yield (ChunkHeader, raw_uncompressed_bytes) chunk by chunk."""
        if self.is_binary:
            yield from self._iter_binary_chunks()
        else:
            yield from self._iter_text_chunks()

    def _iter_text_chunks(self) -> Iterator[Tuple[ChunkHeader, bytes]]:
        expected_index = 0
        while True:
            line = self.file.readline()
            if not line:
                break
            sline = line.strip()
            if not sline:
                continue
            if sline == TEXT_MAGIC_END:
                break
            if sline.startswith(TEXT_CHUNK_START):
                header = ChunkHeader.from_header_line(sline)
                if header.index != expected_index:
                    raise ContainerFormatError(
                        f"Chunk sequence gap: expected chunk {expected_index}, found {header.index}"
                    )

                text_lines: List[str] = []
                end_marker = f"{TEXT_CHUNK_END}{header.index}-----"
                while True:
                    payload_line = self.file.readline()
                    if not payload_line:
                        raise ContainerFormatError(f"Premature EOF in chunk {header.index}")
                    sp = payload_line.strip()
                    if sp == end_marker:
                        break
                    text_lines.append(sp)

                encoded_text = "".join(text_lines)
                try:
                    compressed_bytes = decode_text(encoded_text, header.text_encoding)
                except Exception as e:
                    raise ContainerFormatError(f"Text decoding failed in chunk {header.index}: {e}") from e

                codec = CodecRegistry.get(header.codec)
                try:
                    raw_bytes = codec.decode(compressed_bytes)
                except Exception as e:
                    raise ContainerFormatError(f"Codec decompression failed in chunk {header.index}: {e}") from e

                actual_sha256 = compute_sha256(raw_bytes)
                if actual_sha256 != header.chunk_sha256:
                    raise IntegrityError(
                        f"Chunk {header.index} SHA-256 mismatch: expected {header.chunk_sha256}, got {actual_sha256}"
                    )
                if len(raw_bytes) != header.raw_size:
                    raise IntegrityError(
                        f"Chunk {header.index} size mismatch: expected {header.raw_size}, got {len(raw_bytes)}"
                    )

                expected_index += 1
                yield header, raw_bytes

        if expected_index != self.manifest.total_chunks:
            raise ContainerFormatError(
                f"Total chunks mismatch: manifest specified {self.manifest.total_chunks}, but {expected_index} were read"
            )

    def _iter_binary_chunks(self) -> Iterator[Tuple[ChunkHeader, bytes]]:
        expected_index = 0
        while True:
            chk_magic = self.file.read(4)
            if not chk_magic:
                break
            if chk_magic == BIN_MAGIC_END[:4]:
                # Trailing end marker
                break
            if chk_magic != BIN_CHUNK_MAGIC:
                raise ContainerFormatError(f"Invalid chunk magic: {chk_magic}")

            header_bytes = self.file.read(13)
            if len(header_bytes) < 13:
                raise ContainerFormatError("Premature EOF in binary chunk header.")
            index, raw_size, comp_size, codec_len = struct.unpack(">IIIB", header_bytes)

            if index != expected_index:
                raise ContainerFormatError(f"Chunk gap: expected {expected_index}, got {index}")

            codec_bytes = self.file.read(codec_len)
            codec_name = codec_bytes.decode("utf-8")

            raw_sha256_bytes = self.file.read(32)
            chunk_sha256 = raw_sha256_bytes.hex()

            header = ChunkHeader(
                index=index,
                raw_size=raw_size,
                compressed_size=comp_size,
                codec=codec_name,
                text_encoding="none",
                chunk_sha256=chunk_sha256,
            )

            compressed_bytes = self.file.read(comp_size)
            if len(compressed_bytes) != comp_size:
                raise ContainerFormatError(f"Chunk {index} data truncated: expected {comp_size}, got {len(compressed_bytes)}")

            codec = CodecRegistry.get(header.codec)
            try:
                raw_bytes = codec.decode(compressed_bytes)
            except Exception as e:
                raise ContainerFormatError(f"Decompression failed in binary chunk {index}: {e}") from e

            actual_sha256 = compute_sha256(raw_bytes)
            if actual_sha256 != header.chunk_sha256:
                raise IntegrityError(
                    f"Binary Chunk {header.index} SHA-256 mismatch: expected {header.chunk_sha256}, got {actual_sha256}"
                )

            expected_index += 1
            yield header, raw_bytes

        if expected_index != self.manifest.total_chunks:
            raise ContainerFormatError(
                f"Total chunks mismatch in binary container: expected {self.manifest.total_chunks}, got {expected_index}"
            )
