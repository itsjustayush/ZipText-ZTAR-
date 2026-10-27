"""Base codec abstractions and registry for Zip Text."""

from abc import ABC, abstractmethod
from typing import Dict, List, Type


class Codec(ABC):
    """Abstract base class for all compression codecs."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name of the codec."""
        pass

    @abstractmethod
    def encode(self, data: bytes) -> bytes:
        """Compress raw byte sequence."""
        pass

    @abstractmethod
    def decode(self, data: bytes) -> bytes:
        """Decompress compressed byte sequence."""
        pass


class CodecRegistry:
    """Registry maintaining available compression codecs."""

    _codecs: Dict[str, Type[Codec]] = {}

    @classmethod
    def register(cls, codec_cls: Type[Codec]) -> Type[Codec]:
        """Register a codec class."""
        instance = codec_cls()
        cls._codecs[instance.name.lower()] = codec_cls
        return codec_cls

    @classmethod
    def get(cls, name: str) -> Codec:
        """Instantiate and return a codec by name."""
        key = name.lower()
        if key not in cls._codecs:
            available = ", ".join(cls._codecs.keys())
            raise ValueError(f"Codec '{name}' not found. Available codecs: {available}")
        return cls._codecs[key]()

    @classmethod
    def is_available(cls, name: str) -> bool:
        """Check if a codec is registered and available."""
        return name.lower() in cls._codecs

    @classmethod
    def available_codecs(cls) -> List[str]:
        """List names of all registered codecs."""
        return sorted(list(cls._codecs.keys()))
