"""Compare a quoted span with page text: exact after normalisation (stage 2); the stage 4 ladder
replaces found_in."""

CURLY = {"‘": "'", "’": "'", "“": '"', "”": '"'}


def normalize(text: str) -> str:
    for curly, straight in CURLY.items():
        text = text.replace(curly, straight)
    return " ".join(text.split()).casefold()


def found_in(quote: str, page_text: str) -> bool:
    quote = normalize(quote)
    return bool(quote) and quote in normalize(page_text)
