"""Generate the invented six-page scanned fixture (matter 9002.001, binder scan).

    make_scanned.py --check     regenerate into a temp folder and compare with the committed PDF
    make_scanned.py --probe     run intake's OCR arguments on the committed PDF and score every page
    make_scanned.py [--out DIR] write scanned.pdf and scanned.json (a new PDF needs a new probe run
                                and the manifest sha in the same commit)

Every name, date and stamp below is invented. No scan, photo or real record is read or copied.
"""

import argparse
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "src"))

from pypdf import PdfReader, PdfWriter  # noqa: E402

from casefile import intake, pdfsmoke, quotes, stamps as stamp_finder  # noqa: E402

MATTER = "9002.001"
BINDER = "scan"
PDF_NAME = "scanned.pdf"          # the basename is the PDF /Title, so it is fixed
MANIFEST_NAME = "scanned.json"
STAMP_PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"
RATIO_FLOOR = 0.95

HEADER = ["Harrowgate Occupational Clinic", "Progress Note", ""]
PATIENT = "Patient: Delphine Okafor-Brandt   DOB 09/03/1979"

# kind: image (pixels only), blank (white sheet), text (born digital), mixed (pixels plus a digital
# stamp in the text layer). "stamps" are the stamps a reader should find; "drawn" are rendered into
# the pixels as (text, anchor); "digital" are lines of the text layer.
PAGES = [
    {"kind": "image",
     "lines": HEADER + [PATIENT, "Date of visit: 02/18/2026",
                        "Injury: 02/10/2026, lifting a crate at work.",
                        "Assessment: right shoulder strain.",
                        "Pain is 6 out of 10 at rest and with overhead reach.",
                        "Plan: ice, stretching and ibuprofen as needed.",
                        "Work status: no lifting over 10 pounds.",
                        "Seen by Dr. Rafael Soto-Lindgren."],
     "drawn": [("KMR2342", "center")], "stamps": ["KMR2342"],
     "must_contain": ["02/18/2026", "6 out of 10", "no lifting over 10 pounds"]},
    {"kind": "image",
     "lines": HEADER + [PATIENT, "Date of visit: 03/04/2026",
                        "Follow up for right shoulder strain.",
                        "Strength is improving and the brace is in use.",
                        "Patient is released to full duty with the brace.",
                        "Recheck in two weeks if pain returns.",
                        "Seen by Dr. Rafael Soto-Lindgren."],
     "drawn": [("KMR2343", "center")], "stamps": ["KMR2343"],
     "must_contain": ["03/04/2026", "released to full duty"]},
    {"kind": "image",
     "lines": ["Pinecrest Imaging", "Magnetic Resonance Report", "",
               PATIENT, "Study date: 02/25/2026", "Study: right shoulder without contrast.",
               "Findings: partial thickness tear of the supraspinatus tendon.",
               "No full thickness tear is seen.",
               "Impression: partial thickness tear, mild fluid in the bursa."],
     "drawn": [("KMR2344", "center"), ("TWP7731", "right")], "stamps": ["KMR2344", "TWP7731"],
     "must_contain": ["02/25/2026", "partial thickness"]},
    {"kind": "blank", "lines": [], "drawn": [], "stamps": [], "must_contain": []},
    {"kind": "text",
     "lines": ["Wexley Physical Therapy", "Plan of Care", "",
               "Patient: Delphine Okafor-Brandt", "Referred by Dr. Rafael Soto-Lindgren.",
               "Diagnosis: right shoulder strain.",
               "Frequency: two visits per week for four weeks.",
               "Goals: restore overhead reach and lifting strength.",
               "KMR2345"],
     "drawn": [], "stamps": ["KMR2345"], "must_contain": ["two visits per week for four weeks"]},
    {"kind": "mixed",
     "lines": ["Harrowgate Occupational Clinic", "Work Status Letter", "",
               PATIENT, "Date of letter: 03/12/2026",
               "The shoulder is healing as expected.",
               "Plan: return to work 03/16/2026 on light duty.",
               "Signed, Dr. Rafael Soto-Lindgren."],
     "drawn": [], "digital": ["KMR2346"], "stamps": ["KMR2346"],
     "must_contain": ["return to work 03/16/2026"]},
]


def expected_text(page):
    """The text a perfect reader would return for the page, in reading order."""
    if page["kind"] == "blank":
        return ""
    if page["kind"] == "text":
        return "\n".join(page["lines"])
    parts = [line for line in page["lines"]]
    parts += [text for text, _ in page["drawn"]] + page.get("digital", [])
    return "\n".join(parts)


def manifest(sha256):
    return {
        "matter": MATTER, "binder": BINDER, "file": PDF_NAME, "sha256": sha256,
        "pages": [{"page": n, "kind": p["kind"], "stamps": p["stamps"],
                   "must_contain": p["must_contain"], "text": expected_text(p)}
                  for n, p in enumerate(PAGES, 1)],
    }


def build_pdf_bytes():
    """Assemble the six pages into one PDF; the same inputs give the same bytes."""
    with tempfile.TemporaryDirectory() as tmp:
        images = []
        for page in PAGES:
            if page["kind"] == "text":
                images.append(None)
            else:
                images.append(pdfsmoke.render_page(page["lines"], page["drawn"]))
        image_indexes = [i for i, img in enumerate(images) if img is not None]
        scan_path = Path(tmp).resolve() / PDF_NAME
        pdfsmoke.image_pdf([images[i] for i in image_indexes], scan_path)
        scan_reader = PdfReader(str(scan_path))
        writer = PdfWriter()
        position = 0
        for i, page in enumerate(PAGES):
            if page["kind"] == "text":
                text_reader = PdfReader(io.BytesIO(pdfsmoke.text_pdf(page["lines"])))
                writer.add_page(text_reader.pages[0])
                continue
            added = writer.add_page(scan_reader.pages[position])
            position += 1
            if page["kind"] == "mixed":
                overlay = PdfReader(io.BytesIO(
                    pdfsmoke.text_pdf(page["digital"], left=270, top=50))).pages[0]
                added.merge_page(overlay)
        writer.add_metadata({"/Title": PDF_NAME})
        buffer = io.BytesIO()
        writer.write(buffer)
        return buffer.getvalue()


def build(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = build_pdf_bytes()
    (out_dir / PDF_NAME).write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    (out_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest(sha), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return sha


def content(pdf_bytes):
    """Per page: sha256 of decoded image pixels, text-layer text; plus the page count."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    for page in reader.pages:
        images = list(page.images)
        pixels = hashlib.sha256(images[0].image.tobytes()).hexdigest() if images else ""
        pages.append((pixels, (page.extract_text() or "").strip()))
    return len(reader.pages), pages


def check():
    committed = (HERE / PDF_NAME).read_bytes()
    fresh = build_pdf_bytes()
    bytes_equal = fresh == committed
    count_a, pages_a = content(committed)
    count_b, pages_b = content(fresh)
    different = [n for n, (a, b) in enumerate(zip(pages_a, pages_b), 1) if a != b]
    content_equal = count_a == count_b and not different
    print(f"check bytes_equal={int(bytes_equal)} content_equal={int(content_equal)}")
    if count_a != count_b:
        print(f"check pages committed={count_a} regenerated={count_b}")
    for n in different:
        print(f"check page {n} differs")
    return 0 if content_equal else 1


def ratio(expected, got):
    return difflib.SequenceMatcher(None, quotes.normalize(expected), quotes.normalize(got)).ratio()


def tool_path(name):
    found = shutil.which(name)
    if found is None:
        raise SystemExit(f"probe: {name} not found on PATH")
    return found


def probe(extra_args):
    """OCR the committed PDF the way intake does and score every page; exit 1 on any failure."""
    ocrmypdf = tool_path("ocrmypdf")
    tesseract = tool_path("tesseract")
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        src, dst, side = work / "in.pdf", work / "out.pdf", work / "sidecar.txt"
        shutil.copyfile(HERE / PDF_NAME, src)
        (work / "tmp").mkdir()
        env = dict(os.environ, TMPDIR=str(work / "tmp"),
                   PATH=str(Path(tesseract).resolve().parent) + os.pathsep + os.environ.get("PATH", ""))
        # Intake's own command line; extra arguments come last so a probe override wins.
        command = intake.ocr_command(ocrmypdf, src, dst, side, extra_args)
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=900)
        segments = skipped = 0
        if result.returncode != 0 or not dst.exists():
            problems.append(f"ocrmypdf exit={result.returncode}: {result.stderr.strip()[-300:]}")
            texts = []
        else:
            reader = PdfReader(str(dst))
            texts = [(page.extract_text() or "") for page in reader.pages]
            sidecar = side.read_text(encoding="utf-8")
            parts = sidecar.split("\f")
            segments = len(parts)
            skipped = sum(part.strip() == "[skipped page]" for part in parts)
        if len(texts) != len(PAGES):
            problems.append(f"pages={len(texts)} want {len(PAGES)}")
        if segments != len(PAGES):
            problems.append(f"sidecar_segments={segments}")
        if skipped:
            problems.append(f"skipped={skipped}")
        stamps_exact = must_total = must_ok = 0
        ratios = []
        text_layer = []
        for n, (page, got) in enumerate(zip(PAGES, texts), 1):
            found = [s.stamp for s in stamp_finder.find(got, STAMP_PATTERN)]
            want = [stamp_finder.normalize(s) for s in page["stamps"]]
            exact = sorted(found) == sorted(want)
            stamps_exact += exact
            norm = quotes.normalize(got)
            hits = sum(quotes.found_in(span, got) for span in page["must_contain"])
            if page["must_contain"]:
                must_total += 1
                must_ok += hits == len(page["must_contain"])
            r = ratio(expected_text(page), got) if page["kind"] != "blank" else (1.0 if not norm else 0.0)
            ratios.append(r)
            print(f"probe page={n} ratio={r:.3f} must_ok={hits} of {len(page['must_contain'])} "
                  f"stamps={found} want={want}")
            if not exact:
                problems.append(f"page {n} stamps")
            if hits != len(page["must_contain"]):
                problems.append(f"page {n} must_contain")
            if page["kind"] == "blank" and norm:
                problems.append(f"page {n} not empty")
        if texts:
            source_reader = PdfReader(str(HERE / PDF_NAME))
            text_layer = [n for n, page in enumerate(source_reader.pages, 1)
                          if (page.extract_text() or "").strip()]
    min_ratio = min(ratios) if ratios else 0.0
    if min_ratio < RATIO_FLOOR:
        problems.append(f"min_ratio {min_ratio:.3f} under {RATIO_FLOOR}")
    verdict = "FAIL" if problems else "PASS"
    print(f"scanned_probe pages={len(texts)} stamps_exact={stamps_exact} of {len(PAGES)} "
          f"must_ok={must_ok} of {must_total} min_ratio={min_ratio:.3f} text_layer={text_layer} "
          f"sidecar_segments={segments} skipped={skipped} verdict={verdict}")
    for problem in problems:
        print(f"probe problem: {problem}")
    return 1 if problems else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--ocr-arg", action="append", default=[],
                        help="extra ocrmypdf argument for --probe (last one wins)")
    args = parser.parse_args(argv)
    if args.check:
        return check()
    if args.probe:
        return probe(args.ocr_arg)
    print(f"wrote {args.out / PDF_NAME} sha256={build(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
