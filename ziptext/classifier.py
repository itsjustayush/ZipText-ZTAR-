"""File type classification and viability advisor for Zip Text."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, Union


class FileCategory:
    TEXT_CONFIG = "Text & Configuration"
    VECTOR_IMAGE = "Vector Graphics"
    RAW_MEDIA = "Uncompressed Media / Audio"
    LOSSY_RASTER = "Lossy Raster Images"
    LOSSLESS_RASTER = "Lossless Raster Images"
    MEDIA_CONTAINER = "Audio & Video Media Containers"
    COMPOUND_DOCUMENT = "Documents & Office Formats"
    ARCHIVE_EXECUTABLE = "Archives & Executables"
    GENERIC_BINARY = "Generic Binary Data"


@dataclass
class ClassificationResult:
    category: str
    extension: str
    description: str
    ziptext_viability_text: str  # Rating in .ztxt mode (Base85)
    ziptext_viability_binary: str  # Rating in .zbin mode (Binary)
    recommended_profile: str
    expected_size_delta: str
    technical_notes: str


_EXTENSION_MAP: Dict[str, Tuple[str, str, str, str, str, str, str]] = {
    # Data & Config
    ".json": (
        FileCategory.TEXT_CONFIG,
        "Structured JSON configuration/data",
        "Excellent (-60% to -85%)",
        "Superior (-70% to -90%)",
        "text",
        "-70% to -90%",
        "High character redundancy; whitespace and repeated key dictionaries compress efficiently.",
    ),
    ".xml": (
        FileCategory.TEXT_CONFIG,
        "Extensible Markup Language document",
        "Excellent (-70% to -90%)",
        "Superior (-75% to -92%)",
        "text",
        "-75% to -92%",
        "Repeated closing/opening tags and schema headers collapse under LZMA/Zlib.",
    ),
    ".yaml": (
        FileCategory.TEXT_CONFIG,
        "YAML configuration file",
        "Excellent (-60% to -85%)",
        "Superior (-70% to -90%)",
        "text",
        "-70% to -90%",
        "Structured indentation and repeated properties compress readily.",
    ),
    ".yml": (
        FileCategory.TEXT_CONFIG,
        "YAML configuration file",
        "Excellent (-60% to -85%)",
        "Superior (-70% to -90%)",
        "text",
        "-70% to -90%",
        "Structured indentation and repeated properties compress readily.",
    ),
    ".csv": (
        FileCategory.TEXT_CONFIG,
        "Comma-Separated Values tabular data",
        "Exceptional (-85% to -98%)",
        "Exceptional (-90% to -99%)",
        "text",
        "-90% to -98%",
        "Columnar alignment and repeated tabular fields yield massive dictionary deduplication.",
    ),
    # Source Code & Text
    ".py": (
        FileCategory.TEXT_CONFIG,
        "Python source code",
        "Excellent (-70% to -90%)",
        "Superior (-75% to -92%)",
        "text",
        "-75% to -92%",
        "Keyword syntax, indentation patterns, and identifiers yield high compression.",
    ),
    ".js": (
        FileCategory.TEXT_CONFIG,
        "JavaScript source code",
        "Excellent (-65% to -85%)",
        "Superior (-70% to -90%)",
        "text",
        "-70% to -90%",
        "Repeated function syntax, DOM APIs, and boilerplate compress heavily.",
    ),
    ".ts": (
        FileCategory.TEXT_CONFIG,
        "TypeScript source code",
        "Excellent (-70% to -90%)",
        "Superior (-75% to -92%)",
        "text",
        "-75% to -92%",
        "Interface declarations and type annotations add compressible structure.",
    ),
    ".html": (
        FileCategory.TEXT_CONFIG,
        "HTML web document",
        "Excellent (-75% to -90%)",
        "Superior (-80% to -92%)",
        "text",
        "-80% to -92%",
        "DOM tag hierarchies and styling attributes compress efficiently.",
    ),
    ".css": (
        FileCategory.TEXT_CONFIG,
        "CSS stylesheet",
        "Excellent (-70% to -88%)",
        "Superior (-75% to -90%)",
        "text",
        "-75% to -90%",
        "Repeated rule blocks, selectors, and property names compress tightly.",
    ),
    ".txt": (
        FileCategory.TEXT_CONFIG,
        "Plain text prose / documentation",
        "Very Good (-50% to -85%)",
        "Superior (-60% to -90%)",
        "text",
        "-60% to -90%",
        "Natural language n-gram frequencies provide predictable redundancy.",
    ),
    ".md": (
        FileCategory.TEXT_CONFIG,
        "Markdown document",
        "Very Good (-50% to -85%)",
        "Superior (-60% to -90%)",
        "text",
        "-60% to -90%",
        "Prose and structured markdown headings compress well.",
    ),
    ".log": (
        FileCategory.TEXT_CONFIG,
        "Application / server log file",
        "Exceptional (-85% to -98%)",
        "Exceptional (-90% to -99%)",
        "text",
        "-90% to -99%",
        "Repeating timestamps, log levels, and message formats collapse rapidly.",
    ),
    # Vector Graphics
    ".svg": (
        FileCategory.VECTOR_IMAGE,
        "Scalable Vector Graphics (XML)",
        "Excellent (-70% to -90%)",
        "Superior (-75% to -92%)",
        "text",
        "-75% to -92%",
        "XML coordinate paths and curve points compress like standard text.",
    ),
    # Raw Raster & Audio
    ".bmp": (
        FileCategory.RAW_MEDIA,
        "Uncompressed Windows Bitmap image",
        "Excellent (-60% to -90%)",
        "Superior (-70% to -95%)",
        "binary",
        "-70% to -95%",
        "Uncompressed raster pixel matrices have high spatial correlation across scanlines.",
    ),
    ".ppm": (
        FileCategory.RAW_MEDIA,
        "Uncompressed Netpbm Portable Pixmap",
        "Excellent (-70% to -93%)",
        "Superior (-75% to -95%)",
        "binary",
        "-75% to -95%",
        "Raw RGB scanlines compress heavily prior to any container packaging.",
    ),
    ".wav": (
        FileCategory.RAW_MEDIA,
        "Uncompressed Linear PCM audio",
        "Good (-30% to -60%)",
        "Very Good (-40% to -70%)",
        "binary",
        "-40% to -70%",
        "Waveform sample periodicity compresses moderately with general-purpose LZ codecs.",
    ),
    # Lossy Raster Images
    ".jpg": (
        FileCategory.LOSSY_RASTER,
        "JPEG lossy photo format",
        "Poor (+25% to +33% bloat)",
        "Neutral (0% to +0.5%)",
        "binary",
        "0% (binary) / +28% (text)",
        "Already compressed via DCT + Huffman coding; text mode suffers Base85 expansion.",
    ),
    ".jpeg": (
        FileCategory.LOSSY_RASTER,
        "JPEG lossy photo format",
        "Poor (+25% to +33% bloat)",
        "Neutral (0% to +0.5%)",
        "binary",
        "0% (binary) / +28% (text)",
        "Already compressed via DCT + Huffman coding; text mode suffers Base85 expansion.",
    ),
    ".webp": (
        FileCategory.LOSSY_RASTER,
        "WebP optimized image format",
        "Poor (+25% to +33% bloat)",
        "Neutral (0% to +0.5%)",
        "binary",
        "0% (binary) / +28% (text)",
        "High-density arithmetic compression pre-applied; incompressible further.",
    ),
    # Lossless Raster Images
    ".png": (
        FileCategory.LOSSLESS_RASTER,
        "Portable Network Graphics (DEFLATE)",
        "Poor (+22% to +30% bloat)",
        "Neutral (-2% to +1%)",
        "binary",
        "0% to -2% (binary) / +25% (text)",
        "Internal IDAT streams are already zlib compressed; binary profile avoids Base85 bloat.",
    ),
    ".gif": (
        FileCategory.LOSSLESS_RASTER,
        "GIF palette image / animation (LZW)",
        "Poor (+22% to +30% bloat)",
        "Neutral (-1% to +1%)",
        "binary",
        "0% (binary) / +25% (text)",
        "LZW compression pre-applied; Base85 introduces textual overhead.",
    ),
    # Video & Audio Media Containers
    ".mp4": (
        FileCategory.MEDIA_CONTAINER,
        "MPEG-4 Part 14 video container (H.264/AAC)",
        "Terrible (+25% to +33% bloat)",
        "Neutral (0% to +0.3%)",
        "binary",
        "0% (binary) / +28% (text)",
        "Pre-compressed dense entropy streams; text encoding causes mandatory +25% expansion.",
    ),
    ".mov": (
        FileCategory.MEDIA_CONTAINER,
        "QuickTime movie container",
        "Terrible (+25% to +33% bloat)",
        "Neutral (0% to +0.3%)",
        "binary",
        "0% (binary) / +28% (text)",
        "Pre-compressed video stream; binary profile recommended.",
    ),
    ".mkv": (
        FileCategory.MEDIA_CONTAINER,
        "Matroska multimedia container",
        "Terrible (+25% to +33% bloat)",
        "Neutral (0% to +0.3%)",
        "binary",
        "0% (binary) / +28% (text)",
        "High entropy audiovisual tracks; text mode causes Base85 inflation.",
    ),
    ".webm": (
        FileCategory.MEDIA_CONTAINER,
        "WebM open media format (VP8/VP9/Opus)",
        "Terrible (+25% to +33% bloat)",
        "Neutral (0% to +0.3%)",
        "binary",
        "0% (binary) / +28% (text)",
        "Heavily compressed entropy streams.",
    ),
    ".mp3": (
        FileCategory.MEDIA_CONTAINER,
        "MPEG-1 Audio Layer III",
        "Terrible (+25% to +33% bloat)",
        "Neutral (0% to +0.3%)",
        "binary",
        "0% (binary) / +28% (text)",
        "Perceptually coded psychoacoustic audio stream; incompressible.",
    ),
    ".flac": (
        FileCategory.MEDIA_CONTAINER,
        "Free Lossless Audio Codec",
        "Poor (+22% to +30% bloat)",
        "Neutral (-1% to +0.5%)",
        "binary",
        "0% (binary) / +25% (text)",
        "Linear prediction residuals are already compressed.",
    ),
    ".aac": (
        FileCategory.MEDIA_CONTAINER,
        "Advanced Audio Coding stream",
        "Terrible (+25% to +33% bloat)",
        "Neutral (0% to +0.3%)",
        "binary",
        "0% (binary) / +28% (text)",
        "MDCT compressed audio packets.",
    ),
    # Documents
    ".pdf": (
        FileCategory.COMPOUND_DOCUMENT,
        "Portable Document Format",
        "Moderate to High (-15% to -87%)",
        "High (-25% to -90%)",
        "binary",
        "-15% to -87%",
        "Mix of uncompressed text content streams and pre-compressed embedded JPEGs.",
    ),
    ".docx": (
        FileCategory.COMPOUND_DOCUMENT,
        "Microsoft Word OpenXML document",
        "Poor to Neutral (+15% to +28% bloat in text)",
        "Slight (-2% to -10% in binary)",
        "binary",
        "-5% (binary) / +25% (text)",
        "Actually a ZIP archive of XML and media files; recompressing with LZMA gives minor gains.",
    ),
    ".xlsx": (
        FileCategory.COMPOUND_DOCUMENT,
        "Microsoft Excel OpenXML spreadsheet",
        "Poor to Neutral (+15% to +28% bloat in text)",
        "Slight (-5% to -15% in binary)",
        "binary",
        "-8% (binary) / +22% (text)",
        "ZIP archive containing shared strings and sheet XML.",
    ),
    ".pptx": (
        FileCategory.COMPOUND_DOCUMENT,
        "Microsoft PowerPoint OpenXML presentation",
        "Poor (+20% to +30% bloat in text)",
        "Neutral (-1% to +2% in binary)",
        "binary",
        "0% (binary) / +25% (text)",
        "ZIP archive typically dominated by embedded media images.",
    ),
    # Archives & Executables
    ".zip": (
        FileCategory.ARCHIVE_EXECUTABLE,
        "Standard ZIP archive",
        "Terrible (+25% to +33% bloat in text)",
        "Neutral (0% to -3% in binary)",
        "binary",
        "0% (binary) / +28% (text)",
        "Already compressed payload blocks; text mode causes Base85 expansion.",
    ),
    ".gz": (
        FileCategory.ARCHIVE_EXECUTABLE,
        "Gzip compressed tarball/stream",
        "Terrible (+25% to +33% bloat in text)",
        "Neutral (0% to +0.2% in binary)",
        "binary",
        "0% (binary) / +28% (text)",
        "Pre-compressed DEFLATE stream.",
    ),
    ".rar": (
        FileCategory.ARCHIVE_EXECUTABLE,
        "RAR proprietary archive",
        "Terrible (+25% to +33% bloat in text)",
        "Neutral (0% in binary)",
        "binary",
        "0% (binary) / +28% (text)",
        "Proprietary high-density compression pre-applied.",
    ),
    ".exe": (
        FileCategory.ARCHIVE_EXECUTABLE,
        "Windows Portable Executable binary",
        "Neutral to Good (-10% to -40% in binary)",
        "Moderate (+10% to +25% in text)",
        "binary",
        "-20% to -40% (binary)",
        "Machine code, resource tables, and relocations compress moderately under LZMA/XZ.",
    ),
    ".dll": (
        FileCategory.ARCHIVE_EXECUTABLE,
        "Windows Dynamic Link Library",
        "Neutral to Good (-10% to -45% in binary)",
        "Moderate (+10% to +25% in text)",
        "binary",
        "-20% to -45% (binary)",
        "Export tables and compiled x86/x64 opcodes compress well under LZMA.",
    ),
    ".so": (
        FileCategory.ARCHIVE_EXECUTABLE,
        "Linux Shared Object library",
        "Neutral to Good (-15% to -50% in binary)",
        "Moderate (+5% to +20% in text)",
        "binary",
        "-25% to -50% (binary)",
        "ELF symbols and unstripped debug sections yield good compression in binary mode.",
    ),
}


def classify_file(file_path: Union[str, Path]) -> ClassificationResult:
    """Classify any file and provide technical viability assessment and profile recommendation."""
    p = Path(file_path)
    ext = p.suffix.lower()

    if ext in _EXTENSION_MAP:
        cat, desc, viab_text, viab_bin, rec_prof, exp_delta, notes = _EXTENSION_MAP[ext]
        return ClassificationResult(
            category=cat,
            extension=ext,
            description=desc,
            ziptext_viability_text=viab_text,
            ziptext_viability_binary=viab_bin,
            recommended_profile=rec_prof,
            expected_size_delta=exp_delta,
            technical_notes=notes,
        )

    # Fallback for unknown extensions: inspect binary heuristics
    return ClassificationResult(
        category=FileCategory.GENERIC_BINARY,
        extension=ext or "none",
        description="Arbitrary binary or unspecified data format",
        ziptext_viability_text="Variable (+28% if high entropy, -50% if redundant)",
        ziptext_viability_binary="Adaptive (0% to -80% depending on entropy)",
        recommended_profile="binary",
        expected_size_delta="Variable",
        technical_notes="Adaptive engine will test candidate codecs chunk-by-chunk.",
    )
