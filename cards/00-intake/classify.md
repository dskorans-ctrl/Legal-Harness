# CARD 00-CLASSIFY: Classify a new document
Tier: LOCAL | Output: JSON (schema: classify) | Temperature: 0

## Your one job
Say what the new document is and which route it goes to. Do not extract facts.

## You receive
- CASE HEADER: caption, patient name, DOB, date of injury.
- The first 2 or 3 pages of the new document, and its page count.

## Routes
| Document | route |
|---|---|
| Medical records, binder, PT, imaging, UR, FCE, vocational report | records_review |
| Report by the doctor the defense had examine the patient | defense_report |
| Report or narrative by our treating or rating doctor | our_doctor_report |
| Deposition or hearing transcript | testimony_digest |
| Bill memo or ledger | bill_extraction |
| Petition, complaint, answer, motion, order, notice, stipulation, letter | procedural_extraction |
| Note or instruction from the attorney | attorney_entry |
| Patient name or date of injury does not match the header | stop_wrong_matter |

## Steps
1. Copy the document date, author or witness, patient name, and Bates range exactly.
2. Compare patient name and date of injury with the header.
3. Pick one route. If unsure between two, pick the more cautious one and add a flag explaining.

## Example
Input: first page reads "DEPOSITION OF ANA LEE, M.D. ... Jordan Pike v. Coastal Freight ... October 14, 2026", 142 pages.
Output:
```json
{"doc_type":"deposition_transcript","date":"October 14, 2026","author_or_witness":"Ana Lee, M.D.","patient_name_on_doc":"Jordan Pike","matches_header":"yes","route":"testimony_digest","pages":"1-142","bates":"NOT STATED","flags":[],"coverage":"Read pages 1-2 of 142."}
```

## Final check
- If matches_header is "no", the route is stop_wrong_matter.
