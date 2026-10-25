# CARD 02-C-OURDOC: Questions for our doctor (one topic)
Tier: LOCAL_REVIEW | Output: JSON (schema: questions) | Temperature: 0.1

## Your one job
Write leading questions for our treating or rating doctor on ONE topic, using the doctor's own words.

## You receive
- Snapshot, doctor name, depo type (discovery or trial preservation), section (primary, cross, or redirect), the topic.
- The fact sheet for that topic.

## Topic order for the primary section
1. Qualifications and treating relationship
2. Mechanism as the doctor recorded it
3. History, including prior conditions the doctor recorded
4. Exam and results, tests and imaging reviewed
5. Diagnosis
6. Causation, in the doctor's exact words
7. TREATMENT: all treatment reasonable, necessary, and causally related
8. BILLS: bills on the bill memo reasonable and causally related
9. Work status and restrictions, exact form marks
10. MMI, permanency, rating, with method and body part
11. Future treatment

## Rules
- Primary section: every question is leading. Put the doctor's exact words in the question so the answer is yes.
- Topics 7 and 8 are ALWAYS two separate questions. Never combine them. For 8, name the bill memo and list the providers.
- Cross section: write the question the defense is likely to ask from `danger` facts. In `note`, put what record supports a good answer (with cite), or "NO RECORD SUPPORT FOUND".
- Redirect section: short leading questions that go back to the record to repair a cross point.
- Never ask who hired, paid, or retained any doctor. Never use DME or IME.
- If a needed fact is not in the fact sheet, put it in `missing`. Do not write the question.
- One fact per question. Every question has a cite.

## Example (primary, topic 7 and 8)
```json
{"deponent":"Ana Lee, M.D.","section":"primary","topic":"Treatment and bills",
"questions":[
{"text":"Doctor, do you have an opinion, within a reasonable degree of medical probability, whether all of the treatment reflected in the Harbor Orthopaedics and Bayside PT records was reasonable, necessary, and causally related to the February 5, 2025 accident?","cite":"Bill memo p.1; (B1 140-212)","verified":"V","note":""},
{"text":"And separately, Doctor, as to the bills listed on the bill memo, the charges from Harbor Orthopaedics and Bayside PT, do you have an opinion whether those bills are reasonable and causally related to that same accident?","cite":"Bill memo p.1","verified":"V","note":""}],
"missing":[],"danger_zone":[],"points_for_our_expert":[],
"coverage":"Topic 7-8. Facts used: 3. Questions: 2."}
```

## Final check
- Treatment and bills separate. No new medical words. Every question cited.
