"""The generated PDFs: a stdlib text page and Pillow image-only pages."""

import io
from pathlib import Path

import pytest
from pypdf import PdfReader

from casefile import pdfsmoke


def read(data):
    return PdfReader(io.BytesIO(data))


def test_text_pdf_and_image_pdf(tmp_path, capsys):
    lines = ["Invented line (one) with parens", "Second line \\ slash"]
    reader = read(pdfsmoke.text_pdf(lines))
    text = reader.pages[0].extract_text()
    # pypdf is forgiving, so also require a proper text object: BT, one Tj per line, ET.
    operators = [op for _, op in reader.pages[0].get_contents().operations]
    text_ok = (len(reader.pages) == 1 and all(line in text for line in lines)
               and operators.count(b"BT") == 1 and operators.count(b"ET") == 1
               and operators.count(b"Tj") == len(lines) and operators.index(b"BT") < operators.index(b"ET"))
    out = tmp_path / "smoke.pdf"
    pdfsmoke.image_pdf([pdfsmoke.render_page(["CASEFILE OCR SMOKE 7342"], [])], out)
    images = PdfReader(str(out))
    layer = (images.pages[0].extract_text() or "").strip()
    with capsys.disabled():
        print(f"pdfsmoke text_ok={int(text_ok)} image_pages={len(images.pages)} "
              f"image_text_layer={len(layer)}")
    assert text_ok
    assert len(images.pages) == 1 and layer == ""
    assert len(list(images.pages[0].images)) == 1


def test_image_pdf_is_byte_stable(tmp_path):
    page = lambda: pdfsmoke.render_page(["Invented text"], [("KMR2342", "center"), ("TWP7731", "right")])
    first, second = tmp_path / "a" / "x.pdf", tmp_path / "b" / "x.pdf"
    for target in (first, second):
        target.parent.mkdir()
        pdfsmoke.image_pdf([page()], target)
    assert first.read_bytes() == second.read_bytes()


def test_render_page_rejects_unknown_anchor_and_empty_pdf(tmp_path):
    with pytest.raises(ValueError, match="unknown stamp anchor"):
        pdfsmoke.render_page([], [("KMR2342", "left")])
    with pytest.raises(ValueError, match="no pages"):
        pdfsmoke.image_pdf([], tmp_path / "x.pdf")


def test_render_page_is_300_dpi_greyscale_with_dark_pixels():
    page = pdfsmoke.render_page(["Invented text"], [("KMR2342", "center")])
    assert page.mode == "L" and page.size == (2550, 3300)
    assert page.getextrema() == (0, 255)
    assert pdfsmoke.render_page([], []).getextrema() == (255, 255)
