"""Benchmark comparison matrix runner for Zip Text."""

import csv
import json
import os
import shutil
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ziptext.codecs.base import CodecRegistry
from ziptext.engine import ZipTextEngine
from ziptext.utils import compute_file_sha256, format_bytes
from ziptext.validator import MediaValidator


@dataclass
class MatrixResultRow:
    file_name: str
    file_type: str
    original_size_bytes: int
    chunk_size_bytes: int
    policy: str
    codecs_used: str
    encoded_size_bytes: int
    size_change_pct: float
    ratio: float
    encode_time_ms: float
    decode_time_ms: float
    peak_memory_kib: float
    exact_match: bool
    media_valid: bool
    media_format: str
    original_sha256: str
    reconstructed_sha256: str


class MatrixRunner:
    """Executes the full test matrix across fixtures, codecs, and chunk sizes."""

    DEFAULT_CHUNK_SIZES = [262144, 1048576]  # 256 KiB and 1 MiB
    DEFAULT_POLICIES = ["raw", "zlib", "bz2", "lzma", "lz4", "auto"]

    def __init__(
        self,
        fixtures_dir: Union[str, Path],
        output_dir: Union[str, Path],
        chunk_sizes: Optional[List[int]] = None,
        policies: Optional[List[str]] = None,
        profile: str = "text",
    ):
        self.fixtures_dir = Path(fixtures_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.chunk_sizes = chunk_sizes or self.DEFAULT_CHUNK_SIZES
        self.policies = policies or self.DEFAULT_POLICIES
        self.profile = profile
        self.engine = ZipTextEngine()

    def run(self) -> List[MatrixResultRow]:
        """Run all test combinations and return collected result rows."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        fixture_files = sorted([f for f in self.fixtures_dir.iterdir() if f.is_file()])
        if not fixture_files:
            raise FileNotFoundError(f"No fixture files found in {self.fixtures_dir}")

        # Filter policies according to available codecs
        available_policies = []
        for p in self.policies:
            if p == "auto" or CodecRegistry.is_available(p):
                available_policies.append(p)

        results: List[MatrixResultRow] = []
        scratch_dir = Path(tempfile.mkdtemp(prefix="ziptext_matrix_"))

        try:
            total_cases = len(fixture_files) * len(available_policies) * len(self.chunk_sizes)
            container_ext = ".ztxt" if self.profile == "text" else ".zbin"
            print(f"Starting Zip Text Benchmark Matrix [{self.profile.upper()} profile]: {total_cases} total test cases...")

            case_idx = 0
            for file_path in fixture_files:
                original_size = file_path.stat().st_size
                original_sha256 = compute_file_sha256(file_path)
                file_type = file_path.suffix.lstrip(".").lower() or "bin"

                for chunk_size in self.chunk_sizes:
                    for policy in available_policies:
                        case_idx += 1
                        container_path = scratch_dir / f"test_{case_idx}{container_ext}"
                        recovered_path = scratch_dir / f"recovered_{case_idx}{file_path.suffix}"

                        # Encode
                        t0 = time.perf_counter()
                        enc_res = self.engine.encode_file(
                            input_path=file_path,
                            output_path=container_path,
                            codec=policy,
                            chunk_size=chunk_size,
                            encoding="base85",
                            profile=self.profile,
                        )
                        enc_time_ms = (time.perf_counter() - t0) * 1000.0

                        # Decode
                        t1 = time.perf_counter()
                        dec_res = self.engine.decode_file(
                            input_path=container_path,
                            output_path=recovered_path,
                        )
                        dec_time_ms = (time.perf_counter() - t1) * 1000.0

                        recovered_sha256 = compute_file_sha256(recovered_path)
                        exact_match = (original_sha256 == recovered_sha256)

                        # Validate recovered media integrity
                        val_report = MediaValidator.validate(recovered_path)
                        media_valid = val_report.is_valid
                        media_format = val_report.format_name

                        codecs_str = "+".join(
                            f"{k}:{v}" for k, v in sorted(enc_res.codec_distribution.items())
                        ) if enc_res.codec_distribution else policy

                        peak_mem_kib = max(enc_res.peak_memory_rss, dec_res.peak_memory_rss) / 1024.0

                        row = MatrixResultRow(
                            file_name=file_path.name,
                            file_type=file_type,
                            original_size_bytes=original_size,
                            chunk_size_bytes=chunk_size,
                            policy=policy,
                            codecs_used=codecs_str,
                            encoded_size_bytes=enc_res.encoded_size,
                            size_change_pct=enc_res.size_change_pct,
                            ratio=enc_res.ratio,
                            encode_time_ms=enc_time_ms,
                            decode_time_ms=dec_time_ms,
                            peak_memory_kib=peak_mem_kib,
                            exact_match=exact_match,
                            media_valid=media_valid,
                            media_format=media_format,
                            original_sha256=original_sha256,
                            reconstructed_sha256=recovered_sha256,
                        )
                        results.append(row)

                        # Clean up temp files for this iteration
                        if container_path.exists():
                            container_path.unlink()
                        if recovered_path.exists():
                            recovered_path.unlink()

                        status_sym = "[OK]" if (exact_match and media_valid) else "[FAIL]"
                        print(
                            f"[{case_idx}/{total_cases}] {status_sym} {file_path.name:<18} "
                            f"| chunk={chunk_size//1024:>4}K | policy={policy:<5} "
                            f"| {format_bytes(original_size):>8} -> {format_bytes(enc_res.encoded_size):>8} "
                            f"({enc_res.size_change_pct:+.1f}%) | {media_format}"
                        )

            # Export JSON and CSV
            self._export_results(results)

        finally:
            shutil.rmtree(scratch_dir, ignore_errors=True)

        return results

    def _export_results(self, results: List[MatrixResultRow]) -> None:
        """Write matrix_results.json and matrix_results.csv."""
        suffix = f"_{self.profile}" if self.profile != "text" else ""
        json_path = self.output_dir / f"matrix_results{suffix}.json"
        csv_path = self.output_dir / f"matrix_results{suffix}.csv"

        # CSV export
        fieldnames = [
            "file_name",
            "file_type",
            "original_size_bytes",
            "chunk_size_bytes",
            "policy",
            "codecs_used",
            "encoded_size_bytes",
            "size_change_pct",
            "ratio",
            "encode_time_ms",
            "decode_time_ms",
            "peak_memory_kib",
            "exact_match",
            "media_valid",
            "media_format",
            "original_sha256",
            "reconstructed_sha256",
        ]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(asdict(r))

        # JSON export
        passed_count = sum(1 for r in results if r.exact_match and r.media_valid)
        summary = {
            "profile": self.profile,
            "total_cases": len(results),
            "exact_round_trips": passed_count,
            "pass_rate_pct": (passed_count / len(results) * 100.0) if results else 0.0,
            "policies_tested": self.policies,
            "chunk_sizes_tested": self.chunk_sizes,
            "results": [asdict(r) for r in results],
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"\n[Matrix Complete] {passed_count}/{len(results)} cases passed byte-for-byte & media integrity verification.")
        print(f"Results saved to: {csv_path} and {json_path}")
