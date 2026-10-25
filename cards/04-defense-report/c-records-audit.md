# CARD 04-C: Records review audit
Tier: LOCAL_REVIEW | Output: JSON (schema: records_audit) | Temperature: 0

## Your one job
Match the report's list of records against our document inventory.

## You receive
- The report's records list (from card 04-A).
- The case file inventory (doc ID, provider, dates), limited to documents dated before the report.

## Steps
1. listed_and_present: report item matches an inventory document. Give the doc ID.
2. listed_not_in_production: report item with no matching inventory document. These go to "records to obtain".
3. in_production_not_listed: inventory document dated before the report that the report does not list.
4. listed_not_discussed: report item that is listed but never summarized or mentioned elsewhere in the report.
5. Match by provider name and dates. If a match is unclear, put it under listed_not_in_production and say why in coverage.

## Example
```json
{"listed_and_present":[{"as_listed":"Harbor Orthopaedics 3/24/25-11/21/25","inventory_doc":"DOC-0004"}],
"listed_not_in_production":[{"as_listed":"Primary care note 12/5/23","report_cite":"Hale report p.2"}],
"in_production_not_listed":[{"inventory_doc":"DOC-0006","date":"02/14/2025","provider":"Coastal Neurology"}],
"listed_not_discussed":[],
"coverage":"Report list: 7 items. Inventory before report date: 9 documents."}
```

## Final check
- Every report item lands in exactly one list.
