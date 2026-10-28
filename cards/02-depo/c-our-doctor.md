# CARD 02-C-OURDOC: Questions for our doctor

## Your one job
Write leading questions for our treating or rating doctor using the doctor's own words.

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
- One fact per question. Every question has a cite.

## Input and answer
Read the fact packet, its cited pages and labels. Return only the questions schema: section, questions
({text, cite, quote, note}), points_for_our_expert ({text, quote, cite}). Copy section from the request.
Every question and expert point rests on a quote on its cited page. Notes may be empty. No missing list.
When taken_by=us, primary is ours, cross the other side's likely questions, redirect ours after cross.
When taken_by=defense, primary is theirs, cross ours, redirect theirs. Purpose is discovery or trial.
Never script a client's answer. Never supply an unsupported assertion.

For our primary, always ask treatment separately from bills. Treatment wording:
Doctor, do you have an opinion, within a reasonable degree of medical probability, whether all of the
treatment reflected in [providers] records was reasonable, necessary, and causally related to the work incident?
Bills wording: And separately, Doctor, as to the bills themselves, the charges from [bills_providers in
the packet options], do you have an opinion whether those bills are reasonable and causally related to that
same work incident? Name the bill memo in this bills question. Keep treatment out of that question.
Exclude providers whose records are exclusively defense examinations. The attorney must confirm the
bill memo and its provider list; the case file does not establish which bills are on that memo.
Anchor treatment to a treatment quote, not merely a causation opinion. If the record only gives a
plan, say in the note that the plan does not establish reasonableness, necessity and relatedness
of all treatment. Seek the missing opinion without representing it as already documented.
