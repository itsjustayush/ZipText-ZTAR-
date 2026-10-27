"""Utilities for hashing, memory tracking, and formatting."""

import hashlib
import os
import time
from pathlib import Path
from typing import Generator, Optional, Union
import psutil


def compute_sha256(data: bytes) -> str:
    """Compute hex SHA-256 digest of a byte sequence."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


def compute_file_sha256(file_path: Union[str, Path], chunk_size: int = 1048576) -> str:
    """Compute hex SHA-256 digest of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def format_bytes(size: Union[int, float]) -> str:
    """Format byte count into human-readable binary prefix units (KiB, MiB, GiB)."""
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    val = float(size)
    for unit in units:
        if abs(val) < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(val)} B"
            return f"{val:.2f} {unit}"
        val /= 1024.0
    return f"{val:.2f} TiB"


class MemoryTracker:
    """Context manager to measure peak resident set memory (RSS)."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_rss: int = 0
        self.peak_rss: int = 0
        self.delta_rss: int = 0
        self.start_time: float = 0.0
        self.elapsed_time: float = 0.0

    def __enter__(self) -> "MemoryTracker":
        self.start_time = time.perf_counter()
        self.start_rss = self.process.memory_info().rss
        self.peak_rss = self.start_rss
        return self

    def poll(self) -> None:
        """Poll current memory to update peak."""
        current = self.process.memory_info().rss
        if current > self.peak_rss:
            self.peak_rss = current

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.poll()
        self.elapsed_time = time.perf_counter() - self.start_time
        self.delta_rss = max(0, self.peak_rss - self.start_rss)
