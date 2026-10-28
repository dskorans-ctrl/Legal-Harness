# CARD 02-C-WITNESS: Witness questions

Write the requested section's questions from the witness's statements and the cited documents.
If the witness gave different accounts, keep each version with its cite in the note.
Use the section meaning below; do not invent the witness's attitude or an answer.

## Input and answer
Read the fact packet, its cited pages and labels. Return only the questions schema: section, questions
({text, cite, quote, note}), points_for_our_expert ({text, quote, cite}). Copy section from the request.
Every question and expert point rests on a quote on its cited page. Notes may be empty. No missing list.
When taken_by=us, primary is ours, cross the other side's likely questions, redirect ours after cross.
When taken_by=defense, primary is theirs, cross ours, redirect theirs. Purpose is discovery or trial.
Never script a client's answer. Never supply an unsupported assertion.
