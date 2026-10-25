# CARD 00-ATTORNEY: Record an attorney note
Tier: LOCAL | Output: Markdown (one block) | Temperature: 0

## Your one job
Record what the attorney said as an ATTORNEY entry. Never change a record entry because of it.

## Steps
1. Copy the attorney's statement as written.
2. Tag it (issue, body part, provider, witness) from the approved list.
3. If it corrects a record fact, name the record entry ID it conflicts with and add an open item: "Confirm against source."

## Format
```
KIND: ATTORNEY
STATEMENT: "[attorney's words]"
CITE: Attorney, [date]
TAGS: issue=[..]; provider=[..]
CONFLICTS_WITH: [entry ID or none]
OPEN_ITEM: [text or none]
```

## Example
Attorney: "The DOS on the 5/2 Harbor note is wrong, it was 5/12."
```
KIND: ATTORNEY
STATEMENT: "The DOS on the 5/2 Harbor note is wrong, it was 5/12."
CITE: Attorney, 10/23/2026
TAGS: provider=Harbor Orthopaedics
CONFLICTS_WITH: CH-0055
OPEN_ITEM: Confirm date of service of CH-0055 against the source page.
```

## Final check
- The record entry is untouched. The attorney note is never used as a record fact.
