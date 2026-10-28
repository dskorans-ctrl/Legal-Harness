# Round 6 output critic

OUTPUT CRITIC 5/10 · high 4 · med 9 · low 8

Critic: fresh session, no building context this round. Branch `loop/round-06`, tip 1f987f6.

## How the documents were produced

```
scripts/run.sh pytest -q -s tests/test_stage6_exit.py --basetemp="$(cd $TMPDIR && pwd -P)/critic6"
```

Passed (1 passed; all eight `stage6` lines match EXPECTED; server_stopped=1). The six documents are under
`$TMPDIR/critic6/test_stage6_exit0/matters/9001.001/outputs/`: `memo.docx`, `depo-defense-doctor-us.docx`,
`depo-our-doctor-us.docx`, `hearing.docx`, `report-defense-report.docx`, `report-okonkwo-lind.docx`.
Each was opened with python-docx through `scripts/run.sh python` and dumped as `NNN [style] text` (NNN is the
paragraph index used below). Every quote followed by `[cite X]`, and every quote line under a `From [cite X]:`
block, was checked as a substring of the cited fixture page: 479 quotes, 0 off their page. No em or en dash, no
DME, IME or "independent medical" in any document. Every document ends in Open items with the known DEF0001 item
and every CLI job exited 1, as expected.

Reproduce any finding: run the command above, then open the named document with python-docx and read the
paragraph index given.

## Findings, most severe first

**H1 (high) depo-defense-doctor-us, Questions: primary, paragraphs 091, 095, 097, 099.** Four of the six primary
questions to the defense examiner have him confirm his own adverse findings and conclusions ("straight leg raise
was negative bilaterally", "degenerative and pre-existing, not causally related", "at maximum medical
improvement", "No further treatment is medically necessary"), which locks in the defense case on our cross.
Breaks: deposition-prep §2 test 9 and playbook `defense-doctor-documents-not-medicine` (do not read defense-friendly
rationale to him), test 7 (the SLR finding cuts both ways: negative at the ER [cite MED0002], positive at
[cite MED0007]; it belongs in the danger zone), and `defense-doctor-use-instead` (lock in his concessions, not his
conclusions).

**H2 (high) depo-our-doctor-us, Questions: primary, paragraph 091.** The bills question asks our treating doctor
whether "the charges from ... Dr. Theodore Marchetti" on the bill memo are reasonable and causally related; that is
the defense examiner, whose exam is not treatment and is not on the claimant's bill memo. Breaks: deposition-prep §1
(the bill memo lists the claimant's treatment charges) and playbook `our-doctor-treatment-and-bills`; it also puts
the examiner's charges into a question, which the owner's "no fee questions to the examiner" ruling is meant to
keep out. The exit test pins this as `providers_named=6 of 6`, so the gate accepts it.

**H3 (high) report-defense-report, Undefined labels, paragraphs 053 to 054.** "Findings the report gives: none
stated on the pages sent: DEF0001, DEF0002, DEF0003" is false: DEF0002 lists "Strength testing of lower extremities
is 5/5 bilaterally.", "Reflexes are 2+ and symmetric in all tested segments.", "Sensation is intact to light touch
throughout the dermatomes." and "Straight leg raise negative bilaterally." under the very label. An attorney who
asks "what specific findings?" expecting none will get five. Breaks: answer key item 1 (an absence the page
contradicts) and deposition-prep §2 "Undefined labels" (know the answer from a document in hand, test 8).

**H4 (high) memo Conflicts 169 and 174; hearing 115, 120, 226, 231, 394, 471, 476, 556, 561; report-defense-report
042, 047, 078, 083; report-okonkwo-lind 047, 088.** In both conflicts with DEF0002 (key G6, G9) the `From [cite
DEF0002]:` block is empty, so only our side is quoted. The defense words are on the page ("No objective findings of
radiculopathy on today's examination.", "The L4-L5 disc changes are described as degenerative.") and the
defense report document itself quotes the first one at 052. Breaks: owner ruling Q49 item 54 (verified quotes from
both pages beneath each conflict). The exit check `conflict_quotes_ok=1` passes because no case-file fact cites
DEF0002, so the expected list is empty.

**M1 (med) hearing, Closing outline, Our strongest facts, 399 to 448 and 484 to 533.** Lists all 25 non-defense
facts as "our strongest", including facts that hurt us: "Patient denies any prior back injury or back pain."
[cite MED0001] (impeached by MED0003, key G2), the 40 pound tote [cite EMP0001] (key G1), "Straight leg raise
negative bilaterally." [cite MED0002], plus filler ("Date of service", the wage line). Breaks: usability (3) and the
danger-zone rule (those are pivot points, not closing points).

**M2 (med) depo-defense-doctor-us 072 to 086, depo-our-doctor-us 072 to 086, hearing 082 to 096 and 193 to 207.**
"Case outline: the defense view" and "Defense position" include our records' restrictions: ER [cite MED0002],
family medicine [cite MED0003] and Dr. Okonkwo-Lind's sedentary restriction [cite MED0008]. Breaks: spec §2 (our
view, then the defense view) and the roles in `matter.toml` (only `defense-report` is defense).

**M3 (med) hearing, Hearing outline, 020 to 080 and 131 to 191; Doctor preparation 280 to 281.** Heading levels are
broken: under "Issue: permanency" (Heading 2) comes "Our key facts" (Heading 3) and then "Records referenced",
"History", "Opinions" at Heading 2, so in Word's navigation pane the categories sit beside the issues, not inside
them; "Defense position" (Heading 3) is followed by "Opinions" (Heading 2); "What the doctor's records say" is an
empty Heading 2 followed by another Heading 2. Breaks: usability (3), structure.

**M4 (med) hearing, Doctor preparation, Defense report points to be ready for, 318 to 374.** The same G3 conflict
block (reading plus eight quotes) is printed four times, once under each DEF0003 opinion, and a fifth time at
377 to 388: about 70 lines of repetition. Breaks: usability (3).

**M5 (med) memo 175 to 196; hearing 256 to 277; all conflict blocks.** The quotes beneath a conflict are every
fact on that page, not the conflicting ones: the tote weight conflict (G1) quotes "Date of service: 03/11/2025",
"Pain 7/10 ..." and "Date of hire: 08/02/2021"; the prior injury conflict (G2) quotes the MED0003 restrictions and
PT referral. Breaks: Q49 item 54 intent (the quotes show the conflict) and usability (3).

**M6 (med) depo-our-doctor-us, Questions: primary, 089 to 090.** The treatment question "Rests on" the causation
quote [cite MED0008], which says nothing about the treatment being reasonable or necessary; the report on the same
doctor (report-okonkwo-lind 057) says `treatment_reasonable_necessary_related: NOT FOUND`. The document presents a
record basis that does not exist. Breaks: (1) cite does not support the line.

**M7 (med) depo-defense-doctor-us, Danger zone, 108 to 110.** One item only (the 2019 strain). The chart holds more
that cuts both ways or is a likely defense explanation: the negative ER straight leg raise [cite MED0002], "There
is mild degenerative change noted at the lower vertebral levels." [cite MED0006], the ER denial of prior injury
[cite MED0001], the 40 versus 60 pound tote (G1). Breaks: playbook `danger-zone`, deposition-prep §2 tests 4 and 7.

**M8 (med) depo-defense-doctor-us, Questions, 088 to 107.** None of the "use instead" tools is used: no "what
specific findings support 'No objective findings of radiculopathy'" question (the defense report document flags this
label at 052), no accurate-quotation question on the MRI (his report calls the L4-L5 changes degenerative; the MRI
puts the protrusion at L4-L5 and the degenerative disease at L5-S1, key G9), no process or omission question beyond
confirming one listed record. Breaks: playbook `defense-doctor-use-instead`, deposition-prep §2.

**M9 (med) report-defense-report, Candidate cross topics 084, What the report states 014 to 023.** The closing line
says "the report's records-referenced statements are listed under What the report states for your own comparison",
but that section holds only the four DEF0003 opinions; the records-reviewed list on DEF0001 and the history and exam
on DEF0001 and DEF0002 appear nowhere in it. Breaks: (3) the document points to content it does not contain.

**L1 (low) build jargon in attorney documents.** hearing 012 "(question 28)", 016 "(transcripts are stage 8)",
375 "not checked this round (no records audit card runs)"; memo 151 "(stage 7b)"; report-defense-report 084 "not
built this round". Breaks: (3).

**L2 (low) raw field ids as labels.** memo chronology 017 to 077 ("other:", "mechanism_of_injury:",
"order_or_referral:"), memo 105 and 108 "prior_history:", report-defense-report 049 and 059 "positive_finding:",
report-okonkwo-lind 049 to 069 and hearing 297 to 317 element ids, report-okonkwo-lind 090 to 093 "Items to raise
with the doctor" is a bare list of ids. Breaks: (3).

**L3 (low) memo, Facts without a date, by page, 197 to 213.** Fourteen Heading 2 page headings, twelve with nothing
beneath them (every fact is dated). Breaks: (3); print "none" once instead.

**L4 (low) report-okonkwo-lind Elements 051, 061, 064 (same in hearing 299, 309, 312).** `permanency_rating:
PARTIAL` rests on the MMI line (there is no rating; NOT FOUND is the honest label); `records_reviewed: STATED`
rests on "The MRI findings were reviewed", the same support as `imaging_reviewed`; `history_prior_conditions:
PARTIAL` rests on a line about where she sought care, not a prior condition. Breaks: (1) label overstates support.

**L5 (low) depo-defense-doctor-us 102 to 107.** The "anticipated cross" question takes our doctor's positive
straight leg raise to the examiner (a finding with a contrary exam in the chart, test 4) and the redirect question
106 repeats primary question 3 word for word. Breaks: deposition-prep §2 tests 4 and 7; (3).

**L6 (low) depo headers 008.** "Deposition of Dr. Marchetti, NEEDED" is an unlabeled placeholder; it should say
what is needed (deposition date and time). Breaks: (3), playbook `header-block`.

**L7 (low) memo chronology 035.** "Date of hire: 08/02/2021" is placed under 03/11/2025 (the report date), which reads
as a hire on the accident date. Breaks: (1) date shown is not the fact's date.

**L8 (low) depo outlines 012 to 069.** "Case outline: our view" runs 25 quote and reading pairs (about three pages)
where spec §2 asks for a two-page outline; many "Model's reading" lines restate the quote word for word, doubling
the length. Breaks: spec §2, (3).

## Owner questions (practice the playbook and skills do not settle)

1. Our-doctor deposition prints "Purpose: discovery". Should a deposition we take of our own treating doctor default
   to trial preservation?
2. Should the bills question name providers from the attorney's bill memo entry (memory: billing memo supplied by
   attorney) rather than every provider string in the case file? Until then, should examiners be excluded (H2)?
3. Header: both skills require the caption; `matter.toml` has none and the documents print none. Add a caption field
   (with NEEDED when blank)?
4. Our-doctor primary questions: only the two firm questions are produced. Should primary also walk causation,
   diagnosis, MMI and restrictions, or is the attorney expected to add them?
5. Hearing outline and closing print identical content under "permanency" and "termination". Should facts be
   filtered per issue, and by what rule?
6. When we take the defense examiner, are "anticipated cross" and "redirect" the right section names (defense
   counsel's questions and our recross)?

## Good enough to keep

- Every quote (479) is on its cited page; every cite is a Bates stamp; no invented facts (the two facts beyond the
  key, hire date [cite EMP0001] and the 50 pound job demand [cite EMP0002], are on their pages).
- Memo: all 29 key facts present with correct dates and providers; all five key conflicts and four gaps present;
  defense-against-ours conflicts first; spec §2 sections in order; the cross-run limit stated.
- Header from `matter.toml` on all six documents, matching exactly; build line with case file entry, playbook and model.
- Hearing: the starred billing memo item is first on the checklist, totals honestly "not on file"; STANDARD NEEDED
  and RELIEF NEEDED where the matter leaves them blank and listed again in Open items; issues from the matter's list.
- Our-doctor treatment and bills are two separate questions in the skill's phrasing; no compound question; no fee,
  hiring or volume question to the examiner; no DME or IME in our words; no em or en dashes.
- "Model's reading" and "Model's note" labels are applied to every model sentence; DEF0001 is reported as an open
  item in every document and every job exits 1, as expected.
- Report on Dr. Okonkwo-Lind: fourteen elements in order with treatment and bills NOT FOUND kept separate in Gaps.

## Chair reproduction and rulings (2026-10-28)

Reproduced in the critic's documents (`$TMPDIR/critic6/.../outputs/`, python-docx): H2 (our-doctor bills question ends
"... Dr. Priya Okonkwo-Lind, Dr. Theodore Marchetti, do you have an opinion whether those bills are reasonable ..."),
H1 (defense depo Q2 "Your report says straight leg raise was negative bilaterally, correct?" and Q4 his causation
sentence "..., correct?"), H3 ("none stated on the pages sent: DEF0001, DEF0002, DEF0003" while DEF0002 lists 5/5
strength, 2+ reflexes, intact sensation, negative SLR), H4 (`From [cite DEF0002]:` followed directly by the next
conflict). Root cause of H3 and H4: the answer key and ideal answer hold no fact on DEF0002 (an answer key gap since
round 2), so nothing verified exists to quote. Others taken as described; each fix proves its finding red first.

Rulings (fix cycle 2, Codex):
- Fixture (deliberate baseline move, recorded at close): add DEF0002's examination findings to `key.json` and
  `ideal.json` (each a quote on the page, with date 06/20/2025, category and provider Dr. Theodore Marchetti); leave
  `flawed.json` missing them so its line still shows misses; re-derive and name every moved pin (bench, stages 2, 4, 5,
  6). DEF0001 stays the fixture's known open item.
- H4 and M5 (code): a conflict quote block never prints empty: with no verified fact on a cited page it prints "No
  verified fact quoted from <cite>; read the page."; with facts, it prints only facts sharing a category with a fact
  on the other cited page, else all of the page's facts under "(all facts on this page)". M4: one block per conflict per
  document section.
- H3, M9: a report section that finds nothing says which pages were sent and that the model returned no item; section
  cross-references name the section that holds the items.
- H2: bills-question providers exclude every provider whose facts all lie in a `defense` role binder.
- H1, M6, M7, M8, L4, L5 (practice in the recorded answers and card text): rewrite the defense-doctor primary, cross and
  redirect recorded answers and the our-doctor and report recordings to follow the deposition-prep skill's tests for
  the defense examiner (no question asks him to confirm his own adverse conclusion; use the skill's use-instead tools:
  which findings support a conclusion, accurate quotation of the MRI and records, history taken), the danger zone to
  name the harmful items the critic lists (each with its verified quote), the treatment question to rest on a
  treatment quote, element labels to rest on the right quote, redirect not to repeat primary; and tighten the card
  bodies with the skill's rules in words. Recorded limit: question quality is graded by the critic and the benchmark;
  no code gate can judge it.
- M1: "Our strongest facts" holds only facts the factsheet step labelled helpful to us; with no labels the heading reads
  "Facts (not ranked)". M2: the defense view and Defense position draw only on `defense` role binders.
- M3: heading levels nest (an issue's subsections sit under it); a heading with nothing under it is not printed (also L3).
- L1: no build jargon (question numbers, stage names, "not built this round") in any document; L2: human labels for
  category and element ids; L6: the deponent placeholder reads "Deposition of: NEEDED (doctor's name)".
- L7: a fact's date must appear in its quote; a quote without a date may take the page's one date of service; else the
  fact is undated. Re-derive the key's dates under this rule and name every change.
- L8: rejected (owner Q54 item 68 confirmed "no page cap on the two-page outline").
- Adjacent A1 from fix cycle 1 (an append failure after the Word file is replaced leaves status `current`): fix and prove.
- The critic's six owner questions are filed as 82 to 87 with fail-closed interims.
