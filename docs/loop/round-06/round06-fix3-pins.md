# Round 6 fix cycle 3: every moved pin

Values below compare the inherited cycle 2 tree with cycle 3. All other cycle 2 pins remain unchanged.

## Fixture dates (cycle 2 -> cycle 3)

| File | Fact | Cite | Old | New |
|---|---|---|---|---|
| key.json | F10 | MED0003 | 04/11/2025 | 03/14/2025 |
| key.json | F13 | MED0005 | 04/10/2025 | 04/14/2025 |
| key.json | F20 | MED0008 | 03/11/2025 | 05/09/2025 |
| key.json | F22 | EMP0001 | (empty) | 03/11/2025 |
| key.json | F23 | EMP0003 | (empty) | 03/15/2025 |
| key.json | F24 | DEF0003 | 03/11/2025 | 06/20/2025 |
| key.json | F27 | MED0008 | 06/20/2025 | 05/09/2025 |
| ideal.json | fact 10 | MED0003 | 04/11/2025 | 03/14/2025 |
| ideal.json | fact 13 | MED0005 | 04/10/2025 | 04/14/2025 |
| ideal.json | fact 20 | MED0008 | 03/11/2025 | 05/09/2025 |
| ideal.json | fact 22 | EMP0001 | (empty) | 03/11/2025 |
| ideal.json | fact 23 | EMP0003 | (empty) | 03/15/2025 |
| ideal.json | fact 24 | DEF0003 | 03/11/2025 | 06/20/2025 |
| ideal.json | fact 27 | MED0008 | 06/20/2025 | 05/09/2025 |
| ideal.json | fact 30 | EMP0001 | 08/02/2021 | 03/11/2025 |
| ideal.json | fact 31 | EMP0002 | (empty) | 03/11/2025 |

## Test and benchmark pins

- `test_bench_cli.FLAWED_LINE`, `test_bench_detail.FLAWED_LINE`, `test_bench_multi.FLAWED_LINE`, `test_benchscore.FLAWED`: `dates_wrong=7` -> `dates_wrong=1`. All other fields unchanged.
- `test_bench_detail.FLAWED_DETAIL`: remove six artificial date mismatches for F10, F13, F20, F22, F23 and F27. Retain the intentional F01 mismatch.
- `test_cards.VERSIONS[01-MEMO]`, `test_extract.test_extract_card`: `2f58978d959b` -> `ed0e58680bc9` (restored committed extraction card).
- `test_stage5_exit.EXPECTED`, memo 1, 2 and 3: `chronology=34 dated=34` -> `chronology=37 dated=37`; `readings=35` -> `readings=38`. Fact totals, cites and casefile line counts unchanged.
- `test_stage6_exit.EXPECTED`, memo: `chronology=34 dated=34 of 37` -> `chronology=37 dated=37 of 37`. Every other stage 6 field unchanged.
- `test_round06_fix2.test_fixture_def0002_and_dates`: hire fact prefix `08/02/2021` -> `03/11/2025` (the incident record date).
- `test_round06_fix2.DATE_MOVES`: all nine independent quote/date expectations restored, listed below in the complete diff. Seven DEF0002 expectations stay 06/20/2025.
- `test_round06_fix2.test_practice_cards[01-MEMO]`: withdrawn quote-only instruction -> restored page wording.
- `test_round06_fix2.test_l7_ambiguous_service_date` -> `test_l7_multiple_page_dates`: multiple dates on the cited page fail -> pass, per D46.
- `test_round06_fix2.test_l7_date_rule`: quote-only expectations -> page date outside quote passes; absent, other-page-only and unparseable dates fail.
- Added `test_chronology_record_date_label`: first paragraph equals `Entries run by the date of the record.` and passes the firm rules.

## Observed benchmark lines

```text
bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14
bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14
```

## Additional pin found by the first full suite

The first full post-edit suite reported `2 failed, 784 passed in 67.55s (0:01:07)`.
Both failures reached `tests/test_memo.py:390`, the shared legacy-upgrade assertion:
`upgrade: undated fact entered chronology`. The actual section held the new introduction instead of `none`.
The renderer now retains `none` beneath the introduction for an empty chronology.
The shared assertion used by `test_memo` and `test_upgraded_fact_is_undated` moves
from `['none']` to `['Entries run by the date of the record.', 'none']`.
This preserves the no-dated-legacy-facts check and the empty-section marker required by D41.
Its independent missing-marker seed went red, was restored with `cmp=0`, then green.

## Complete cycle 3 diff (old -> new)

```diff
--- cycle2/cards/01-records/memo.md
+++ cycle3/cards/01-records/memo.md
@@ -1,6 +1,6 @@
 Read the pages of this matter. Return one JSON object with facts and flags.
 Each fact has cite, quote, text, date, category and provider. Cite the page's Bates stamp, or its page id when unstamped. The quote is an exact span from that page. The text is one sentence saying no more than the quote.
-The date must appear in the fact's quote, copied exactly. A quote without a date may use the page's one explicit date of service. Otherwise leave date empty. Never substitute a report, print, fax, examination or signature date. If several dates in a quote cannot be distinguished, leave date empty. Supported forms: MM/DD/YYYY, M/D/YYYY, YYYY-MM-DD and Month D, YYYY (full month name).
+The date is the date of service of the record the page belongs to, copied exactly as written on the page, never a print, fax or signature date. Leave date empty when the page shows none. Supported forms: MM/DD/YYYY, M/D/YYYY, YYYY-MM-DD and Month D, YYYY (full month name).
 The provider is the provider or facility name as written on the page; leave it empty when none is shown.
 Choose category from: mechanism_of_injury, chief_complaint, pain_score, prior_history, family_history, comorbidity_social, exam_finding, imaging_result, diagnostic_test, diagnosis, treatment_rendered, medication, procedure, order_or_referral, work_status, mmi_statement, causation_statement, impairment_rating, future_treatment, patient_statement, compliance, records_referenced, employment, other.
 Each flag has kind (conflict or gap), cites (the pages involved) and about (one sentence). A conflict is two pages that disagree. A gap is a record a page refers to that is absent from these pages. Preserve disagreements between the report and our records.
--- cycle2/src/casefile/dates.py
+++ cycle3/src/casefile/dates.py
@@ -27,20 +27,3 @@
 def iso(text) -> str:
     value = parse(text)
     return value.isoformat() if value else ''
-
-
-DATE_PATTERN = r'(?<!\w)(?:\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}|[A-Za-z]+ \d{1,2}, \d{4})(?!\w)'
-
-
-def written(text):
-    return tuple(dict.fromkeys(value for value in re.findall(DATE_PATTERN, text) if parse(value)))
-
-
-def fact_dates(quote, page):
-    """A dated quote governs; otherwise only one explicit service date can supply a date."""
-    own = written(quote)
-    if own:
-        return own
-    service = tuple(dict.fromkeys(match[1] for match in re.finditer(
-        r'\bdate of service\s*:\s*(' + DATE_PATTERN + ')', page, re.I) if parse(match[1])))
-    return service if len(service) == 1 else ()
--- cycle2/src/casefile/gates.py
+++ cycle3/src/casefile/gates.py
@@ -137,11 +137,6 @@
                     faults.append(f"{path}.date: {value} is not a date written on {_page_label(page)}")
                 elif parse_date(value) is None:
                     faults.append(f"{path}.date: {value} is not a recognised date form")
-                else:
-                    from casefile.dates import fact_dates
-
-                    if value not in fact_dates(item.get('quote', ''), page.text):
-                        faults.append(f"{path}.date: {value} is neither a date in its quote nor the page's sole date of service")
             if item.get("provider") and quotes.match(item["provider"], page.text) is None:
                 faults.append(f"{path}.provider: not on {_page_label(page)}")
         flag_pages = set()
--- cycle2/src/casefile/memo.py
+++ cycle3/src/casefile/memo.py
@@ -109,9 +109,11 @@
     present = {page.page_id: page for page in pages}
     placement = {fact.id: next((index for index, page_id in enumerate(fact.page_ids)
                                if page_id in present), None) for fact in records}
-    chronology = Section("Treatment chronology")
+    chronology = Section("Treatment chronology", [_paragraph("Entries run by the date of the record.")])
     dated = [(fact, placement[fact.id]) for fact in records
              if placement[fact.id] is not None and fact.dates[placement[fact.id]]]
+    if not dated:
+        chronology.paragraphs.append(_paragraph("none"))
     for fact, primary in sorted(dated, key=lambda pair: dates.parse(pair[0].dates[pair[1]])):
         page = present[fact.page_ids[primary]]
         chronology.paragraphs.extend(_fact_paragraphs(fact, primary, page.page_id,
--- cycle2/tests/fixtures/matters/9001.001/key.json
+++ cycle3/tests/fixtures/matters/9001.001/key.json
@@ -68,7 +68,7 @@
       "cite": "MED0003",
       "quote": "Restrictions: no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
       "text": "Restrictions were no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
-      "date": "04/11/2025"
+      "date": "03/14/2025"
     },
     {
       "id": "F11",
@@ -89,7 +89,7 @@
       "cite": "MED0005",
       "quote": "Patient reports new numbness into the left calf since approximately 04/10/2025.",
       "text": "The patient reported new numbness into the left calf since approximately 04/10/2025.",
-      "date": "04/10/2025"
+      "date": "04/14/2025"
     },
     {
       "id": "F14",
@@ -138,7 +138,7 @@
       "cite": "MED0008",
       "quote": "In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.",
       "text": "Dr. Okonkwo-Lind gave the opinion that the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025.",
-      "date": "03/11/2025"
+      "date": "05/09/2025"
     },
     {
       "id": "F21",
@@ -152,21 +152,21 @@
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
       "text": "The employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "date": ""
+      "date": "03/11/2025"
     },
     {
       "id": "F23",
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
       "text": "The average weekly wage was $912.40.",
-      "date": ""
+      "date": "03/15/2025"
     },
     {
       "id": "F24",
       "cite": "DEF0003",
       "quote": "The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
       "text": "Dr. Marchetti's report states the L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
-      "date": "03/11/2025"
+      "date": "06/20/2025"
     },
     {
       "id": "F25",
@@ -187,7 +187,7 @@
       "cite": "MED0008",
       "quote": "Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on 06/20/2025.",
       "text": "Dr. Okonkwo-Lind restricted the patient to sedentary duty with no lifting over 15 pounds until re-evaluation on 06/20/2025.",
-      "date": "06/20/2025"
+      "date": "05/09/2025"
     },
     {
       "id": "F28",
--- cycle2/tests/fixtures/matters/9001.001/ideal.json
+++ cycle3/tests/fixtures/matters/9001.001/ideal.json
@@ -76,7 +76,7 @@
       "cite": "MED0003",
       "quote": "Restrictions: no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
       "text": "Restrictions were no lifting over 10 pounds and no repetitive bending through 04/11/2025.",
-      "date": "04/11/2025",
+      "date": "03/14/2025",
       "category": "work_status",
       "provider": "Brightwater Family Medicine"
     },
@@ -100,7 +100,7 @@
       "cite": "MED0005",
       "quote": "Patient reports new numbness into the left calf since approximately 04/10/2025.",
       "text": "The patient reported new numbness into the left calf since approximately 04/10/2025.",
-      "date": "04/10/2025",
+      "date": "04/14/2025",
       "category": "patient_statement",
       "provider": "Ridgeline Physical Therapy"
     },
@@ -156,7 +156,7 @@
       "cite": "MED0008",
       "quote": "In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.",
       "text": "Dr. Okonkwo-Lind gave the opinion that the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025.",
-      "date": "03/11/2025",
+      "date": "05/09/2025",
       "category": "causation_statement",
       "provider": "Dr. Priya Okonkwo-Lind"
     },
@@ -172,7 +172,7 @@
       "cite": "EMP0001",
       "quote": "Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
       "text": "The employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.",
-      "date": "",
+      "date": "03/11/2025",
       "category": "mechanism_of_injury",
       "provider": ""
     },
@@ -180,7 +180,7 @@
       "cite": "EMP0003",
       "quote": "Average weekly wage: $912.40",
       "text": "The average weekly wage was $912.40.",
-      "date": "",
+      "date": "03/15/2025",
       "category": "employment",
       "provider": ""
     },
@@ -188,7 +188,7 @@
       "cite": "DEF0003",
       "quote": "The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
       "text": "Dr. Marchetti's report states the L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.",
-      "date": "03/11/2025",
+      "date": "06/20/2025",
       "category": "causation_statement",
       "provider": "Dr. Theodore Marchetti"
     },
@@ -212,7 +212,7 @@
       "cite": "MED0008",
       "quote": "Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on 06/20/2025.",
       "text": "Dr. Okonkwo-Lind restricted the patient to sedentary duty with no lifting over 15 pounds until re-evaluation on 06/20/2025.",
-      "date": "06/20/2025",
+      "date": "05/09/2025",
       "category": "work_status",
       "provider": "Dr. Priya Okonkwo-Lind"
     },
@@ -236,7 +236,7 @@
       "cite": "EMP0001",
       "quote": "Date of hire: 08/02/2021",
       "text": "The incident report gives a hire date of 08/02/2021.",
-      "date": "08/02/2021",
+      "date": "03/11/2025",
       "category": "employment",
       "provider": ""
     },
@@ -244,7 +244,7 @@
       "cite": "EMP0002",
       "quote": "Lift up to 50 pounds repeatedly during the shift.",
       "text": "The job description requires lifting up to 50 pounds repeatedly.",
-      "date": "",
+      "date": "03/11/2025",
       "category": "employment",
       "provider": ""
     },
--- cycle2/tests/test_bench_cli.py
+++ cycle3/tests/test_bench_cli.py
@@ -16,7 +16,7 @@
 FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
 PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
+FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
                "flags_extra=1 rules=1 pages_failed=0 of 14")
 
 def bench(config, *args):
--- cycle2/tests/test_bench_detail.py
+++ cycle3/tests/test_bench_detail.py
@@ -12,19 +12,13 @@
 FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
 PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
+FLAWED_LINE = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
                "flags_extra=1 rules=1 pages_failed=0 of 14")
 FLAWED_DETAIL = [
     "  missed: F04 F15 F24 F30 F31 F32 F33 F34 F35 F36",
     '  invented: MED0003 "Patient was lifting 80 pounds." (quote not on the page)',
     '  invented: MED0099 "Date of service: 03/11/2025" (no such page)',
     "  dates_wrong: F01 (03/12/2025 for 03/11/2025)",
-    '  dates_wrong: F10 (03/14/2025 for 04/11/2025)',
-    '  dates_wrong: F13 (04/14/2025 for 04/10/2025)',
-    '  dates_wrong: F20 (05/09/2025 for 03/11/2025)',
-    '  dates_wrong: F22 (03/11/2025 for )',
-    '  dates_wrong: F23 (03/15/2025 for )',
-    '  dates_wrong: F27 (05/09/2025 for 06/20/2025)',
     "  flags_missed: G3",
     "  flags_extra: conflict MED0001,MED0004",
     '  rules: no-dme-ime DEF0003 "IME"',
--- cycle2/tests/test_bench_multi.py
+++ cycle3/tests/test_bench_multi.py
@@ -13,7 +13,7 @@
 FLAWED = ROOT / "tests" / "fixtures" / "bench" / "flawed.json"
 PERFECT = ("bench 9001.001 model=qwen3.8:27b found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED_LINE = ("bench 9001.001 model=qwen3.8:27b found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
+FLAWED_LINE = ("bench 9001.001 model=qwen3.8:27b found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
                "flags_extra=1 rules=1 pages_failed=0 of 14")
 
 
--- cycle2/tests/test_benchscore.py
+++ cycle3/tests/test_benchscore.py
@@ -13,7 +13,7 @@
 MATTER = ROOT / "tests" / "fixtures" / "matters" / "9001.001"
 PERFECT = ("bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 "
            "flags_extra=0 rules=0 pages_failed=0 of 14")
-FLAWED = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=7 flags=8 of 9 flags_missed=1 "
+FLAWED = ("bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 "
           "flags_extra=1 rules=1 pages_failed=0 of 14")
 
 PAGES = {"medical": [("Pain 7/10 in the low back.\nOther real line.", "MED0001"),
--- cycle2/tests/test_cards.py
+++ cycle3/tests/test_cards.py
@@ -9,7 +9,7 @@
 from casefile import cards, playbook
 from conftest import ROOT
 
-VERSIONS = {'01-MEMO': '2f58978d959b', '00-BILLS': '7805311400a2', '00-CLASSIFY': '0919de24f802', '00-PROCEDURAL': '58ef7e481a89', '00-TESTIMONY': 'acf3b1c3a5ef', '01-P0': 'c87983a810e7', '02-A': '008d522f2b4d', '02-C-CLIENT': 'f243ad762b1f', '02-C-DEFDOC': '77f7427b15f0', '02-C-OURDOC': 'a1d57a9f112b', '02-C-WITNESS': 'ddd72eea4d3e', '03-CLIENT': 'dbead8527c45', '04-G': '3279e19325a0', '05-A': 'cd37084912ca', '07-ANON': 'bd075ed6a208'}
+VERSIONS = {'01-MEMO': 'ed0e58680bc9', '00-BILLS': '7805311400a2', '00-CLASSIFY': '0919de24f802', '00-PROCEDURAL': '58ef7e481a89', '00-TESTIMONY': 'acf3b1c3a5ef', '01-P0': 'c87983a810e7', '02-A': '008d522f2b4d', '02-C-CLIENT': 'f243ad762b1f', '02-C-DEFDOC': '77f7427b15f0', '02-C-OURDOC': 'a1d57a9f112b', '02-C-WITNESS': 'ddd72eea4d3e', '03-CLIENT': 'dbead8527c45', '04-G': '3279e19325a0', '05-A': 'cd37084912ca', '07-ANON': 'bd075ed6a208'}
 
 
 def test_cards():
--- cycle2/tests/test_extract.py
+++ cycle3/tests/test_extract.py
@@ -16,7 +16,7 @@
 def test_extract_card():
     card = extract.card()
     print(f"card_version={card.version} card_name={card.name} docx_import={int(docx.__name__ == 'docx')}")
-    assert card.version == "2f58978d959b", f"card_version={card.version}"
+    assert card.version == "ed0e58680bc9", f"card_version={card.version}"
     assert card.name == extract.CARD_NAME == "medical_memo"
     assert extraction_card().text == card.text
     assert card.text.endswith(extract.ID_SENTENCE)
--- cycle2/tests/test_stage5_exit.py
+++ cycle3/tests/test_stage5_exit.py
@@ -31,9 +31,9 @@
     'stage5 run=2 mode=bad_schema exit=1 chunks=1 runs=+1 read=13 open=1 facts=37 conflicts=5 gaps=4 new_facts=0 new_flags=0',
     'stage5 run=3 mode=replay exit=0 chunks=1 runs=+1 read=14 open=0 facts=38 conflicts=5 gaps=4 new_facts=1 new_flags=0',
     'stage5 run=4 mode=replay exit=0 chunks=0 runs=+0 read=14 open=0 facts=38 conflicts=5 gaps=4 new_facts=0 new_flags=0',
-    'stage5 memo=1 sections=15 chronology=34 dated=34 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=118 readings=35 gaps=4 runs_seen=1 open=1 open_status=uncited rule_hits=0 changed=first',
-    'stage5 memo=2 sections=15 chronology=34 dated=34 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=118 readings=35 gaps=4 runs_seen=1 open=1 open_status=failed rule_hits=0 changed=0',
-    'stage5 memo=3 sections=15 chronology=34 dated=34 of 38 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=120 readings=35 gaps=4 runs_seen=2 open=0 open_status=none rule_hits=0 changed=1',
+    'stage5 memo=1 sections=15 chronology=37 dated=37 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=118 readings=38 gaps=4 runs_seen=1 open=1 open_status=uncited rule_hits=0 changed=first',
+    'stage5 memo=2 sections=15 chronology=37 dated=37 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=118 readings=38 gaps=4 runs_seen=1 open=1 open_status=failed rule_hits=0 changed=0',
+    'stage5 memo=3 sections=15 chronology=37 dated=37 of 38 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 cites=120 readings=38 gaps=4 runs_seen=2 open=0 open_status=none rule_hits=0 changed=1',
     'stage5 status read=13 then 14 open=1 then 0 outputs=memo:current',
     'stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=56 chain_ok=1 server_stopped=1',
 )
--- cycle2/tests/test_stage6_exit.py
+++ cycle3/tests/test_stage6_exit.py
@@ -22,7 +22,7 @@
 MATTER = ROOT / 'tests/fixtures/matters' / NUMBER
 ANSWERS = ROOT / 'tests/fixtures/outputs' / NUMBER
 EXPECTED = (
-    'stage6 memo sections=15 chronology=34 dated=34 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 rule_hits=0 exit=1',
+    'stage6 memo sections=15 chronology=37 dated=37 of 37 providers=6 conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 rule_hits=0 exit=1',
     'stage6 depo=defense-doctor-us outline_our=19 outline_defense=11 questions=8 rests_on_page=8 of 8 danger=6 points=1 forbidden_topics=0 rule_hits=0 header_ok=1 exit=1',
     'stage6 depo=our-doctor-us outline_our=19 outline_defense=11 questions=4 rests_on_page=4 of 4 danger=6 points=0 treatment_q=1 bills_q=1 compound=0 providers_named=5 of 5 rule_hits=0 header_ok=1 exit=1',
     'stage6 hearing checklist_first=1 starred=1 issues=2 standard_needed=2 client_direct=2 client_cross=2 elements=14 not_found=5 closing=2 relief_needed=2 rule_hits=0 header_ok=1 exit=1',
--- cycle2/tests/test_round06_fix2.py
+++ cycle3/tests/test_round06_fix2.py
@@ -177,15 +177,15 @@
     assert any('model returned no item' in x and 'DEF0001' in x and 'DEF0002' in x and 'DEF0003' in x for x in lines), 'H3: empty report section omits model limit and searched pages'
 
 
-def test_l7_ambiguous_service_date(case):
+def test_l7_multiple_page_dates(case):
     from casefile.matter import Page
     page = Page('medical', 1, 'Date of service: 03/11/2025\nDate of service: 03/14/2025\nNormal gait.', ('ABC0001',))
     detail, _ = gates._references({'facts':[dict(cite='ABC0001',quote='Normal gait.',date='03/11/2025')]}, (page,), case[4].rules)
-    assert 'faults=' in detail, 'L7: ambiguous service dates accepted'
+    assert 'faults=' not in detail, 'L7: a parseable date written on the cited page was refused'
 
 
 @pytest.mark.parametrize('card,text', [
-    ('01-MEMO', "date must appear in the fact's quote"),
+    ('01-MEMO', 'copied exactly as written on the page'),
     ('02-A', 'Do not label a harmful fact helpful'),
     ('02-C-DEFDOC', 'Do not turn an adverse conclusion'),
     ('02-C-OURDOC', 'Anchor treatment to a treatment quote'),
@@ -224,19 +224,28 @@
     assert 'Deposition of: NEEDED (doctor\'s name)' in flat(doc) and 'Deposition date and time: NEEDED' in flat(doc), 'L6: deposition placeholder is unlabelled'
 
 
-def test_l7_date_rule(case):
+@pytest.mark.parametrize('date,good,message', [
+    ('03/11/2025', True, 'L7: record date on the cited page but outside the quote was refused'),
+    ('03/12/2025', False, 'L7: date written on no page was accepted'),
+    ('03/14/2025', False, 'L7: date written only on another page was accepted'),
+    ('02/30/2025', False, 'L7: unparseable date written on the cited page was accepted'),
+])
+def test_l7_date_rule(case, date, good, message):
     from casefile.matter import Page
-    base = dict(cite='ABC0001', quote='Date of hire: 08/02/2021', date='03/11/2025')
-    page = Page('medical', 1, 'Date of service: 03/11/2025\nDate of hire: 08/02/2021', ('ABC0001',))
-    detail, _ = gates._references({'facts': [base]}, (page,), case[4].rules)
-    assert 'faults=' in detail and '.date:' in detail, 'L7: unrelated page date accepted for a dated quote'
-    for quote, date in [('Date of hire: 08/02/2021','08/02/2021'), ('No restrictions.', '03/11/2025')]:
-        page = replace(page, text=page.text + '\nNo restrictions.')
-        detail, _ = gates._references({'facts': [{**base, 'quote':quote, 'date':date}]}, (page,), case[4].rules)
-        assert 'faults=' not in detail, 'L7: quote date or unique service date refused'
-    page = replace(page, text='Date of Report: 03/11/2025\nNo restrictions.')
-    detail, _ = gates._references({'facts': [{**base, 'quote':'No restrictions.'}]}, (page,), case[4].rules)
-    assert 'faults=' in detail, 'L7: report date silently used as service date'
+    base = dict(cite='ABC0001', quote='Date of hire: 08/02/2021', date=date)
+    page = Page('medical', 1, 'Date of Report: 03/11/2025\nDate of hire: 08/02/2021\nInvalid date: 02/30/2025', ('ABC0001',))
+    other = Page('medical', 2, 'Date of Report: 03/14/2025', ('ABC0002',))
+    detail, _ = gates._references({'facts': [base]}, (page, other), case[4].rules)
+    assert ('faults=' not in detail) == good, message
+    if not good:
+        assert '.date:' in detail, message
+
+
+def test_chronology_record_date_label(tmp_path, case):
+    doc = built_memo(tmp_path, case)
+    first = section(doc, 'Treatment chronology')[0]
+    assert first == 'Entries run by the date of the record.', 'Chronology: record-date convention missing from first paragraph'
+    assert not case[4].rules.check(first, unit='text', stamped=True), 'Chronology: record-date convention violates firm rules'
 
 
 @pytest.mark.parametrize('kind', ['report','memo'])
@@ -304,13 +313,13 @@
     indexes = [i for i,x in enumerate(lines) if x == 'From [cite DEF0002]:']
     assert len(indexes) == 2 and all(lines[i+1].startswith('"') for i in indexes), 'H4 fixture: DEF0002 has no quote beneath its conflicts'
     chronology = section(doc,'Treatment chronology')
-    assert any(x.startswith('08/02/2021,') and 'Date of hire' in x for x in chronology), 'L7 fixture: hire date appears under report date'
+    assert any(x.startswith('03/11/2025,') and 'Date of hire' in x for x in chronology), 'L7 fixture: hire fact is not under the record date'
     assert any('5/5 bilaterally' in x and x.startswith('06/20/2025,') for x in chronology), 'H3 fixture: examination findings absent from chronology'
 
 
 # These expected values are pinned independently of the runtime fixture loader.
 DEF0002_QUOTES = ['Range of motion (ROM) in the lumbar spine is limited in flexion.', 'Strength testing of lower extremities is 5/5 bilaterally.', 'Reflexes are 2+ and symmetric in all tested segments.', 'Sensation is intact to light touch throughout the dermatomes.', 'Straight leg raise negative bilaterally.', "No objective findings of radiculopathy on today's examination.", 'The L4-L5 disc changes are described as degenerative.']
-DATE_MOVES = [('Restrictions: no lifting over 10 pounds and no repetitive bending through 04/11/2025.', '04/11/2025'), ('Patient reports new numbness into the left calf since approximately 04/10/2025.', '04/10/2025'), ('In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.', '03/11/2025'), ('Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.', ''), ('Average weekly wage: $912.40', ''), ('The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.', '03/11/2025'), ('Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on 06/20/2025.', '06/20/2025'), ('Date of hire: 08/02/2021', '08/02/2021'), ('Lift up to 50 pounds repeatedly during the shift.', '')]
+DATE_MOVES = [('Restrictions: no lifting over 10 pounds and no repetitive bending through 04/11/2025.', '03/14/2025'), ('Patient reports new numbness into the left calf since approximately 04/10/2025.', '04/14/2025'), ('In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.', '05/09/2025'), ('Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.', '03/11/2025'), ('Average weekly wage: $912.40', '03/15/2025'), ('The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.', '06/20/2025'), ('Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on 06/20/2025.', '05/09/2025'), ('Date of hire: 08/02/2021', '03/11/2025'), ('Lift up to 50 pounds repeatedly during the shift.', '03/11/2025')]
 
 def test_fixture_each_new_fact(tmp_path, case):
     doc = built_memo(tmp_path, case)
--- cycle2/tests/test_memo.py
+++ cycle3/tests/test_memo.py
@@ -387,7 +387,7 @@
     memo.render(upgraded_memo, path, rules=firm)
     upgrade_doc = Document(path)
     assert upgraded.upgraded == 1
-    assert [p.text for p in section(upgrade_doc, 'Treatment chronology')] == ['none'], 'upgrade: undated fact entered chronology'
+    assert [p.text for p in section(upgrade_doc, 'Treatment chronology')] == ['Entries run by the date of the record.', 'none'], 'upgrade: undated fact entered chronology'
     assert f'"{pages[0].text}" [cite MED0001]' in [p.text for p in section(upgrade_doc, 'Facts without a date, by page')], 'upgrade: undated fact lost'
 
 
```
