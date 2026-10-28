"""The fixed extraction card and shared prompt encoding for stages 4 and 5."""

import hashlib
import json
from pathlib import Path

from casefile import schema
from casefile.matter import Page

CARD_TEXT = (
    "You are reading the pages of one workers' compensation matter. Use only the text in this request.\n"
    "Answer with one JSON object and nothing else: {\"facts\": [...], \"flags\": [...]}.\n"
    "Each fact: {\"cite\": the Bates stamp of the page, \"quote\": an exact span copied from that page, "
    "\"text\": one sentence that says no more than the quote}.\n"
    "Each flag: {\"kind\": \"conflict\" or \"gap\", \"cites\": the Bates stamps involved, \"about\": one sentence}.\n"
    "A conflict is two pages that disagree. A gap is a record a page refers to that is not among these pages.\n"
    "Never name an examination as a DME or an IME in any form; write \"the report\".\n"
    "Never write who hired, paid or retained a doctor, any fee, or how many examinations a doctor does.\n"
    "Never guess, infer or fill in. If a value is not on the page, leave it out.\n")
ID_SENTENCE = (
    'The first key is "prompt_id" and the last key is "end_id", both holding the value '
    'of the prompt_id line at the top of this message.\n')
TEXT = CARD_TEXT + ID_SENTENCE
CARD_NAME = "bench_extract"


def card():
    from casefile.gates import Card

    return Card(CARD_NAME, TEXT, schema.load(
        Path(__file__).resolve().parents[2] / "schemas" / "bench_extract.schema.json"))


def page_block(page: Page) -> str:
    return f"=== PAGE {page.page_id} BATES {" ".join(page.stamps)} ===\n{page.text}\n"


def prompt_sha256(msgs) -> str:
    return hashlib.sha256(json.dumps(msgs, sort_keys=True).encode()).hexdigest()

