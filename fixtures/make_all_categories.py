import io
import json
import math
import os
import tarfile
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

out = Path("fixtures/all_categories")
out.mkdir(parents=True, exist_ok=True)

# 1. Text & Configuration
(out / "data.json").write_text(
    json.dumps(
        {"status": "ok", "version": "1.0", "records": [{"id": i, "val": f"val_{i % 10}"} for i in range(400)]},
        indent=2,
    )
)
(out / "data.yaml").write_text(
    "status: ok\nversion: 1.0\nrecords:\n"
    + "\n".join(f"  - id: {i}\n    val: val_{i % 10}" for i in range(250))
)
(out / "config.xml").write_text(
    '<configuration><app name="ZipText"><settings>'
    + "".join(f'<property id="{i}" key="k_{i % 5}">val_{i}</property>' for i in range(300))
    + "</settings></app></configuration>"
)
(out / "table.csv").write_text(
    "id,name,category,score\n"
    + "\n".join(f"{i},Item_{i % 20},Category_{i % 5},{80 + (i % 20)}" for i in range(800))
)

# Source code
(out / "source.py").write_text(
    "def compute(n: int) -> int:\n    total = 0\n    for i in range(n):\n        total += (i * 3) % 7\n    return total\n\n"
    * 50
)
(out / "script.js").write_text(
    "function processData(items) {\n    return items.map(x => x.score * 1.5).filter(s => s > 100);\n}\n"
    * 60
)
(out / "types.ts").write_text(
    "export interface RecordItem {\n    id: number;\n    name: string;\n    tags: string[];\n    active: boolean;\n}\n"
    * 50
)
(out / "markup.html").write_text(
    "<!DOCTYPE html><html><head><title>Test</title></head><body>\n"
    + "".join(f"<div id='card-{i}' class='card'><h2>Item {i}</h2><p>Description for item {i}</p></div>\n" for i in range(150))
    + "</body></html>"
)
(out / "styles.css").write_text(
    ":root { --primary: #3b82f6; --bg: #0f172a; }\n"
    + "".join(f".card-{i} {{ padding: 12px; margin: 4px; border: 1px solid var(--primary); }}\n" for i in range(150))
)

# Plain text
(out / "notes.txt").write_text("Zip Text Universal File Type Test Suite.\n" * 400)
(out / "readme.md").write_text(
    "# Zip Text Research Benchmark\n\n"
    + "## Section\n- Item in list\n- Another bullet point\n\n```python\nprint('hello')\n```\n\n" * 80
)
(out / "system.log").write_text(
    "\n".join(f"2026-10-27T12:00:{i%60:02d}.000Z [INFO] worker-{i%4}: processed batch {i} status=SUCCESS" for i in range(600))
)

# 2. Vector & Raster Images
svg_circles = "\n".join(
    f'<circle cx="{(i * 10) % 500}" cy="{(i * 12) % 500}" r="{10 + (i % 30)}" fill="blue"/>'
    for i in range(250)
)
svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">\n{svg_circles}\n</svg>'
(out / "vector.svg").write_text(svg_content)

img = Image.new("RGB", (200, 200), (220, 240, 255))
d = ImageDraw.Draw(img)
for i in range(18):
    d.rectangle([i * 5, i * 5, 190 - i * 5, 190 - i * 5], outline=(i * 8 % 255, 100, 200))
img.save(out / "graphic.bmp", format="BMP")
img.save(out / "graphic.png", format="PNG")
img.save(out / "photo.jpg", format="JPEG", quality=85)
img.save(out / "image.webp", format="WEBP", quality=80)
img.save(out / "animation.gif", format="GIF")

# 3. Audio / Video (WAV & MP4)
sample_rate = 44100
samples = bytearray()
for i in range(sample_rate):
    val = int(16000 * math.sin(2 * math.pi * 440 * i / sample_rate))
    samples.extend(val.to_bytes(2, byteorder="little", signed=True))
wav_hdr = (
    b"RIFF"
    + (36 + len(samples)).to_bytes(4, "little")
    + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
    + sample_rate.to_bytes(4, "little")
    + (sample_rate * 2).to_bytes(4, "little")
    + b"\x02\x00\x10\x00data"
    + len(samples).to_bytes(4, "little")
)
(out / "audio.wav").write_bytes(wav_hdr + bytes(samples))

if Path("fixtures/synthetic.mp4").is_file():
    import shutil
    shutil.copy("fixtures/synthetic.mp4", out / "video.mp4")

# 4. Document / Office
docx_buf = io.BytesIO()
with zipfile.ZipFile(docx_buf, "w") as z:
    z.writestr(
        "[Content_Types].xml",
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/></Types>',
    )
    z.writestr(
        "word/document.xml",
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Zip Text Document Test</w:t></w:r></w:p></w:body></w:document>',
    )
(out / "document.docx").write_bytes(docx_buf.getvalue())

xlsx_buf = io.BytesIO()
with zipfile.ZipFile(xlsx_buf, "w") as z:
    z.writestr(
        "[Content_Types].xml",
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/></Types>',
    )
    z.writestr(
        "xl/workbook.xml",
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Sheet1" sheetId="1"/></sheets></workbook>',
    )
(out / "sheet.xlsx").write_bytes(xlsx_buf.getvalue())

if Path("fixtures/synthetic.pdf").is_file():
    shutil.copy("fixtures/synthetic.pdf", out / "document.pdf")

# 5. Archive & Binary
zip_buf = io.BytesIO()
with zipfile.ZipFile(zip_buf, "w") as z:
    z.writestr("file1.txt", "Hello inside archive")
    z.writestr("file2.txt", "Second file inside archive")
(out / "bundle.zip").write_bytes(zip_buf.getvalue())

tar_buf = io.BytesIO()
with tarfile.open(fileobj=tar_buf, mode="w:gz") as tar:
    tinfo = tarfile.TarInfo(name="archived.txt")
    data = b"Content inside compressed tar archive\n" * 50
    tinfo.size = len(data)
    tar.addfile(tinfo, io.BytesIO(data))
(out / "archive.tar.gz").write_bytes(tar_buf.getvalue())

dos_hdr = b"MZ" + b"\x00" * 58 + (0x40).to_bytes(4, "little")
pe_hdr = b"PE\x00\x00" + b"\x00" * 20
(out / "sample.exe").write_bytes(dos_hdr + pe_hdr + b"\x90" * 512)

print(f"Successfully generated {len(list(out.iterdir()))} test files across all categories:")
for f in sorted(out.iterdir()):
    print(f" - {f.name:18} ({f.stat().st_size:,} bytes)")
