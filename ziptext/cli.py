"""Command-line interface for Zip Text Lab (ZTAR)."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from ziptext import __version__
from ziptext.codecs.base import CodecRegistry
from ziptext.container import ContainerReader, IntegrityError, ZipTextError
from ziptext.engine import ZipTextEngine
from ziptext.fixtures import generate_corpus
from ziptext.matrix import MatrixRunner
from ziptext.utils import format_bytes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ziptext",
        description="Zip Text Adaptive Representation (ZTAR) - Research Prototype CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommand to execute")

    # fixtures subcommand
    p_fixtures = subparsers.add_parser("fixtures", help="Generate synthetic test corpus")
    p_fixtures.add_argument(
        "--output",
        "-o",
        type=str,
        default="fixtures",
        help="Directory to save generated test fixtures (default: fixtures)",
    )
    p_fixtures.add_argument(
        "--size-mb",
        type=float,
        default=4.0,
        help="Base size parameter in megabytes (default: 4.0)",
    )

    # matrix subcommand
    p_matrix = subparsers.add_parser("matrix", help="Run benchmark comparison matrix across fixtures")
    p_matrix.add_argument(
        "fixtures_dir",
        type=str,
        nargs="?",
        default="fixtures",
        help="Directory containing test fixtures",
    )
    p_matrix.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="results/matrix",
        help="Directory to store JSON and CSV benchmark reports (default: results/matrix)",
    )

    # encode subcommand
    p_encode = subparsers.add_parser("encode", help="Encode a file into a Zip Text container (.ztxt)")
    p_encode.add_argument("input", type=str, help="Source file path to encode")
    p_encode.add_argument("output", type=str, help="Destination .ztxt container path")
    p_encode.add_argument(
        "--codec",
        "-c",
        type=str,
        default="auto",
        help="Compression policy: 'auto', 'raw', 'zlib', 'bz2', 'lzma', 'lz4' (default: auto)",
    )
    p_encode.add_argument(
        "--chunk-size",
        "-s",
        type=int,
        default=1048576,
        help="Chunk size in bytes (default: 1048576 [1 MiB])",
    )
    p_encode.add_argument(
        "--encoding",
        "-e",
        type=str,
        default="base85",
        help="Text encoding: 'base85' or 'base64' (default: base85)",
    )

    # decode subcommand
    p_decode = subparsers.add_parser("decode", help="Decode a Zip Text container (.ztxt) into original file")
    p_decode.add_argument("input", type=str, help="Source .ztxt container path")
    p_decode.add_argument("output", type=str, help="Destination recovered file path")

    # verify subcommand
    p_verify = subparsers.add_parser("verify", help="Verify integrity of a Zip Text container (.ztxt)")
    p_verify.add_argument("input", type=str, help="Path to .ztxt container")

    # info subcommand
    p_info = subparsers.add_parser("info", help="Inspect metadata manifest of a Zip Text container")
    p_info.add_argument("input", type=str, help="Path to .ztxt container")

    return parser


def cmd_fixtures(args: argparse.Namespace) -> int:
    out_dir = Path(args.output)
    print(f"Generating synthetic test corpus in: {out_dir}...")
    paths = generate_corpus(out_dir, scale_mb=args.size_mb)
    print(f"Successfully generated {len(paths)} test fixtures:")
    for name, path in paths.items():
        print(f"  - {name:<22} ({format_bytes(path.stat().st_size)})")
    return 0


def cmd_matrix(args: argparse.Namespace) -> int:
    fixtures_dir = Path(args.fixtures_dir)
    if not fixtures_dir.exists():
        print(f"Fixtures directory '{fixtures_dir}' does not exist. Generating default fixtures first...")
        generate_corpus(fixtures_dir)

    runner = MatrixRunner(
        fixtures_dir=fixtures_dir,
        output_dir=args.output_dir,
    )
    rows = runner.run()
    failures = [r for r in rows if not r.exact_match]
    if failures:
        print(f"Warning: {len(failures)} cases failed exact verification!")
        return 1
    return 0


def cmd_encode(args: argparse.Namespace) -> int:
    engine = ZipTextEngine()
    print(f"Encoding '{args.input}' -> '{args.output}' [codec={args.codec}, chunk_size={args.chunk_size}]...")
    try:
        res = engine.encode_file(
            input_path=args.input,
            output_path=args.output,
            codec=args.codec,
            chunk_size=args.chunk_size,
            encoding=args.encoding,
        )
        print(f"Encoding complete in {res.duration_seconds:.3f}s:")
        print(f"  Original size:    {format_bytes(res.original_size)} ({res.original_size} bytes)")
        print(f"  Container size:   {format_bytes(res.encoded_size)} ({res.encoded_size} bytes)")
        print(f"  Size change:      {res.size_change_pct:+.2f}% (ratio: {res.ratio:.3f})")
        print(f"  Total chunks:     {res.total_chunks}")
        print(f"  Codecs used:      {res.codec_distribution}")
        print(f"  SHA-256:          {res.file_sha256}")
        return 0
    except Exception as e:
        print(f"Encoding failed: {e}", file=sys.stderr)
        return 1


def cmd_decode(args: argparse.Namespace) -> int:
    engine = ZipTextEngine()
    print(f"Decoding '{args.input}' -> '{args.output}' with byte-for-byte SHA-256 verification...")
    try:
        res = engine.decode_file(
            input_path=args.input,
            output_path=args.output,
        )
        print(f"Decoding successful in {res.duration_seconds:.3f}s:")
        print(f"  Recovered size:   {format_bytes(res.file_size)} ({res.file_size} bytes)")
        print(f"  Chunks verified:  {res.total_chunks}")
        print(f"  Reconstructed:    {res.reconstructed_sha256}")
        print(f"  Exact match:      {res.exact_match} (Lossless verified!)")
        return 0
    except IntegrityError as ie:
        print(f"INTEGRITY ERROR: {ie}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Decoding failed: {e}", file=sys.stderr)
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    engine = ZipTextEngine()
    print(f"Verifying container '{args.input}'...")
    try:
        res = engine.verify_file(args.input)
        if res["valid"]:
            print("Container integrity VERIFIED successfully!")
            print(f"  Original filename: {res['manifest'].filename}")
            print(f"  File size:         {format_bytes(res['total_bytes'])}")
            print(f"  Chunks verified:   {res['chunks_verified']}")
            print(f"  SHA-256 digest:    {res['computed_sha256']}")
            return 0
        else:
            print("Container verification FAILED (checksum mismatch).", file=sys.stderr)
            return 2
    except Exception as e:
        print(f"Verification error: {e}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    p = Path(args.input)
    if not p.is_file():
        print(f"File not found: {p}", file=sys.stderr)
        return 1
    with open(p, "r", encoding="utf-8") as f:
        reader = ContainerReader(f)
        m = reader.manifest
        print("=== Zip Text Container Manifest ===")
        print(f"Version:          {m.version}")
        print(f"Original File:    {m.filename}")
        print(f"File Size:        {format_bytes(m.file_size)} ({m.file_size} bytes)")
        print(f"SHA-256:          {m.file_sha256}")
        print(f"Chunk Size:       {format_bytes(m.chunk_size)} ({m.chunk_size} bytes)")
        print(f"Total Chunks:     {m.total_chunks}")
        print(f"Policy:           {m.policy}")
        print(f"Default Encoding: {m.default_encoding}")
        print(f"Created At:       {m.created_at}")
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "fixtures": cmd_fixtures,
        "matrix": cmd_matrix,
        "encode": cmd_encode,
        "decode": cmd_decode,
        "verify": cmd_verify,
        "info": cmd_info,
    }

    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
