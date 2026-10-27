"""Generate small invented PDFs: a hand-written text page and Pillow image-only pages (stage 3).

Used by the scanned fixture generator and by the doctor's OCR smoke page. No system font is read:
image pages use Pillow's bundled font. Output bytes are stable for fixed inputs and versions.
"""

from pathlib import Path
import time

from PIL import Image, ImageDraw, ImageFont

DPI = 300
PAGE_PX = (2550, 3300)          # Letter at 300 dpi
BODY_PX = 44
STAMP_PX = 60
JPEG_QUALITY = 90
MARGIN_PX = 300
LINE_PX = 80
STAMP_Y = 3000


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def text_pdf(lines: list[str], *, size: int = 14, left: int = 72, top: int = 720) -> bytes:
    """One Letter page, Helvetica (not embedded), one Tj per line, with a valid xref table."""
    leading = size + 6
    ops = ["BT", f"/F1 {size} Tf"]
    y = top
    for line in lines:
        ops.append(f"1 0 0 1 {left} {y} Tm ({_escape(line)}) Tj")
        y -= leading
    ops.append("ET")
    stream = "\n".join(ops).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n").encode()
    return bytes(out)


def render_page(lines: list[str], stamps: list[tuple[str, str]]) -> Image.Image:
    """A white 300 dpi greyscale page with dark body lines and stamps at the bottom.

    Each stamp is (text, "center" or "right"). No text layer exists: this is pixels only.
    """
    page = Image.new("L", PAGE_PX, 255)
    draw = ImageDraw.Draw(page)
    body = ImageFont.load_default(size=BODY_PX)
    y = MARGIN_PX
    for line in lines:
        draw.text((MARGIN_PX, y), line, font=body, fill=0)
        y += LINE_PX
    stamp_font = ImageFont.load_default(size=STAMP_PX)
    for text, anchor in stamps:
        width = draw.textlength(text, font=stamp_font)
        if anchor == "center":
            x = (PAGE_PX[0] - width) / 2
        elif anchor == "right":
            x = PAGE_PX[0] - MARGIN_PX - width
        else:
            raise ValueError(f"unknown stamp anchor {anchor}")
        draw.text((x, STAMP_Y), text, font=stamp_font, fill=0)
    return page


def image_pdf(pages: list[Image.Image], out_path: Path) -> None:
    """Save image-only pages as one PDF with fixed dates (byte-stable for one basename)."""
    if not pages:
        raise ValueError("no pages")
    stamp = time.gmtime(0)
    pages[0].save(out_path, "PDF", resolution=float(DPI), save_all=True, append_images=pages[1:],
                  quality=JPEG_QUALITY, creationDate=stamp, modDate=stamp)
