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


class CompositeCodec(Codec):
    """Wraps a base compression codec with an invertible preconditioning transform."""

    def __init__(self, base_codec: Codec, transform_name: str):
        self._base = base_codec
        self._transform_name = transform_name.lower()

    @property
    def name(self) -> str:
        return f"{self._base.name}+{self._transform_name}"

    def encode(self, data: bytes) -> bytes:
        from ziptext.transforms.aspd import apply_transform
        transformed = apply_transform(data, self._transform_name)
        return self._base.encode(transformed)

    def decode(self, data: bytes) -> bytes:
        from ziptext.transforms.aspd import invert_transform
        decompressed = self._base.decode(data)
        return invert_transform(decompressed, self._transform_name)


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
        """Instantiate and return a codec by name (supports 'base+transform' composite syntax)."""
        key = name.lower()
        if "+" in key:
            base_part, transform_part = key.split("+", 1)
            base_codec = cls.get(base_part)
            from ziptext.transforms.aspd import TRANSFORM_REGISTRY
            if transform_part not in TRANSFORM_REGISTRY and transform_part not in ("none", "raw", ""):
                raise ValueError(f"Unknown transform '{transform_part}' in composite codec '{name}'.")
            return CompositeCodec(base_codec, transform_part)

        if key not in cls._codecs:
            available = ", ".join(cls._codecs.keys())
            raise ValueError(f"Codec '{name}' not found. Available codecs: {available}")
        return cls._codecs[key]()

    @classmethod
    def is_available(cls, name: str) -> bool:
        """Check if a codec is registered and available."""
        key = name.lower()
        if "+" in key:
            base_part, transform_part = key.split("+", 1)
            from ziptext.transforms.aspd import TRANSFORM_REGISTRY
            return cls.is_available(base_part) and (
                transform_part in TRANSFORM_REGISTRY or transform_part in ("none", "raw", "")
            )
        return key in cls._codecs

    @classmethod
    def available_codecs(cls) -> List[str]:
        """List names of all registered base codecs."""
        return sorted(list(cls._codecs.keys()))

