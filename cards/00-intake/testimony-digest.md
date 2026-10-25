# CARD 00-TESTIMONY: Deposition or hearing testimony digest
Tier: LOCAL | Output: JSON (schema: testimony) | Temperature: 0

## Your one job
Pull the testimony that matters from one chunk of a transcript. Copy questions and answers word for word.

## You receive
- CASE HEADER with the approved tag list (issues, body parts, providers, witnesses).
- 10 to 20 transcript pages, with page and line numbers.

## What to capture
- Opinions and concessions.
- Statements about records the witness reviewed or did not review.
- Anything about treatment, bills, work status, MMI, permanency, causation, prior conditions.
- Admissions and statements that differ from the records.

## Steps
1. One entry per statement. Copy the question and the answer exactly. If the answer is only "Yes" or "Correct", the question carries the meaning, so copy it in full.
2. Include any objection that affects the answer, in the question quote.
3. Cite as `[Witness] Dep. page:line-page:line`.
4. Tag using only the approved tag list.
5. `designate`: verbatim (worth reading to the Board), reference, or none.
6. For our doctor: if treatment and bills were asked in ONE combined question, add flag COMPOUND_TREATMENT_BILLS.

## Do not
- Do not paraphrase inside a quote.
- Do not decide whether testimony is true.

## Example
Input:
```
34  2  Q. Doctor, was the treatment you provided reasonable, necessary
    3     and causally related to the February 5, 2025 accident?
    4  A. Yes.
```
Output:
```json
{"entries":[{"witness":"Ana Lee, M.D.","summary":"Treatment reasonable, necessary, and causally related to 2/5/25 accident","question_quote":"Doctor, was the treatment you provided reasonable, necessary and causally related to the February 5, 2025 accident?","answer_quote":"Yes.","cite":"Lee Dep. 34:2-34:4","tags":{"body_part":[],"issue":["medical treatment"],"provider":["Ana Lee"],"witness":["Ana Lee"]},"designate":"verbatim","flags":[]}],
"coverage":"Read transcript pages 34-35. Entries: 1."}
```
Note: no bills question here. The script checks later chunks before flagging bills as missing.

## Final check
- Every quote word for word. Every cite has page:line.
