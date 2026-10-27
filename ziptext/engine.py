"""Zip Text Engine for adaptive chunked encoding, decoding, and verification."""

import hashlib
import os
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ziptext.codecs.base import CodecRegistry
from ziptext.container import (
    ContainerManifest,
    ContainerReader,
    ContainerWriter,
    IntegrityError,
    ZipTextError,
)
from ziptext.text_encodings import encode_text
from ziptext.utils import MemoryTracker, compute_file_sha256, compute_sha256
from ziptext.validator import MediaValidator, ValidationReport


@dataclass
class EncodeResult:
    """Detailed summary of an encoding operation."""
    input_path: Path
    output_path: Path
    original_size: int
    encoded_size: int
    ratio: float  # encoded / original
    size_change_pct: float  # ((encoded - original) / original) * 100
    chunk_size: int
    total_chunks: int
    policy: str
    text_encoding: str
    file_sha256: str
    codec_distribution: Dict[str, int]
    duration_seconds: float
    peak_memory_rss: int
    profile: str = "text"


@dataclass
class DecodeResult:
    """Detailed summary of a decoding operation."""
    input_path: Path
    output_path: Path
    file_size: int
    total_chunks: int
    file_sha256: str
    reconstructed_sha256: str
    exact_match: bool
    duration_seconds: float
    peak_memory_rss: int
    original_filename: str = ""
    media_format_info: Optional[str] = None
    validation: Optional[ValidationReport] = None


class ZipTextEngine:
    """Core ZTAR processing engine."""

    def __init__(self):
        pass

    def _select_adaptive_codec(
        self,
        raw_bytes: bytes,
        encoding: str = "base85",
        candidate_codecs: Optional[List[str]] = None,
        is_binary_profile: bool = False,
    ) -> Tuple[str, bytes]:
        """Test candidate codecs and pick the one with smallest serialized representation."""
        if candidate_codecs is None:
            candidate_codecs = CodecRegistry.available_codecs()

        best_codec = "raw"
        best_comp_bytes = raw_bytes

        if is_binary_profile:
            best_size = len(raw_bytes)
        else:
            best_size = len(encode_text(raw_bytes, encoding))

        for c_name in candidate_codecs:
            if c_name == "raw":
                continue
            try:
                codec = CodecRegistry.get(c_name)
                comp_bytes = codec.encode(raw_bytes)

                if is_binary_profile:
                    candidate_size = len(comp_bytes)
                else:
                    candidate_size = len(encode_text(comp_bytes, encoding))

                # Strictly smaller representation
                if candidate_size < best_size:
                    best_size = candidate_size
                    best_codec = c_name
                    best_comp_bytes = comp_bytes
            except Exception:
                continue

        return best_codec, best_comp_bytes

    def encode_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        codec: str = "auto",
        chunk_size: int = 1048576,
        encoding: str = "base85",
        profile: str = "auto",
    ) -> EncodeResult:
        """Encode a file into a Zip Text container (.ztxt text or .zbin binary)."""
        in_p = Path(input_path).resolve()
        out_p = Path(output_path).resolve()

        if not in_p.is_file():
            raise FileNotFoundError(f"Input file not found: {in_p}")

        out_p.parent.mkdir(parents=True, exist_ok=True)

        # Resolve container profile
        if profile == "auto":
            effective_profile = "binary" if out_p.suffix.lower() == ".zbin" else "text"
        else:
            effective_profile = profile.lower()

        original_size = in_p.stat().st_size
        file_sha256 = compute_file_sha256(in_p)

        # Handle empty file edge-case
        total_chunks = max(1, (original_size + chunk_size - 1) // chunk_size) if original_size > 0 else 0

        manifest = ContainerManifest(
            version="0.1.0",
            filename=in_p.name,
            file_size=original_size,
            file_sha256=file_sha256,
            chunk_size=chunk_size,
            total_chunks=total_chunks,
            policy=codec,
            default_encoding=encoding if effective_profile == "text" else "none",
            profile=effective_profile,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        codec_distribution: Dict[str, int] = {}
        is_bin = (effective_profile == "binary")

        with MemoryTracker() as mem:
            open_mode = "wb" if is_bin else "w"
            open_kwargs = {} if is_bin else {"encoding": "utf-8"}

            with open(out_p, open_mode, **open_kwargs) as out_f:
                writer = ContainerWriter(out_f, manifest, profile=effective_profile)

                if original_size > 0:
                    with open(in_p, "rb") as in_f:
                        chunk_idx = 0
                        while True:
                            raw_chunk = in_f.read(chunk_size)
                            if not raw_chunk:
                                break

                            chunk_sha256 = compute_sha256(raw_chunk)

                            if codec == "auto":
                                chosen_codec, comp_bytes = self._select_adaptive_codec(
                                    raw_chunk,
                                    encoding=encoding,
                                    is_binary_profile=is_bin,
                                )
                            else:
                                chosen_codec = codec.lower()
                                c_inst = CodecRegistry.get(chosen_codec)
                                comp_bytes = c_inst.encode(raw_chunk)

                            writer.write_chunk(
                                index=chunk_idx,
                                raw_size=len(raw_chunk),
                                compressed_bytes=comp_bytes,
                                codec_name=chosen_codec,
                                text_encoding=encoding,
                                raw_sha256=chunk_sha256,
                            )

                            codec_distribution[chosen_codec] = codec_distribution.get(chosen_codec, 0) + 1
                            chunk_idx += 1
                            mem.poll()

                writer.close()

        encoded_size = out_p.stat().st_size
        ratio = (encoded_size / original_size) if original_size > 0 else 1.0
        size_change_pct = ((encoded_size - original_size) / original_size * 100.0) if original_size > 0 else 0.0

        return EncodeResult(
            input_path=in_p,
            output_path=out_p,
            original_size=original_size,
            encoded_size=encoded_size,
            ratio=ratio,
            size_change_pct=size_change_pct,
            chunk_size=chunk_size,
            total_chunks=total_chunks,
            policy=codec,
            text_encoding=encoding if effective_profile == "text" else "none",
            file_sha256=file_sha256,
            codec_distribution=codec_distribution,
            duration_seconds=mem.elapsed_time,
            peak_memory_rss=mem.peak_rss,
            profile=effective_profile,
        )

    def decode_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
    ) -> DecodeResult:
        """Decode a Zip Text container (.ztxt or .zbin) into the reconstructed file with integrity verification."""
        in_p = Path(input_path).resolve()

        if not in_p.is_file():
            raise FileNotFoundError(f"Container file not found: {in_p}")

        # Use ContainerReader.open which handles both text (.ztxt) and binary (.zbin) transparently
        with ContainerReader.open(in_p) as reader:
            manifest = reader.manifest

            if output_path is None:
                out_p = in_p.parent / f"recovered_{manifest.filename}"
            else:
                out_p = Path(output_path).resolve()

            out_p.parent.mkdir(parents=True, exist_ok=True)
            temp_out = out_p.with_suffix(out_p.suffix + ".ztmp")

            with MemoryTracker() as mem:
                hasher = hashlib.sha256()
                total_written = 0
                chunks_processed = 0

                try:
                    with open(temp_out, "wb") as out_f:
                        for header, raw_chunk in reader.iter_chunks():
                            hasher.update(raw_chunk)
                            out_f.write(raw_chunk)
                            total_written += len(raw_chunk)
                            chunks_processed += 1
                            mem.poll()

                    reconstructed_sha256 = hasher.hexdigest()

                    # Verify overall file size and whole-file SHA-256
                    if total_written != manifest.file_size:
                        raise IntegrityError(
                            f"Reconstructed file size mismatch: expected {manifest.file_size} bytes, got {total_written} bytes"
                        )

                    if reconstructed_sha256 != manifest.file_sha256:
                        raise IntegrityError(
                            f"Whole-file SHA-256 mismatch!\nExpected: {manifest.file_sha256}\nComputed: {reconstructed_sha256}"
                        )

                    # Atomic replace on success
                    if temp_out.exists():
                        shutil.move(str(temp_out), str(out_p))

                except Exception:
                    if temp_out.exists():
                        temp_out.unlink()
                    raise

        exact_match = (reconstructed_sha256 == manifest.file_sha256)
        validation_rep = MediaValidator.validate(out_p)
        media_info = f"{validation_rep.format_name} - {validation_rep.details}"

        return DecodeResult(
            input_path=in_p,
            output_path=out_p,
            file_size=total_written,
            total_chunks=chunks_processed,
            file_sha256=manifest.file_sha256,
            reconstructed_sha256=reconstructed_sha256,
            exact_match=exact_match,
            duration_seconds=mem.elapsed_time,
            peak_memory_rss=mem.peak_rss,
            original_filename=manifest.filename,
            media_format_info=media_info,
            validation=validation_rep,
        )

    def verify_file(self, container_path: Union[str, Path]) -> Dict[str, Any]:
        """Verify integrity of all chunks and whole-file hash without writing to disk."""
        p = Path(container_path).resolve()
        hasher = hashlib.sha256()
        total_bytes = 0
        chunks_count = 0

        with ContainerReader.open(p) as reader:
            manifest = reader.manifest
            for header, raw_chunk in reader.iter_chunks():
                hasher.update(raw_chunk)
                total_bytes += len(raw_chunk)
                chunks_count += 1

        computed_sha256 = hasher.hexdigest()
        exact = (computed_sha256 == manifest.file_sha256) and (total_bytes == manifest.file_size)

        return {
            "valid": exact,
            "manifest": manifest,
            "chunks_verified": chunks_count,
            "total_bytes": total_bytes,
            "expected_sha256": manifest.file_sha256,
            "computed_sha256": computed_sha256,
            "profile": manifest.profile,
        }
