"""Corpora manager and downloader for established compression benchmarks."""

import io
import shutil
import tarfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

CANTERBURY_URL = "https://corpus.canterbury.ac.nz/resources/cantrbry.tar.gz"

CANTERBURY_FILES = [
    "alice29.txt",
    "asyoulik.txt",
    "cp.html",
    "fields.c",
    "grammar.lsp",
    "kennedy.xls",
    "lcet10.txt",
    "plrabn12.txt",
    "ptt5",
    "sum",
    "xargs.1",
]


class CorporaManager:
    """Manages downloading, caching, and verification of external benchmark corpora."""

    @classmethod
    def fetch_canterbury_corpus(cls, target_dir: Optional[Path] = None) -> Path:
        """Download and extract the canonical Canterbury Corpus."""
        dest = Path(target_dir) if target_dir else Path("fixtures/canterbury")
        dest.mkdir(parents=True, exist_ok=True)

        # Check if already downloaded
        existing = [f.name for f in dest.iterdir() if f.is_file()]
        if all(cf in existing for cf in CANTERBURY_FILES):
            print(f"Canterbury Corpus already present in: {dest}")
            return dest

        print(f"Fetching Canterbury Corpus from {CANTERBURY_URL}...")
        req = urllib.request.Request(
            CANTERBURY_URL,
            headers={"User-Agent": "ZipText-Benchmark-Agent/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()

        with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as tar:
            tar.extractall(path=dest)

        extracted = [f.name for f in dest.iterdir() if f.is_file()]
        print(f"Successfully unpacked {len(extracted)} files to {dest}")
        return dest
