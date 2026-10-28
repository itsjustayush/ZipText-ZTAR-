"""Shannon Entropy and Information Density estimation utilities."""

import math
from collections import Counter
from typing import Sequence, Union


def compute_shannon_entropy(data: Union[bytes, bytearray, Sequence[int]]) -> float:
    """Calculate 0-order empirical Shannon entropy in bits per byte (0.0 to 8.0).
    
    H(X) = - sum(p(x) * log2(p(x))) for all x in alphabet
    """
    n = len(data)
    if n == 0:
        return 0.0

    counts = Counter(data)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        entropy -= p * math.log2(p)
    return entropy
