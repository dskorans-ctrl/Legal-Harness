"""The fixed extraction card and shared prompt encoding for stages 4 and 5."""

import hashlib
import json

from casefile import cards
from casefile.matter import Page

ID_SENTENCE = (
    'The first key is "prompt_id" and the last key is "end_id", both holding the prompt_id '
    'value given in this request.\n')
CARD_NAME = "medical_memo"


def card(book=None):
    return cards.card("01-MEMO", book)


def page_block(page: Page) -> str:
    return f"=== PAGE {page.page_id} BATES {" ".join(page.stamps)} ===\n{page.text}\n"


def prompt_sha256(msgs) -> str:
    return hashlib.sha256(json.dumps(msgs, sort_keys=True).encode()).hexdigest()

