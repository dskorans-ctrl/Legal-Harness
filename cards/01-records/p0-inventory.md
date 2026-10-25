# CARD 01-P0: Page inventory
Tier: LOCAL | Output: JSON (schema: inventory) | Temperature: 0

## Your one job
Describe each page you are given. One entry per page. Do not summarize medical content.

## You receive
- CASE HEADER: patient name, DOB, date of injury. Use it only to check identity.
- 5 to 15 pages of text, each starting with a line like `=== PDF PAGE 41 ===`.

## Steps
1. For each page, copy: document type, provider or facility, the date shown, footer page number, Bates number, patient name on the page.
2. Copy each value exactly as printed. If it is not on the page, write NOT STATED.
3. Set `readable`: yes, partial, or no.
4. Add flags:
   - WRONG_PATIENT? if the name or DOB differs from the header
   - DUPLICATE? if the page repeats another page you were given
   - BLANK_OR_ILLEGIBLE, NO_DATE_VISIBLE, OCR_SUSPECT (garbled text like "1O/12/25")
   - INDEX_PAGE if the page lists documents. A listed document is not proof the document exists.

## Do not
- Do not guess a date from nearby pages.
- Do not use the file name or folder name.

## Example
Input:
```
CASE HEADER: Patient: Jordan Pike  DOB: 03/14/1975  DOI: 02/05/2025
=== PDF PAGE 41 ===
Harbor Orthopaedics  Patient: Jordan Pike  DOB 03/14/1975
Office Visit  DOS: 08/18/2025 ... Page 2 of 4
=== PDF PAGE 42 ===
MEDICAL RECORDS INDEX  Tab 1 ER  Tab 2 Harbor Ortho  Tab 3 PT
```
Output:
```json
{"pages":[
{"pdf_page":41,"doc_type":"office_visit","provider_or_facility":"Harbor Orthopaedics","date_on_page":"08/18/2025","footer_page":"Page 2 of 4","bates":"NOT STATED","patient_name_on_page":"Jordan Pike","readable":"yes","flags":[]},
{"pdf_page":42,"doc_type":"index_or_tab","provider_or_facility":"NOT STATED","date_on_page":"NOT STATED","footer_page":"NOT STATED","bates":"NOT STATED","patient_name_on_page":"NOT STATED","readable":"yes","flags":["INDEX_PAGE","NO_DATE_VISIBLE"]}],
"coverage":"Received PDF pages 41-42. Processed: 41, 42. Unreadable: none."}
```

## Final check
- One entry per page received. Every value copied or NOT STATED. Coverage lists every page.
