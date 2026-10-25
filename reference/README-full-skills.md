# Local Legal Skills: How They Fit Together

These seven files are instructions for a local model (for example, Qwen running on the Mac). Load the one that matches the task as the system prompt, then give it one pass of material at a time.

## The central case file

Every matter has one case file, kept by **00-case-file-manager**. It is the single source of truth. Every new document (records, reports, transcripts, bill memos, petitions, letters) goes through intake first. The other skills read from the case file instead of from raw documents.

```
New document --> 00 intake --> verified, cited entries in the case file
                                        |
        +-------------+-------------+---+---------+-------------+
        |             |             |             |             |
   01 records    02 depositions  03 hearing   04 / 05 report   06 briefs
   (also the                                   analysis
   extraction
   route for
   records)
```

Key rules of the case file:
- Only cited, verbatim facts go in. Analysis lives separately in `analysis/`.
- Nothing is ever overwritten or deleted. Newer versions supersede, conflicts are kept side by side.
- Record facts, testimony, secondhand summaries, and attorney notes are labeled separately.
- Every update reports what changed and which earlier outputs may now be out of date.
- Every output is stamped with the case file version it was built on.

## The skills

| File | Use it for |
|---|---|
| 00-case-file-manager | Intake of every new document; keeps the case file current |
| 01-medical-records-review | Extracting and verifying medical records (the intake route for records) |
| 02-deposition-prep | Our doctor, defense doctor, our client, or a witness |
| 03-workers-comp-hearing-prep | IAB hearing outline, client prep, doctor prep, closing |
| 04-defense-report-analysis | Auditing the defense doctor's report |
| 05-treating-doctor-report-analysis | What our doctor's reports establish and what is missing |
| 06-brief-motion-drafting | Motions, briefs, memos, letters to the Court |

## Things every skill assumes

- **One pass per request.** The skill text plus one chunk of material should use no more than about 60 percent of the model's context window.
- **A helper script** does the mechanical work: OCR, chunking, checking that quotes really appear in the source, merging update packets, pulling case file entries by tag, totaling bills, sorting dates, flagging out-of-date outputs, and converting Markdown to Word.
- **Attorney-supplied law.** No skill states legal standards or cites authority from memory.

## Firm rules built in

- Never use DME, IME, or "independent" or "defense medical examination." Say "Dr. [Name]'s report."
- Never ask about who hired, paid, or retained a doctor, fees, or volume of examinations.
- Treatment and bills are always two separate questions or items.
- Billing memo is the first item on every hearing checklist.
- Questions to our doctor are leading and use the doctor's own words.
- Cross of the defense doctor stays on documents, never on medicine.
- Bates cites, or binder page plus footer page, with a warning when records are not Bates-stamped.
- No em dashes.
