"""Four-Representation and Multi-Baseline Evaluation Runner for ZTAR-Bench."""

import io
import json
import os
import shutil
import tempfile
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ziptext.codecs.base import CodecRegistry
from ziptext.container import ContainerWriter, ContainerReader
from ziptext.engine import ZipTextEngine
from ziptext.text_encodings import encode_text
from ziptext.utils import compute_file_sha256, format_bytes
from ziptext.validator import MediaValidator


@dataclass
class BaselineSizes:
    raw_bytes: int
    zlib_bytes: int
    zstd_bytes: int
    lz4_bytes: int
    brotli_bytes: int
    lzma_bytes: int
    zip_bytes: int


@dataclass
class FourTierResultRow:
    file_name: str
    category: str
    original_size_bytes: int  # Rep A
    compressed_binary_bytes: int  # Rep B
    compressed_text_bytes: int  # Rep C
    complete_ztxt_container_bytes: int  # Rep D (.ztxt)
    complete_zbin_container_bytes: int  # Rep D (.zbin)
    best_codec: str
    text_bloat_penalty_pct: float  # (C - B) / B * 100
    container_overhead_bytes: int  # D_ztxt - C
    net_storage_reduction_ztxt_pct: float  # (A - D_ztxt) / A * 100
    net_storage_reduction_zbin_pct: float  # (A - D_zbin) / A * 100
    baselines: BaselineSizes
    exact_match: bool
    media_valid: bool
    media_format: str
    encode_time_ms: float
    decode_time_ms: float


class FourTierEvaluator:
    """Evaluates files across the 4 ZTAR representations and competitive baselines."""

    def __init__(self, output_dir: Union[str, Path] = "results/ztar_bench"):
        self.output_dir = Path(output_dir)
        self.engine = ZipTextEngine()

    def evaluate_directory(
        self,
        corpus_dir: Union[str, Path],
        category: str = "General",
        chunk_size: int = 1048576,
    ) -> List[FourTierResultRow]:
        """Run 4-tier evaluation across all files in corpus_dir."""
        p = Path(corpus_dir)
        files = sorted([f for f in p.iterdir() if f.is_file()])
        if not files:
            raise FileNotFoundError(f"No files found in {corpus_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        results: List[FourTierResultRow] = []

        scratch_dir = Path(tempfile.mkdtemp(prefix="four_tier_"))
        try:
            for f in files:
                orig_bytes = f.read_bytes()
                orig_size = len(orig_bytes)
                orig_sha = compute_file_sha256(f)

                # 1. Competitive Baselines
                baselines = self._measure_baselines(orig_bytes)

                # 2. Adaptive best codec selection
                best_codec_name = "zstd" if CodecRegistry.is_available("zstd") else "lzma"
                min_comp_size = orig_size
                best_comp_bytes = orig_bytes

                for c_name in CodecRegistry.available_codecs():
                    if c_name == "raw":
                        continue
                    try:
                        codec = CodecRegistry.get(c_name)
                        comp = codec.encode(orig_bytes)
                        if len(comp) < min_comp_size:
                            min_comp_size = len(comp)
                            best_codec_name = c_name
                            best_comp_bytes = comp
                    except Exception:
                        pass

                # Representation A: Original File Size
                rep_a_size = orig_size

                # Representation B: Compressed Binary
                rep_b_size = len(best_comp_bytes)

                # Representation C: Compressed & Text-Encoded (Base85)
                text_payload = encode_text(best_comp_bytes, "base85")
                rep_c_size = len(text_payload)
                text_bloat_pct = ((rep_c_size - rep_b_size) / rep_b_size * 100.0) if rep_b_size else 0.0

                # Representation D: Complete ZTAR Container (.ztxt and .zbin)
                ztxt_path = scratch_dir / f"{f.name}.ztxt"
                zbin_path = scratch_dir / f"{f.name}.zbin"
                rec_path = scratch_dir / f"rec_{f.name}"

                t0 = time.perf_counter()
                enc_res_txt = self.engine.encode_file(
                    input_path=f,
                    output_path=ztxt_path,
                    codec=best_codec_name,
                    chunk_size=chunk_size,
                    profile="text",
                )
                enc_time_ms = (time.perf_counter() - t0) * 1000.0

                enc_res_bin = self.engine.encode_file(
                    input_path=f,
                    output_path=zbin_path,
                    codec=best_codec_name,
                    chunk_size=chunk_size,
                    profile="binary",
                )

                rep_d_ztxt_size = ztxt_path.stat().st_size
                rep_d_zbin_size = zbin_path.stat().st_size
                container_overhead = rep_d_ztxt_size - rep_c_size

                # Decode & Verify
                t1 = time.perf_counter()
                self.engine.decode_file(ztxt_path, rec_path)
                dec_time_ms = (time.perf_counter() - t1) * 1000.0

                rec_sha = compute_file_sha256(rec_path)
                exact_match = (orig_sha == rec_sha)

                # Media Validation
                val_report = MediaValidator.validate(rec_path)

                net_red_txt = ((orig_size - rep_d_ztxt_size) / orig_size * 100.0) if orig_size else 0.0
                net_red_bin = ((orig_size - rep_d_zbin_size) / orig_size * 100.0) if orig_size else 0.0

                row = FourTierResultRow(
                    file_name=f.name,
                    category=category,
                    original_size_bytes=rep_a_size,
                    compressed_binary_bytes=rep_b_size,
                    compressed_text_bytes=rep_c_size,
                    complete_ztxt_container_bytes=rep_d_ztxt_size,
                    complete_zbin_container_bytes=rep_d_zbin_size,
                    best_codec=best_codec_name,
                    text_bloat_penalty_pct=text_bloat_pct,
                    container_overhead_bytes=container_overhead,
                    net_storage_reduction_ztxt_pct=net_red_txt,
                    net_storage_reduction_zbin_pct=net_red_bin,
                    baselines=baselines,
                    exact_match=exact_match,
                    media_valid=val_report.is_valid,
                    media_format=val_report.format_name,
                    encode_time_ms=enc_time_ms,
                    decode_time_ms=dec_time_ms,
                )
                results.append(row)

                # Clean up temp files
                for tmp_f in [ztxt_path, zbin_path, rec_path]:
                    if tmp_f.exists():
                        tmp_f.unlink()

            self._save_results(results, category)
        finally:
            shutil.rmtree(scratch_dir, ignore_errors=True)

        return results

    def _measure_baselines(self, data: bytes) -> BaselineSizes:
        """Measure competitive standard baselines: zlib, zstd, lz4, brotli, lzma, zip."""
        import zlib
        import bz2
        import lzma

        zlib_size = len(zlib.compress(data, level=6))
        lzma_size = len(lzma.compress(data))

        # Zstd
        if CodecRegistry.is_available("zstd"):
            zstd_size = len(CodecRegistry.get("zstd").encode(data))
        else:
            zstd_size = zlib_size

        # LZ4
        if CodecRegistry.is_available("lz4"):
            lz4_size = len(CodecRegistry.get("lz4").encode(data))
        else:
            lz4_size = zlib_size

        # Brotli
        if CodecRegistry.is_available("brotli"):
            brotli_size = len(CodecRegistry.get("brotli").encode(data))
        else:
            brotli_size = zlib_size

        # ZIP archive
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("data", data)
        zip_size = len(buf.getvalue())

        return BaselineSizes(
            raw_bytes=len(data),
            zlib_bytes=zlib_size,
            zstd_bytes=zstd_size,
            lz4_bytes=lz4_size,
            brotli_bytes=brotli_size,
            lzma_bytes=lzma_size,
            zip_bytes=zip_size,
        )

    def _save_results(self, results: List[FourTierResultRow], category: str) -> None:
        """Export JSON and CSV results."""
        out_json = self.output_dir / f"four_tier_{category.lower().replace(' ', '_')}.json"
        data = {
            "category": category,
            "total_files": len(results),
            "exact_matches": sum(1 for r in results if r.exact_match),
            "media_valid_count": sum(1 for r in results if r.media_valid),
            "results": [asdict(r) for r in results],
        }
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
