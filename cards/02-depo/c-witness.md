# CARD 02-C-WITNESS: Witness questions (one topic)
Tier: LOCAL_REVIEW | Output: JSON (schema: questions) | Temperature: 0.1

## Your one job
Write questions for a fact witness on ONE topic, based only on that witness's statements and documents.

## Before you start
The request must say whether the witness is friendly or adverse and which side noticed the deposition. If either is missing, output only:
`NEED: friendly or adverse, and which side noticed the deposition.`

## Steps
1. Section "primary": questions from the side that noticed the deposition.
2. Section "cross": what the other side is likely to ask.
3. Section "redirect": repair questions.
4. If the witness gave more than one version of an event, list each in `note` with cites.

## Example
```json
{"deponent":"Sam Ortiz","section":"primary","topic":"What he saw",
"questions":[{"text":"Mr. Ortiz, in your written statement you said the floor was wet near aisle 7, correct?","cite":"Ortiz statement 3/2/25 p.1","verified":"V","note":"Incident report quotes him as saying 'near aisle 6' (Incident report p.2)."}],
"missing":[],"danger_zone":[],"points_for_our_expert":[],
"coverage":"Topic: what he saw. Questions: 1."}
```

## Final check
- Every question rests on a cited statement or document.
