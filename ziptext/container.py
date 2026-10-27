"""Zip Text Container (.ztxt) format specification, streaming parser, and serializer."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, Optional, TextIO, Tuple, Union

from ziptext.codecs.base import CodecRegistry
from ziptext.text_encodings import decode_text, encode_text
from ziptext.utils import compute_sha256

CONTAINER_MAGIC_START = "-----BEGIN ZIPTEXT CONTAINER v0.1.0-----"
CONTAINER_MAGIC_END = "-----END ZIPTEXT CONTAINER-----"
MANIFEST_END_MARKER = "-----END MANIFEST-----"
CHUNK_START_PREFIX = "-----BEGIN CHUNK "
CHUNK_END_PREFIX = "-----END CHUNK "

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
            f"{CHUNK_START_PREFIX}{self.index} "
            f"raw_size={self.raw_size} "
            f"compressed_size={self.compressed_size} "
            f"codec={self.codec} "
            f"encoding={self.text_encoding} "
            f"sha256={self.chunk_sha256}-----"
        )

    @classmethod
    def from_header_line(cls, line: str) -> "ChunkHeader":
        line = line.strip()
        if not line.startswith(CHUNK_START_PREFIX) or not line.endswith("-----"):
            raise ContainerFormatError(f"Malformed chunk header line: {line}")
        inner = line[len(CHUNK_START_PREFIX):-len("-----")].strip()
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


class ContainerWriter:
    """Streaming writer for creating .ztxt container files."""

    def __init__(self, out_file: TextIO, manifest: ContainerManifest):
        self.out = out_file
        self.manifest = manifest
        self._chunks_written = 0
        self._write_header()

    def _write_header(self) -> None:
        self.out.write(CONTAINER_MAGIC_START + "\n")
        self.out.write(self.manifest.to_json() + "\n")
        self.out.write(MANIFEST_END_MARKER + "\n")

    def write_chunk(
        self,
        index: int,
        raw_size: int,
        compressed_bytes: bytes,
        codec_name: str,
        text_encoding: str,
        raw_sha256: str,
    ) -> int:
        """Write a single encoded chunk and return serialized characters written."""
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

        # Wrap text in chunks of LINE_WRAP_WIDTH characters
        for i in range(0, len(encoded_text), LINE_WRAP_WIDTH):
            line = encoded_text[i:i + LINE_WRAP_WIDTH] + "\n"
            self.out.write(line)
            chars_written += len(line)

        end_line = f"{CHUNK_END_PREFIX}{index}-----\n"
        self.out.write(end_line)
        chars_written += len(end_line)

        self._chunks_written += 1
        return chars_written

    def close(self) -> None:
        """Write final container terminator."""
        self.out.write(CONTAINER_MAGIC_END + "\n")


class ContainerReader:
    """Streaming reader for reading and verifying .ztxt container files."""

    def __init__(self, in_file: TextIO):
        self.file = in_file
        self.manifest = self._read_manifest()

    def _read_manifest(self) -> ContainerManifest:
        first_line = self.file.readline()
        if not first_line:
            raise ContainerFormatError("Empty container file.")
        if first_line.strip() != CONTAINER_MAGIC_START:
            raise ContainerFormatError(
                f"Invalid container magic: expected '{CONTAINER_MAGIC_START}', got '{first_line.strip()}'"
            )

        json_lines: List[str] = []
        while True:
            line = self.file.readline()
            if not line:
                raise ContainerFormatError("Unexpected EOF while reading container manifest.")
            if line.strip() == MANIFEST_END_MARKER:
                break
            json_lines.append(line)

        manifest_str = "".join(json_lines).strip()
        try:
            data = json.loads(manifest_str)
            return ContainerManifest.from_dict(data)
        except Exception as e:
            raise ContainerFormatError(f"Corrupted manifest JSON: {e}") from e

    def iter_chunks(self) -> Iterator[Tuple[ChunkHeader, bytes]]:
        """Yield (ChunkHeader, raw_uncompressed_bytes) chunk by chunk."""
        expected_index = 0
        while True:
            line = self.file.readline()
            if not line:
                break
            sline = line.strip()
            if not sline:
                continue
            if sline == CONTAINER_MAGIC_END:
                break
            if sline.startswith(CHUNK_START_PREFIX):
                header = ChunkHeader.from_header_line(sline)
                if header.index != expected_index:
                    raise ContainerFormatError(
                        f"Chunk sequence gap: expected chunk {expected_index}, found {header.index}"
                    )

                text_lines: List[str] = []
                end_marker = f"{CHUNK_END_PREFIX}{header.index}-----"
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
