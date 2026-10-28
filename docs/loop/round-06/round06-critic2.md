# Round 6 output critic, second grading (after fix cycles 1 to 3)

OUTPUT CRITIC 7/10 · high 0 · med 6 · low 9

Critic: fresh session, no building context. Branch `loop/round-06`, tip 6fba08f (uncommitted records only). The first
grading (`round06-critic.md`) was read only after the findings below were written.

## How the documents were produced

```
scripts/run.sh pytest -q -s tests/test_stage6_exit.py --basetemp="$(cd $TMPDIR && pwd -P)/critic6b"
```

1 passed in 3.04s; last line `stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1`. The six documents
are under `$TMPDIR/critic6b/test_stage6_exit0/matters/9001.001/outputs/`: `memo.docx`, `depo-defense-doctor-us.docx`,
`depo-our-doctor-us.docx`, `hearing.docx`, `report-defense-report.docx`, `report-okonkwo-lind.docx`. Each was opened
with python-docx (body paragraphs and tables in order, section headers and footers) through `scripts/run.sh python`
and read in full.

Own checks:
- Quotes: every `"..." [cite X]` in all six documents checked as a substring of the cited fixture page (whitespace
  normalised): 490 quotes, 0 off their page. Control (the same check with "60 pounds" altered to "50 pounds" in the
  read text): 7 off. The check can fail.
- Key: all 36 key facts appear in the memo; all 9 key flags (5 conflicts, 4 gaps) appear with the key's wording.
  One key date is not honoured (M1). Two facts beyond the key (hire date [cite EMP0001], the 50 pound job demand
  [cite EMP0002]) are on their pages; nothing invented.
- Rules: no DME, IME or "independent medical" in any document; no hired, retained, fee or paid wording; no em or en
  dash; no build jargon except one line noted under L1 in the earlier-findings table.
- DEF0001: every document ends with `DEF0001 (defense-report/001): uncited: ...` under Open items, as expected.

Reproduce any finding: run the command above, dump the named document with python-docx, find the quoted text.

## Findings, most severe first

**M1 (med) memo, Treatment chronology, entry "03/11/2025, Fennimore County Hospital, Exam finding"; and
report-defense-report, What the report states, first examination finding.** The ER's straight leg raise (key F05,
MED0002, 03/11/2025) and Dr. Marchetti's straight leg raise (key F34, DEF0002, 06/20/2025) are merged into one fact
because the quotes are word for word the same. In the memo the defense finding is filed under the ER visit
("Also cited: [cite DEF0002]" / "Model's reading of [cite DEF0002]: Straight leg raise negative bilaterally."), so the
06/20/2025 Marchetti exam entries list ROM, strength, reflexes, sensation and radiculopathy but no straight leg raise.
In the report analysis the merge runs the other way: under "What the report states" the DEF0002 finding carries "Also
cited: [cite MED0002]" and the ER's reading, which the report does not state. Breaks: key F34 date 06/20/2025 and the
chair's restored rule (a fact's date is the date of its own record); usability (the chronology no longer runs by the
record). Reproduce: grep "Also cited" in memo.docx and report-defense-report.docx.

**M2 (med) depo-defense-doctor-us, Questions: primary (whole section).** No treatment concession and no bills
concession is sought, and the document does not say that the report offers none. The report's only treatment words
are "No further treatment is medically necessary." [cite DEF0003]; it says nothing about past treatment. The firm rule
asks for the two concessions as two separate questions where available; where none is available the attorney needs a
line saying so, so he does not go looking. Breaks: playbook `defense-doctor-two-concessions`; deposition-prep §1 last
paragraph.

**M3 (med) depo-defense-doctor-us, Questions: primary 1 and 6; report-defense-report "Records review audit: not
performed".** The omission points the skill names, all fixed by documents in hand, are missed. DEF0001 lists
"Lakeshore Orthopedic Associates, Dr. Priya Okonkwo-Lind, 05/09/2025" and "Ridgeline Physical Therapy notes", yet his
opinion page [cite DEF0003] never mentions her radiculopathy impression, her positive left straight leg raise or the
new left calf numbness of 04/14/2025 [cite MED0005]; the employer incident report and job description are not in his
list. Question 1 confirms the PT notes are listed and stops before the point. The report analysis says the audit was
not performed although the depo questions quote DEF0001's records list, so the page was read. Breaks: deposition-prep
§2 "Omissions in his review" (records he listed but never summarized); playbook `defense-doctor-use-instead`.

**M4 (med) depo-defense-doctor-us, "Questions: anticipated cross" and "Questions: redirect".** Both sections hold one
filler question each: "Your report identifies the examination date as 06/20/2025, correct?" and "Your report
identifies the MRI reader as Dr. Ansgar Velloso-Krantz, correct?". In the usual case (owner Q59 item 87: the defense
takes its own doctor's deposition and we cross) the attorney needs to know what defense direct will bring out
(degenerative, MMI, no restrictions, 5/5, negative SLR) and what to recross on; neither section gives that. Breaks:
usability (3); the section frame does not match the case Q59 item 87 describes.

**M5 (med) depo-our-doctor-us, "Points for our expert: none"; "Questions: anticipated cross" (one question).** Our
treating doctor's prep gives her nothing to answer the defense report with, although the case file holds three
defense against ours conflicts (G3, G6, G9) and the defense depo document itself puts the straight leg raise dispute
under "Points for our expert". The degenerative and pre-existing opinion, MMI reached, no restrictions, 5/5 strength
and no objective radiculopathy [cite DEF0002], [cite DEF0003] are what defense counsel will cross her on; only the 2019
strain is anticipated. Breaks: playbook `points-for-our-expert` (medical support comes from our treating physician);
usability (3). Partly overlaps owner Q59 item 85 (round 7), but rebuttal of the defense report is not in item 85's list.

**M6 (med) all documents, conflict MED0007 against DEF0002 (key G6); both depo danger zones.** The model's reading
says Dr. Okonkwo-Lind's strength was "graded 4/5", but no quote under `From [cite MED0007]:` shows it; the page has
"Motor strength was graded 4/5 bilaterally in lower extremities." Her same exam also records "Reflexes were intact
throughout the lower extremities." and "Sensation was preserved in all dermatomes tested.", which line up with the
defense exam, and the 4/5 weakness is bilateral, not left sided. Those cut both ways on her radiculopathy impression
and belong in the danger zone of both deposition documents; neither lists them. Breaks: deposition-prep §2 test 7 and
playbook `danger-zone`; Q49 item 54 intent (the quotes show the conflict).

**L1 (low) report-defense-report, What the report states, last line.** "On page DEF0001, the model returned no item;
read the page." is contradicted in the same document by the danger zone quote "He acknowledges a 2019 episode of low
back pain that resolved." [cite DEF0001], and by three depo questions and a hearing question resting on DEF0001.
Breaks: (3), the document says two things about one page.

**L2 (low) hearing, Doctor preparation, "Defense report points to be ready for".** After the MMI, restrictions and
treatment items comes a bare "none" line each (three orphan lines) with no label saying what is none. Breaks: (3).

**L3 (low) hearing, Client preparation, Likely cross 2.** "The history in the report describes a tote of about 60
pounds, correct?" [cite DEF0001] helps the client (it matches the ER's 60 pounds against the employer's 40); defense
counsel will not ask it. It belongs under direct or consistency flags. Breaks: (3).

**L4 (low) hearing, Closing outline, "Our strongest facts" (both issues).** Still lists facts that carry no weight or
cut against us: "Pain 7/10 in the low back, no radiation." [cite MED0001] (no radiation, against a radiculopathy
case), "Lumbar spine x-ray, three views, ordered; report to follow." [cite MED0002], "Discharge summary to follow at
visit 12." [cite MED0005]. Breaks: (3). Overlaps owner Q59 item 86 (round 7).

**L5 (low) hearing, Closing outline, "Our answer".** Restates the three conflicts with their quotes; the G9 answer
rests on the MRI placing degenerative disease at L5-S1, but "Mild degenerative disc disease at L5-S1." [cite MED0006]
is not quoted there (the defense depo question 5 does quote it). Breaks: (3).

**L6 (low) depo-our-doctor-us, Questions: primary 1 and 2.** The treatment question ends "causally related to the work
incident?" without the date the skill's phrasing carries ("the [date] work incident"; here 03/11/2025). The provider
list in the bills question has no "and" before the last name. Breaks: deposition-prep §1 suggested phrasing; (3).

**L7 (low) memo, Treatment chronology, three employer entries; both depo headers.** The source prints as the binder
name "employer" ("03/11/2025, employer, Mechanism of injury") although the page names Quarry Ridge Logistics LLC;
"Deposition of: Dr. Marchetti" drops the first name used everywhere else (Dr. Theodore Marchetti). Breaks: (3).

**L8 (low) report-okonkwo-lind, Elements; hearing, Opinions the case needs.** "Records reviewed: NOT FOUND" although
MED0007 recites the course of care it reviewed (Brightwater 03/14/2025, PT 03/24/2025 and 04/14/2025, "The MRI
findings were reviewed during this consultation."); PARTIAL is the honest label. The Gaps section then repeats the
five NOT FOUND lines word for word. Breaks: (1) label understates support; (3).

**L9 (low) memo, Diagnoses and Our doctors' opinions.** "Diagnoses" lists Dr. Marchetti's "The L4-L5 disc changes are
described as degenerative." [cite DEF0002] among our diagnoses without saying it is the defense report's; "Our
doctors' opinions" lists the ER's off-work note and the family medicine restrictions as opinions. Breaks: (3).

## Round 7 scope (carried by owner Q59 items 82 to 86 and the format specification; not round 6 findings)

- Header and caption (Q59 item 84; format spec §0.1, §0.2): no caption line ("[SURNAME] v. [EMPLOYER]"; the employer
  name Quarry Ridge Logistics LLC is on EMP0001 to EMP0003 but appears in no document), no red privilege line, no
  running header, no "Page X of Y" footer (section headers and footers are empty in all six), `Label: value` lines
  plus "Matter 9001.001" and a build line instead.
- Our doctor's deposition (Q59 items 82, 85): "Purpose: discovery" on both depo documents; Q59 82 says our doctor's
  deposition is testimony preserved for the hearing. The our-doctor primary has two questions only; item 85 asks for
  mechanism, injury, treatment, records reviewed and opinion as well.
- Bills (Q59 item 83): the bills question's providers come from extraction, not from the attorney's bill memo;
  the hearing checklist's totals read "not on file" rather than the itemized bill memo table with blanks.
- Facts per issue (Q59 item 86): permanency and termination sections in the hearing outline and closing are identical;
  the termination point the record supports (job demand "Lift up to 50 pounds repeatedly during the shift."
  [cite EMP0002] against "sedentary duty, no lifting over 15 pounds" [cite MED0008] and "No work restrictions are
  indicated." [cite DEF0003]) is not drawn out.
- Shape and type (format spec B6, C6): hearing organized by issue, not by witness; no tables, callout boxes, checkbox
  bullets or continuous question numbering; cites on separate "Rests on:" lines rather than in parentheses; default
  python-docx margins and styles; client direct has two questions where the client sheet expects topics.

## Earlier findings (first grading, tip 1f987f6) against this tip

| Id | Verdict | Document text now |
|---|---|---|
| H1 | FIXED | Defense depo primary asks no confirmation of his adverse conclusions: "2. What specific findings support the label "No objective findings of radiculopathy" in your report?", "4. The MRI report reads "L4-L5: 4 mm posterior central disc protrusion contacting the thecal sac."; have I quoted that accurately?". The negative SLR is in the danger zone. |
| H2 | FIXED | Bills question: "the charges from Fennimore County Hospital, Brightwater Family Medicine, Ridgeline Physical Therapy, Lakeshore Imaging, Dr. Priya Okonkwo-Lind"; no Marchetti. |
| H3 | FIXED | report-defense-report, Undefined labels: "Findings the report gives:" then the four DEF0002 quotes (5/5, 2+ reflexes, sensation intact, SLR negative). |
| H4 | FIXED | Every `From [cite DEF0002]:` block holds quotes, e.g. G9: "From [cite DEF0002]: "The L4-L5 disc changes are described as degenerative." [cite DEF0002]". |
| M1 | FIXED (harmful facts gone; filler remains, see L4) | "Our strongest facts" no longer lists the ER denial, the 40 pound tote, the ER negative SLR, the date of service or the wage line. Heading not renamed. |
| M2 | FIXED | "Case outline: the defense view" and "Defense position" hold only DEF0002 and DEF0003 items. |
| M3 | FIXED | Hearing: "Issue: permanency" Heading 2, "Our key facts" Heading 3, "Records referenced" Heading 4; Doctor preparation: "What the doctor's records say" Heading 2 with Heading 3 categories beneath. |
| M4 | FIXED | "Defense report points to be ready for" prints the G3 block once (three orphan "none" lines remain, see L2). |
| M5 | FIXED | G1 quotes only the two tote lines; G2 only "Patient denies any prior back injury or back pain." and the 2019 strain line. |
| M6 | FIXED | Treatment question "Rests on: "Plan: left L4-L5 transforaminal epidural steroid injection." [cite MED0008]" with "Model's note: ... it does not establish that all treatment was reasonable, necessary and related." |
| M7 | FIXED | Defense depo danger zone has six items: 60 pound history, ER denial, ER negative SLR, 2019 strain, 40 pound report, "There is mild degenerative change noted at the lower vertebral levels." |
| M8 | FIXED (omissions still thin, see M3) | Undefined label question 2, accurate quotation questions 4 and 5, records question 1. |
| M9 | FIXED | "Records review audit: not performed. No records-referenced item was returned by the model for the report pages; read the records list in the report." |
| L1 | FIXED | No "question 28", "stage", "not built this round". One forward-looking line remains in memo Conflicts: "A cloud task run reads the whole matter." |
| L2 | FIXED | "Mechanism of injury", "Prior history:", "Positive finding:", "Treating relationship:", "Items to raise with the doctor" in plain words. |
| L3 | FIXED | "Facts without a date, by page" holds one heading, "Page DEF0001 (defense-report/001), binder defense-report", with its open item. |
| L4 | FIXED (records reviewed now understated, see L8) | "Permanency rating: NOT FOUND", "Prior conditions and history: NOT FOUND". |
| L5 | FIXED (sections now filler, see M4) | Anticipated cross no longer takes our SLR to him; redirect no longer repeats primary 3 word for word. |
| L6 | FIXED | "Deposition of: Dr. Marchetti" and "Deposition date and time: NEEDED". |
| L7 | NOT FIXED (withdrawn by chair ruling; accepted) | "03/11/2025, employer, Employment: "Date of hire: 08/02/2021"" under the heading "Entries run by the date of the record." |
| L8 | NOT FIXED (rejected by owner Q54 item 68) | "Case outline: our view" still runs every our-side fact with a reading. |

Counts: FIXED 19, NOT FIXED 2 (both by ruling), WORSE 0. New in this grading: the F05/F34 merge (M1), which the
DEF0002 key facts added in fix cycle 2 brought into view.

## Good enough to keep

- Accuracy: 490 quotes on their cited pages (control proves the check bites); all 36 key facts and all 9 key flags
  present with correct providers; nothing invented; every cite a page stamp.
- Memo: spec §2 sections in order, chronology by date of record, defense against ours conflicts first, conflict quotes
  from both pages and now only the conflicting lines, the one-run limit stated.
- Practice: starred billing memo first on the checklist with honest "not on file" totals; treatment and bills two
  separate questions, bills anchored on the bill memo by name and walking providers, no examiner in the list; no fee,
  hiring, volume or DME/IME wording; the defense cross now uses the skill's use-instead tools and a real danger zone.
- Headers from `matter.toml` match on all six; STANDARD NEEDED, RELIEF NEEDED and Deposition date NEEDED fail closed
  and are repeated in Open items; DEF0001 reported in every document.
- Model sentences are labelled "Model's reading" or "Model's note" throughout, so the attorney can tell record words
  from model words.
