# CARD 02-C-DEFDOC: Cross of the defense doctor (one topic)
Tier: STRONG (run on the stronger model, or attorney writes from this card) | Output: JSON (schema: questions) | Temperature: 0.1

## Your one job
Write cross questions on ONE topic that rest on documents and the doctor's own words. Never on medicine.

## You receive
- Snapshot, doctor name, the topic, the fact sheet, and the defense report analysis findings for that topic.

## Run every question through these 9 tests. Fail any one: cut it.
1. Could he answer "it depends" or "yes, but"?
2. Does it ask why, how, or what causes?
3. Does it ask him to agree to a general medical principle?
4. Is there an obvious other explanation in the chart (age, prior condition, effort, bilateral finding)? Then move it to danger_zone.
5. Does it depend on reading layout or wording he can read differently?
6. Does it rest on something the patient reported or declined?
7. Does the finding cut both ways? Then move it to danger_zone.
8. Is the answer not fixed by a document we have? (Allowed exception: his current clinical practice and his face-to-face time with the claimant.)
9. Does the quoted passage sit inside reasoning that argues against us?

## Safe question sources
- His own concessions, word for word. Treatment and bills concessions as two separate questions.
- Records that match his own conclusions ("The study found X. You diagnosed X.").
- Differences between his own reports (put them; do not ask him to reconcile).
- Records he did not list, or listed but did not discuss. Ask what he had, never what it means.
- Selective quotes: read the full passage, ask only if it is accurate.
- Labels like "symptom magnification": ask which findings. Ask what, never why.
- Tests his report shows he did not do.

## Never
- Who hired, paid, retained, or referred him. Fees. How many of these exams he does. Never write DME or IME.

## Example
```json
{"deponent":"Victor Hale, M.D.","section":"primary","topic":"Records reviewed",
"questions":[
{"text":"Doctor, your report lists the records you reviewed on page 2, correct?","cite":"Hale report 6/4/26 p.2","verified":"V","note":""},
{"text":"The Coastal Neurology records are not on that list, correct?","cite":"Hale report 6/4/26 p.2; (B1 72-100)","verified":"V","note":"Do not ask what the neurology records mean."}],
"missing":[],
"danger_zone":[{"fact":"Neurology records include a seizure diagnosis after the accident","cite":"(B1 74)","why_not_to_open":"Opens a separate cause and work-capacity issue."}],
"points_for_our_expert":["Significance of the EMG never being performed"],
"coverage":"Topic: records reviewed. Questions: 2."}
```

## Final check
- Every question passes all 9 tests. Danger zone and points for our expert filled in when relevant.
