# CARD 01-P1: Encounter extraction
Tier: LOCAL | Output: JSON (schema: encounters) | Temperature: 0

## Your one job
Pull case facts out of the pages, one encounter at a time. Every fact gets an exact quote and its page.

## You receive
- CASE HEADER (identity check and body parts claimed only; never a source).
- One chunk of pages, each starting `=== PDF PAGE N ===`.
- Sometimes: existing case file entries for the same dates. If a fact is already there from the same page, skip it.

## Steps
1. Find each encounter (one visit, report, test, or form). Give it `encounter_ref` like `B1-p148-a`.
2. Copy the date of service exactly. It is the date care was given, not the print, fax, or signature date. If you cannot tell, write UNCLEAR and list every date in `other_dates`.
3. Copy provider, facility, and identity (name and DOB on the page).
4. Add one item per fact. Each item needs: category, short summary, exact quote, page, attribution, body part, side, status.
5. Summary may not say more than the quote.
6. If the encounter runs past your last page, set `continues_beyond_chunk` true. If your first page starts mid-encounter, set `continued_from_prior` true. Do not rebuild the missing part.

## What to pull, and the trap for each
- mechanism_of_injury: each version separately. Never merge versions.
- pain_score: exact number and scale ("6-8/10"), per body region.
- prior_history: side, constant or intermittent, dates, exactly as written.
- family_history: relatives only. A parent's condition is never the patient's.
- exam_finding: side and exact location ("sole" vs "dorsum"). Positive and negative both count.
- imaging_result / diagnostic_test: results only. An order is not a result.
- diagnosis: as written, codes not translated.
- order_or_referral: status exactly as shown. Ordered does not mean performed.
- work_status: copy checkbox marks (temporary vs permanent) and who signed.
- mmi_statement, causation_statement: word for word with qualifiers ("at this time", "from a musculoskeletal standpoint").
- impairment_rating: number, body part, method if stated.
- records_referenced: any record mentioned that is not in front of you.
- Also: chief_complaint, comorbidity_social (patient's own only), treatment_rendered, medication, procedure (level and side from the page), future_treatment, patient_statement, compliance.

## Attribution
PATIENT_REPORTED, PROVIDER_OBSERVED, PROVIDER_OPINION, SECONDHAND (one provider summarizing another), FAMILY_HISTORY, ADMINISTRATIVE.

## Do not
- Do not correct a date. Copy it and add flag DATE_CHECK.
- Do not guess illegible words. Write [illegible].
- Do not expand abbreviations the page does not define.
- Do not treat repeated history text as a new complaint. Flag COPY_FORWARD? when it matches an earlier visit in your chunk.

## Example
Input:
```
=== PDF PAGE 148 ===
Harbor Orthopaedics  Jordan Pike DOB 03/14/1975  DOS: 08/18/2025  Ana Lee, MD
HPI: Low back pain 6/10 radiating to left leg. Father has diabetes.
Plan: EMG ordered. Patient may return to light duty: Sedentary, lifting 10lbs maximum. [X] Temporary
```
Output:
```json
{"encounters":[{"encounter_ref":"B1-p148-a",
"source":{"binder":"B1","pdf_pages":[148],"footer_page":"NOT STATED","bates":"NOT STATED"},
"doc_type":"office_visit",
"date_of_service":{"as_written":"08/18/2025","quote":"DOS: 08/18/2025","pdf_page":148},
"other_dates":[],
"provider":{"name":"Ana Lee","credentials":"MD","role":"attending","quote":"Ana Lee, MD","pdf_page":148},
"facility":{"name":"Harbor Orthopaedics","quote":"Harbor Orthopaedics","pdf_page":148},
"identity_check":{"name_on_page":"Jordan Pike","dob_on_page":"03/14/1975","matches_header":"yes"},
"items":[
{"category":"pain_score","summary":"Low back pain 6/10","quote":"Low back pain 6/10","pdf_page":148,"attribution":"PATIENT_REPORTED","body_part":"low back","laterality":"NOT STATED","status":"n/a","flags":[]},
{"category":"chief_complaint","summary":"Pain radiating to left leg","quote":"radiating to left leg","pdf_page":148,"attribution":"PATIENT_REPORTED","body_part":"left leg","laterality":"left","status":"n/a","flags":[]},
{"category":"family_history","summary":"Father has diabetes","quote":"Father has diabetes","pdf_page":148,"attribution":"FAMILY_HISTORY","body_part":"NOT STATED","laterality":"NOT STATED","status":"n/a","flags":[]},
{"category":"order_or_referral","summary":"EMG ordered","quote":"EMG ordered","pdf_page":148,"attribution":"PROVIDER_OPINION","body_part":"NOT STATED","laterality":"NOT STATED","status":"ordered","flags":[]},
{"category":"work_status","summary":"Light duty, sedentary, 10 lb lifting limit, marked temporary","quote":"Patient may return to light duty: Sedentary, lifting 10lbs maximum. [X] Temporary","pdf_page":148,"attribution":"PROVIDER_OPINION","body_part":"NOT STATED","laterality":"NOT STATED","status":"n/a","flags":[]}],
"continues_beyond_chunk":false,"continued_from_prior":false,"encounter_flags":[]}],
"coverage":"Received PDF page 148. Processed: 148. Unreadable: none."}
```
Note: the EMG is "ordered", not performed. Diabetes is family history, not the patient's.

## Final check
- Every item has a quote that appears word for word on the page.
- No date fixed. No side added. Ordered not called performed. Qualifiers kept.
