# Legal Harness (casefile)

A local case system for one attorney: it reads client and medical records on a Mac Studio and builds
the case file, medical memo, deposition and hearing prep, and anonymized brief packages. Built round
by round with the `app-loop` skill (`.claude/skills/app-loop/`).

**New session? Read `docs/loop/HANDOFF.md` first** (one page), then `.workflow/LEDGER.md`
(`## Project` and `## Clarified`), then `Librarian.md`'s builder pre-flight.

- Spec (canon): `docs/spec.md`.
- One round per session. Remote Control on (`/rc` if it is not already).
- **No real client data in this repo or in any session.** Fixtures are invented. Never commit a PDF,
  Word file or image outside `tests/fixtures/`, or anything from `Cases/` or `Bench/`.
- Only `main` is pushed to GitHub, and only on the owner's word.
- Prose has no em or en dashes.

## Mistakes Log

(one line per mistake that cost time, newest last)
- 2026-10-27 R2: chair committed a copied review record without running the gate; it held em dashes and the gate
  printed 1 until the builder fixed it. Run the gate before every chair commit.
- 2026-10-28 R6: chair ruled a fact's date must appear in its quote without measuring it on the key; fix cycle 2 moved
  16 key dates and flawed `dates_wrong` 1 to 7, and fix cycle 3 (the last) went to the revert. Measure a gate rule on the
  answer key before ruling it.
