"""Adaptive Structured Preconditioning & Deinterleaving (ASPD).

Provides mathematically bijective, invertible transforms for structured data:
- Delta-k (stride differentials for audio/image/time-series)
- Byte-Plane Deinterleaving (splits multi-byte words into significance planes)
- Combined Plane-Delta transforms
- Entropy-guarded gating to guarantee monotonic compression improvement with zero overfitting.
"""

from typing import Callable, Dict, List, Optional, Tuple
from ziptext.transforms.entropy import compute_shannon_entropy


def delta_encode(data: bytes, stride: int = 1) -> bytes:
    """Forward stride differential: d_i = (x_i - x_{i-stride}) mod 256."""
    n = len(data)
    if n <= stride:
        return data
    out = bytearray(n)
    # Prefix remains untouched
    out[:stride] = data[:stride]
    for i in range(stride, n):
        out[i] = (data[i] - data[i - stride]) & 0xFF
    return bytes(out)


def delta_decode(data: bytes, stride: int = 1) -> bytes:
    """Inverse stride differential: x_i = (d_i + x_{i-stride}) mod 256."""
    n = len(data)
    if n <= stride:
        return data
    out = bytearray(n)
    out[:stride] = data[:stride]
    for i in range(stride, n):
        out[i] = (data[i] + out[i - stride]) & 0xFF
    return bytes(out)


def deinterleave(data: bytes, stride: int = 2) -> bytes:
    """Deinterleave multi-byte words into contiguous significance byte planes."""
    n = len(data)
    if stride <= 1 or n < stride:
        return data
    out = bytearray(n)
    ptr = 0
    for s in range(stride):
        for i in range(s, n, stride):
            out[ptr] = data[i]
            ptr += 1
    return bytes(out)


def interleave(data: bytes, stride: int = 2) -> bytes:
    """Invert byte plane deinterleaving back into original interleaved sequence."""
    n = len(data)
    if stride <= 1 or n < stride:
        return data
    out = bytearray(n)
    ptr = 0
    for s in range(stride):
        for i in range(s, n, stride):
            out[i] = data[ptr]
            ptr += 1
    return bytes(out)


def plane_delta_encode(data: bytes, stride: int = 2) -> bytes:
    """Deinterleave bytes by stride, then apply sequential delta within each plane."""
    n = len(data)
    if stride <= 1 or n < stride:
        return data
    planes = bytearray(deinterleave(data, stride))
    # Calculate boundary size for each plane
    plane_len = n // stride
    rem = n % stride
    offset = 0
    for s in range(stride):
        cur_len = plane_len + (1 if s < rem else 0)
        plane_slice = planes[offset : offset + cur_len]
        planes[offset : offset + cur_len] = delta_encode(bytes(plane_slice), stride=1)
        offset += cur_len
    return bytes(planes)


def plane_delta_decode(data: bytes, stride: int = 2) -> bytes:
    """Inverse per-plane delta, then interleave planes back into original sequence."""
    n = len(data)
    if stride <= 1 or n < stride:
        return data
    planes = bytearray(data)
    plane_len = n // stride
    rem = n % stride
    offset = 0
    for s in range(stride):
        cur_len = plane_len + (1 if s < rem else 0)
        plane_slice = planes[offset : offset + cur_len]
        planes[offset : offset + cur_len] = delta_decode(bytes(plane_slice), stride=1)
        offset += cur_len
    return interleave(bytes(planes), stride)


TRANSFORM_REGISTRY: Dict[str, Tuple[Callable[[bytes], bytes], Callable[[bytes], bytes]]] = {
    "delta1": (lambda d: delta_encode(d, 1), lambda d: delta_decode(d, 1)),
    "delta2": (lambda d: delta_encode(d, 2), lambda d: delta_decode(d, 2)),
    "delta3": (lambda d: delta_encode(d, 3), lambda d: delta_decode(d, 3)),
    "delta4": (lambda d: delta_encode(d, 4), lambda d: delta_decode(d, 4)),
    "plane2": (lambda d: deinterleave(d, 2), lambda d: interleave(d, 2)),
    "plane4": (lambda d: deinterleave(d, 4), lambda d: interleave(d, 4)),
    "pdelta2": (lambda d: plane_delta_encode(d, 2), lambda d: plane_delta_decode(d, 2)),
    "pdelta4": (lambda d: plane_delta_encode(d, 4), lambda d: plane_delta_decode(d, 4)),
}


def apply_transform(data: bytes, transform_name: str) -> bytes:
    """Apply a named reversible preconditioning transform."""
    if not transform_name or transform_name.lower() in ("none", "raw", ""):
        return data
    t_name = transform_name.lower()
    if t_name not in TRANSFORM_REGISTRY:
        raise ValueError(f"Unknown transform: '{transform_name}'. Available: {list(TRANSFORM_REGISTRY.keys())}")
    encoder, _ = TRANSFORM_REGISTRY[t_name]
    return encoder(data)


def invert_transform(data: bytes, transform_name: str) -> bytes:
    """Invert a named preconditioning transform back to original byte stream."""
    if not transform_name or transform_name.lower() in ("none", "raw", ""):
        return data
    t_name = transform_name.lower()
    if t_name not in TRANSFORM_REGISTRY:
        raise ValueError(f"Unknown transform: '{transform_name}'. Available: {list(TRANSFORM_REGISTRY.keys())}")
    _, decoder = TRANSFORM_REGISTRY[t_name]
    return decoder(data)


class ASPDTransform:
    """Adaptive Structured Preconditioning & Deinterleaving Manager."""

    @classmethod
    def evaluate_candidates(
        cls,
        data: bytes,
        compress_fn: Callable[[bytes], bytes],
        candidate_transforms: Optional[List[str]] = None,
        entropy_margin: float = 0.05,
    ) -> Tuple[str, bytes, bytes]:
        """Entropy-guarded selection of best preconditioning transform.
        
        Returns:
            (best_transform_name, transformed_raw_bytes, compressed_bytes)
        """
        if len(data) < 64:
            # For micro chunks (< 64 bytes), preconditioning overhead exceeds benefit
            raw_comp = compress_fn(data)
            return "none", data, raw_comp

        if candidate_transforms is None:
            candidate_transforms = ["pdelta2", "pdelta4", "delta1", "delta2", "delta3", "delta4", "plane2"]

        # Baseline
        base_entropy = compute_shannon_entropy(data)
        base_comp = compress_fn(data)
        best_size = len(base_comp)
        best_transform = "none"
        best_transformed = data
        best_comp = base_comp

        # Quick candidate screening via Shannon entropy gate
        viable_candidates = []
        for t_name in candidate_transforms:
            try:
                encoder, _ = TRANSFORM_REGISTRY[t_name]
                transformed = encoder(data)
                t_entropy = compute_shannon_entropy(transformed)
                # Gate 1: Transform must lower 0-order entropy by at least margin
                if t_entropy < (base_entropy - entropy_margin):
                    viable_candidates.append((t_name, transformed, t_entropy))
            except Exception:
                continue

        # Sort viable candidates by lowest entropy first
        viable_candidates.sort(key=lambda x: x[2])

        # Gate 2: Test empirical compressed size
        for t_name, transformed, _ in viable_candidates:
            try:
                cand_comp = compress_fn(transformed)
                if len(cand_comp) < best_size:
                    best_size = len(cand_comp)
                    best_transform = t_name
                    best_transformed = transformed
                    best_comp = cand_comp
            except Exception:
                continue

        return best_transform, best_transformed, best_comp
