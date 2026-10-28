# Format specification for casefile's Word outputs, distilled from five example documents

Status: design input for the round 7 brief (ledger Q59 item 84), 2026-10-28. Nothing here is canon until the owner
rules and the chair moves the rulings into spec §9.

Source: five final documents the owner uploaded on 2026-10-28 (real work product; the owner waived the no-client-data
rule for reading those five files in that session only). This file records layout and form only. Every name, date,
number, place, party, provider, diagnosis, quote and fact is replaced by a bracketed placeholder. Placeholders:
`[CLAIMANT]` or `[PLAINTIFF]` (the client; `[SURNAME]` where only the surname is used), `[EMPLOYER]`, `[DEFENDANT]`,
`[CARRIER]`, `[OUR DOCTOR]`, `[OUR RATER]`, `[DEFENSE DOCTOR]`, `[OUR EXPERT]`, `[DEFENSE COUNSEL]`, `[ATTORNEY]`,
`[FIRM]`, `[COURT]`, `[CASE NO.]`, `[IAB NO.]`, `[DATE]`, `[DOA]`, `[HEARING DATE]`, `[TIME]`, `[PLACE]`, `[N]`, `[PROVIDER]`,
`[BODY PART]`, `[ISSUE]`, `[QUOTE]`, `[W]` (a witness's short cite form, an initial or a short surname), `p:l` (page:line).

The five kinds, in the order specified below:

| Kind | Audience | casefile output today |
|---|---|---|
| A. Deposition read-in script | attorney at the hearing, reading aloud | none (new output) |
| B. Hearing outline, witness by witness | attorney at the hearing | `casefile hearing` (all parts) |
| C. Client hearing prep sheet | the client, the night before | none (new; `hearing --client` is attorney-facing) |
| D. Deposition day-of prep sheet | attorney, morning of the client's deposition | none (new output) |
| E. Deposition prep outline (client deposed by the defense) | attorney, prep session with the client | `casefile depo --deponent client --taken-by defense` |

`casefile report` and `casefile memo` have no example among the five. The common conventions in section 0 should
still apply to them (privilege line, caption line, running header, page footer, fonts, tables).

---

## 0. Conventions common to the examples

### 0.1 Top of the first page (all five)

Three or four centered lines, in this order, before any heading:

1. Privilege line: bold, centered. In the workers' compensation documents it is dark red (hex B00020), all caps, body
   size (10 pt on the client sheet). In the civil documents it is black, all caps, bold (8 pt on the day-of sheet,
   11 pt on the outline).
   Wording seen: `ATTORNEY WORK PRODUCT | PRIVILEGED & CONFIDENTIAL` (civil; pipe separator);
   `ATTORNEY WORK PRODUCT [dash] PRIVILEGED & CONFIDENTIAL` (workers' compensation; the source uses an en dash, which
   casefile's no-dash rule forbids, so casefile should keep the pipe); client sheet:
   `PRIVILEGED & CONFIDENTIAL | ATTORNEY-CLIENT COMMUNICATION`.
2. Title line: bold, centered, 15 to 18 pt. All caps in two of the hearing documents, title case in the others.
3. Caption line or subtitle line: centered, not bold, 9 to 12 pt (gray 595959 on the client sheet). Parts are joined by
   two spaces, a pipe and two spaces. See each kind for its exact parts.
4. (Some kinds) a caption table or a sources line follows; see each kind.

### 0.2 Running header and footer

| Kind | Header (every page, one line) | Footer |
|---|---|---|
| A, B | `Attorney Work Product [sep] Privileged & Confidential  \|  [SURNAME] v. [EMPLOYER], IAB No. [IAB NO.]  \|  DOA [MM/DD/YYYY]  \|  Hearing [MM/DD/YYYY], [TIME]` | `Page [PAGE] of [NUMPAGES]` (Word fields) |
| C | `Attorney Work Product / Attorney-Client Privileged  \|  [SURNAME] v. [EMPLOYER], IAB No. [IAB NO.]  \|  DOA [MM/DD/YYYY]  \|  Hearing [MM/DD/YYYY], [TIME]` | `Page [PAGE] of [NUMPAGES]` |
| D | none (one dense sheet) | none |
| E | `Attorney Work Product \| Privileged & Confidential \| [PLAINTIFF SURNAME] v. [DEFENDANT], et al.` | `Page [PAGE]` (no total) |

The header uses the short caption (surname v. first-named party), not the full caption.

### 0.3 Page setup and type

| Kind | Paper | Margins (top/bottom, left/right) | Body font | Heading 1 | Heading 2 |
|---|---|---|---|---|---|
| A | Letter, portrait | 0.83 in, 0.9 in | Calibri 11 | Calibri 14 bold, navy 1F3864, rule below | (none used) |
| B | Letter, portrait | 0.9 in, 1.0 in | Calibri 11 | Calibri 13.5 bold, navy 1F3864, rule below | Calibri 11.5 bold, blue 2E5597 |
| C | Letter, portrait | 0.9 in, 1.0 in | Calibri 11 | Calibri 14 bold, navy 1F3864, rule below | Calibri 12 bold, blue 2E5597 |
| D | Letter, portrait | 0.42 in, 0.5 in | Calibri 11 (lists), 8 pt tables and sources line | section heads are bold 11 pt navy 1F3A5F paragraphs with a rule, not Word heading styles | none |
| E | Letter, portrait | 1.0 in all sides | Times New Roman 11 | TNR 14 bold, dark blue 1F3A5F, 14 pt before, 7 pt after | TNR 12 bold, black |

Tables: single-line borders, header row bold and shaded, body text 10 pt (9 pt in the read-in schedules, 8 pt on the
day-of sheet). Header shades seen: light blue D9E2F3 (schedules, order of presentation, ratings), light pink F4CCCC
(bill memo), light yellow FFF2CC (defense cross tables), light gray E7E6E6 or EDEDED (label columns of caption and
"Basics" tables), gray-blue D9E2EC (all civil tables).

Callout boxes (single-cell look made with paragraph shading and a border, indented 0.1 in):
- Star banner: white bold text on dark red B00020, the star at 14 pt. Wording:
  `★ GIVE THE BILLING MEMO TO THE HEARING OFFICER.  Hand it up at the outset with the exhibits.` (kind A ends after
  "at the outset with the exhibits.").
- Witness purpose box (kind B): bold lead "Purpose:" on light blue E8F0FA with a border.
- Caution box (kinds B and C): bold text on light peach FCEBD9 with a border.

Lists: bullets "•" for argument, themes and instructions; checkbox bullets "☐" or "□" for things to do (pre-hearing
checklist, open items, the client's topics to think about); the glyph "Q." as the bullet for anticipated questions in
kind E; decimal numbering only where order matters (corrections on the day-of sheet, witness questions in kind B).

Page breaks: kind B starts each witness section, and the closing, on a new page; kind A starts each witness after the
first on a new page. Kinds C, D, E run on without forced breaks.

### 0.4 How the documents refer to people

- The client: "Ms. [SURNAME]" or "Mr. [SURNAME]" in attorney documents; "she" or "he" inside a topic; "you" in the
  client sheet (opening salutation "Ms. [SURNAME], thank you for coming in tomorrow.").
- Doctors: "Dr. [SURNAME]" in headings and first mention; bare surname in tables, closing argument and comparisons
  ("[OUR RATER] chose ...", "[DEFENSE DOCTOR] agrees ..."); "his" or "her" for the defense doctor after the heading.
- The defense side: the employer or defendant by short name ("[EMPLOYER]'s doctor", "[EMPLOYER]'s lawyer"), "defense",
  "defense counsel", "counsel". The tribunal: "the Board", "the Hearing Officer".
- Transcript speakers keep the reporter's form: `Q.`, `A.`, `MR. [ATTORNEY SURNAME]:`, `MS. [DEFENSE COUNSEL SURNAME]:`.
- Per firm practice (kind B, defense witness box): nothing about who retained the defense doctor, defense work or fees.

### 0.5 Citations

- Transcript: page:line ranges, no "p." prefix, hyphen between ends, semicolon between ranges:
  `[W] 12:3-14:20; [W] 41:2-18`. Within a witness's own section the witness prefix is dropped (`(22:5-15)`). When a
  range stays on one page the second page may be dropped (`41:2-18`) or kept (`8:4-8:19`); both forms appear.
- Medical records (civil): `(Med. Rec. [N])`, `(Med. Rec. [N]-[N])`, `(Med. Rec. [N], [N], [N])`, from a compiled
  records index; other sources by short form defined in a citation key or sources line: `Pl. Rog [N]` (interrogatory
  answer number), `[OUR EXPERT] Rpt. [page]`, `Synopsis` (intake synopsis), `IR` (incident report), `Log`, `Prep`
  (prep session summary), `Timeline`.
- Bates numbers appear only when a transcript passage names one ("Bates [N]").
- Documents and exhibits are referred to by kind, date and author ("[OUR RATER]'s [DATE] rating report", "the bill
  memo", "the medical binder", "binder tab [N]"), and the bill memo by item ("Item [N]").
- Cites sit in parentheses at the end of the sentence or clause they support, never on a separate line.

### 0.6 Dates

Caption lines: long form (`Month D, YYYY`) on the client sheet and the caption tables; `MM/DD/YYYY` in running
headers; short `M/D/YY` in body text and tables. Unknown values print as `[TO BE CONFIRMED]`, `[time]`, `[per TSO]`,
or a blank of underscores (`$__________`, `________ to ________`) where the attorney will write by hand.

---

## A. Deposition read-in script

### A1. Purpose and audience

The verbatim passages the attorney reads aloud at the hearing from each doctor's deposition transcript, in reading
order, witness by witness. Audience: the attorney at the hearing table.

### A2. Caption block

```
            ATTORNEY WORK PRODUCT | PRIVILEGED & CONFIDENTIAL        (centered, bold, dark red)
                     DEPOSITION READ-IN SCRIPT                        (centered, bold, 17 pt, caps)
[CLAIMANT FULL NAME] v. [EMPLOYER FULL NAME]  |  IAB No. [IAB NO.]  |  DOA [MM/DD/YYYY]  |  Hearing [MM/DD/YYYY], [TIME]
                                                                      (centered, 10 pt)
★ GIVE THE BILLING MEMO TO THE HEARING OFFICER at the outset with the exhibits.   (star banner)
[One 10 pt paragraph: every passage is verbatim from the certified transcript and is read aloud; excerpts only; the
cite in each bar is the portion to read; "[ . . . ]" marks a skip; the gray cite marks where each paragraph begins.]
```

### A3. Sections

No numbered sections. One Heading 1 per witness, in hearing order:

1. `Witness [N]: Dr. [OUR DOCTOR] (Deposition [Month D, YYYY])` (numbering continues from the hearing outline, so the
   first doctor is Witness 2 when the client testifies live as Witness 1).
2. Further treating or rating doctors, same form.
3. `Defense Witness: Dr. [DEFENSE DOCTOR] (Deposition [Month D, YYYY])`, followed by a 10 pt note: read after the
   defense reads its portions; skip any portion the defense already read; key `D = his direct, X = our cross,
   R = his redirect`.

Under each witness, a run of portions. Each portion is:

- A portion bar (navy 1F3864 fill, white bold label):
  `Portion [N]   [p:l]-[p:l][; p:l-p:l]   [short summary of what the passage proves]`
  (three spaces between the three parts). For the defense witness the label is `D[N]`, `X[N]` or `R[N]` instead of
  `Portion [N]`. Summaries for passages taken from the other side's examination begin `From defense cross:`; redirect
  passages begin `Redirect:`.
- The transcript lines, one paragraph per speaker turn, indented 0.25 in: a gray (8C8C8C) 8 pt cite `[p:l]`, two
  spaces, then 11 pt text beginning `Q.`, `A.` or `MR./MS. [SURNAME]:`. A passage that begins mid-answer has no
  speaker prefix.
- A skip within a portion is its own gray paragraph `[ . . . ]`.

Order of portions within our doctor (observed form, not content): qualifications and the stipulation to them; history
at first visit; denial of prior similar injury; testing and results; diagnosis; causation to a reasonable degree of
medical probability; treatment prescribed; work status and progress; treatment reasonable and necessary; restrictions
and why; disagreement with the defense doctor's conclusions; agreement that a defense exam finding fits our diagnosis;
bills by bill memo item and total, then treatment reasonable, necessary and causally related, then bills reasonable
and causally related (separate questions); then helpful passages from the defense cross, then redirect. This matches
the owner's list in ledger Q59 item 85.

### A4. Tables

None.

### A5. Conventions

- Verbatim only; the bar cite is the exact span to read; every paragraph inside carries its starting page:line.
- Portions restart at 1 for each witness; defense witness portions are numbered separately within D, X and R.
- No exhibit cites outside the transcript text.
- Fonts and page setup: section 0.3. Each later witness starts on a new page.

### A6. casefile today and gaps

No casefile output corresponds. Gaps:
- casefile has no transcript input: no transcript intake, no page:line model, no speaker turns. The whole kind needs a
  transcript binder type with page and line numbers kept from the certified transcript.
- No designation step (choosing portions, skips, D/X/R labels) and no card for it.
- The renderer has no shaded bars, no gray small cite runs and no indented paragraphs (`outputs.render` writes plain
  paragraphs and Word headings only).
- Quotes would be checked against transcript lines, not record pages; the quote gate needs a page:line address form.

---

## B. Hearing outline, witness by witness

### B1. Purpose and audience

The attorney's script for the whole hearing in presentation order: checklist, order and ratings at a glance, opening,
each witness (live questions or read-in schedule), closing and open items. Audience: the attorney at the hearing.

### B2. Caption block

```
            ATTORNEY WORK PRODUCT | PRIVILEGED & CONFIDENTIAL        (centered, bold, dark red)
                 HEARING OUTLINE: WITNESS BY WITNESS                  (centered, bold, 17 pt, caps)
                    [ISSUE 1] and [ISSUE 2]                           (centered, 12 pt: the live issues)
```

Then a two-column caption table (label column bold, shaded light gray):

| Label | Value |
|---|---|
| Caption | [CLAIMANT FULL NAME] v. [EMPLOYER FULL NAME] |
| IAB Hearing No. | [IAB NO.] |
| Date of Accident | [Month D, YYYY] |
| Hearing | [Weekday], [Month D, YYYY], [TIME], [PLACE] |
| Live Issues | [ISSUE 1] ([statute section]) and [ISSUE 2] ([PROVIDER], [DATE] and ongoing). [Resolved petition] resolved by stipulation. |
| Defense Counsel | [DEFENSE COUNSEL], Esq. ([which depositions taken]); [other counsel on the notice] |

### B3. Sections (Heading 1 with Roman numerals; Heading 2 inside)

- `I. Pre-Hearing Checklist`: star banner; bill memo table (B4); a one-line note that the Board cannot rule on
  reasonable, necessary and related without the numbers, so do not rely on the binder; then a "☐" checklist:
  stipulations to put on the record, transcripts and exhibits to hand up (each transcript by witness and date,
  medical binder, the decision under appeal, any report tabbed because a figure appears only there), records still to
  obtain, figures to reconcile, any motion to make (for example leave to lead), each pointing to its section.
- `II. Order of Presentation and Ratings at a Glance`: order table, ratings table (B4), then a bold key line:
  `Key: READ = read verbatim to the Board.  COUNTER = our counter-designation to read after defense reads its portion.
  SKIP / LEAVE = do not read; noted so you know what is there.`
- `III. Opening ([N] to [N] minutes)`: five or so bullets: what is resolved and what remains; the undisputed core and
  any defense concession; who the Board will hear from and what each establishes; the answer to the defense theory on
  each issue; "Our ask:" with the relief.
- `IV. Witness 1: [CLAIMANT] (Live, Our Only Live Witness)`: caution box (how the questions track the client sheet
  topics, what "(L)" means, when to ask leave to lead, what not to raise); Heading 2 topics numbered to match the
  client sheet (`1. About You and Your Job`, `2. The Accident on [DATE]`, `3. Your Symptoms and Treatment`,
  `4. Getting Back to Work`, `5. How You Are Doing Now`); numbered questions (B5); bold dark-gray subtopic labels
  inside a long topic; a final Heading 2 `Cross Risks (prepped)` with bullets: likely cross point (cite), how she
  answers.
- `V. Witness 2: Dr. [OUR DOCTOR] (Deposition [M/D/YY])` and `VI. Witness 3: Dr. [OUR RATER] (Deposition [M/D/YY])`:
  purpose box ("Purpose: [role]. Establishes [elements]. Client point: ... Watch: ..."); Heading 2
  `Our Read-In Schedule` (table); Heading 2 `Defense Cross: What to Expect`, a one-line note that our helpful answers
  from the defense cross are already in the schedule, then the defense cross table.
- `VII. Defense Witness: Dr. [DEFENSE DOCTOR] (Deposition [M/D/YY])`: box (our read-in uses the whole transcript; read
  after defense, in transcript order, D, X, R; skip what defense read; nothing about retention, defense work or fees);
  Heading 2 `A. Our Read-In` (table); `B. Defense Redirect and Response` (bullets, each led by a bold page:line range,
  then what it shows and "Response:"); `C. Points to Argue From the [DEFENSE DOCTOR] Read-In` (bullets with cites).
- `VIII. Closing`: bullets, each led by a bold label (the undisputed core, then one per issue or rated body part with
  the figure, then the appeal issue), each a short argument with transcript cites; the last bullet `Ask:` with the
  relief.
- `IX. Open Items`: "☐" list of things to fill in, obtain, confirm or research.

### B4. Tables

| Table | Columns | What each holds |
|---|---|---|
| Caption (B2) | label, value | as listed above |
| Bill memo | `Provider (Bill Memo Item)`, `Date Range`, `Balance` | one row per memo item `Item [N]: [PROVIDER] ([W] p:l-l)`, range `MM/DD/YYYY to MM/DD/YYYY`, amount `$[N]`; an indented `incl. [disputed period]` subrow; last row `GRAND TOTAL`; unknown items printed as underscores |
| Order of presentation | `#` (no header text), `Witness`, `Method` | 1 Opening, 2 live client, 3 and 4 our doctors, `D` defense doctor, 5 Closing; method text such as "Live", "Read deposition in portions", "Defense reads its direct; we read our cross and counter-designations", each with "(Section [ROMAN])" |
| Ratings at a glance | `Body Part`, `[OUR RATER]`, `[DEFENSE DOCTOR]`, `Cites` | one row per rated body part; each doctor's figure with its basis in parentheses; cites as `[W] p:l-p:l; [W] p:l-p:l` |
| Our read-in schedule | `#`, `Page:Line`, `Type`, `Content / key lines` | running number (blank for SKIP or LEAVE rows; `D[N]`, `X[N]`, `R[N]` for the defense witness); the range; `READ`, `SKIP` or `LEAVE`; a summary with short quoted phrases, inner cites in parentheses, and bold-caps flags `KEY`, `KEY ADMISSIONS`, `CLIENT POINT`, `STOP at p:l`, `Caution:`, `Optional`, `Pair with [W] p:l-p:l` |
| Defense cross: what to expect | `Defense will likely read`, `Damage`, `Our response` | the range and what it says; the inference defense wants; `COUNTER p:l-p:l:` with what we read back, or a short argument |

Widths seen in the schedule: 0.42 in, 0.94 in, 0.66 in, 4.49 in.

### B5. Conventions

- Live questions are numbered continuously through the witness (1 to [N]), not restarted by topic, typed as
  `[N].  [question]` with a 0.375 in indent; `(L)` before a leading question; an expected answer and its source in
  parentheses at the end (`(… ; [W] p:l-l)`); "If needed (L): ..." for fallback leading forms. Open questions
  ("Tell the Board ...") first in each topic; leading questions fill gaps.
- Read-in summaries refer to the doctor by pronoun; KEY flags mark the passages that carry an element.
- Cites: transcript only, section 0.5; record cites appear only as quoted in testimony.
- Each witness section and the closing start on a new page.

### B6. casefile today and gaps

Corresponds to `casefile hearing` with all four parts (outline, client, doctor, closing). Current sections:
`Pre-hearing checklist`, `Hearing outline` (by issue), `Client preparation`, `Doctor preparation`, `Closing outline`,
`Open items`, under a level 0 title `Hearing preparation` and a labelled header list. Gaps:
- Shape: casefile is organized by issue then by part; the example is organized by witness in presentation order, with
  issues only in the subtitle, caption table, opening and closing. Q59 item 86 (facts per issue) needs a home in this
  shape (see the questions at the end).
- Caption: no privilege line in red, no title line, no caption line or caption table; header is `Label: value` lines
  plus `Matter [number]` and a build line (Q59 item 84).
- No running header, no `Page X of Y` footer, default python-docx margins and heading styles.
- No tables at all. The bill memo is one sentence ("Totals: not on file; the billing memo is supplied by the
  attorney."); it should be the itemized table from the attorney's bill memo (Q59 item 83), blanks as underscores.
- No order of presentation, no ratings at a glance (the `impairment_rating` facts exist but are not compared by doctor).
- No opening section.
- Star banner and boxes are plain paragraphs; checklist items are not checkboxes.
- Client questions: casefile prints `1. [question]` restarting per section, each followed by a `Rests on:` evidence line
  and `Model's note:` lines; the example numbers continuously, marks `(L)`, and puts the expected answer and cite in a
  trailing parenthesis. Topics should match the client sheet (kind C).
- Doctor part: casefile lists what the records say and an elements checklist (`STATED`, `PARTIAL`, `NOT FOUND`); the
  example presents each doctor as a read-in schedule from the transcript plus a defense cross table. Needs transcripts
  (gap A6) and our doctor's deposition (Q59 item 82).
- Cites: casefile `[page X]` or `[cite X]`; the example uses transcript page:line almost everywhere.
- Closing: casefile lists facts chronologically and "Relief requested: ..." with a note that no law is cited; the
  example is one bold-led argument bullet per issue or body part, then `Ask:`.

---

## C. Client hearing prep sheet

### C1. Purpose and audience

A plain-language sheet for the client to read the night before: logistics, what the Board decides, how to testify,
the topics of direct, likely cross questions, and what to do tonight and tomorrow. Audience: the client.

### C2. Caption block

```
          PRIVILEGED & CONFIDENTIAL | ATTORNEY-CLIENT COMMUNICATION   (centered, bold, dark red, 10 pt)
                     Preparing for Your Hearing                       (centered, bold, 18 pt, title case)
[CLAIMANT NAME] v. [EMPLOYER FULL NAME]  |  IAB No. [IAB NO.]  |  Date of Accident: [Month D, YYYY]
                                                                      (centered, 10 pt, gray)
[Unheaded opening paragraph addressed to "Ms. [SURNAME]": what the sheet is, read it tonight, no need to memorize,
tell the truth in your own words.]
```

### C3. Sections (Heading 1 unnumbered; Heading 2 numbered topics)

1. `The Basics`: logistics table (C4).
2. `What the Hearing Is About`: a sentence on what is already resolved; bullets, one per issue, each with a bold lead
   phrase in plain words and one or two sentences naming which doctor says what; a paragraph on the client's role
   (the doctors' opinions are already recorded; only the client can describe daily life).
3. `How to Testify`: about nine bullets, each a bold imperative lead sentence then one or two plain sentences (tell the
   truth; listen and pause; ask for a repeat; do not guess; give real examples; do not exaggerate or minimize; answer
   only the question on cross; stay calm; take your time). Then a caution box: no notes at the witness chair; leave
   this sheet with the attorney.
4. `What I Will Ask You`: a line saying these are topics, not a script; Heading 2 topics numbered and in sentence case
   (`1. About you and your job`, `2. The accident on [Month D, YYYY]`, `3. Your symptoms and treatment`,
   `4. Getting back to work`, `5. How you are doing now`), each a "□" list of topic phrases, not questions, some with
   "(for example ...)" prompts and "Think of ..." invitations.
5. `What [EMPLOYER]'s Lawyer May Ask`: a reassuring line; then the cross table (C4).
6. `Tonight and Tomorrow`: bullets (read once then put away, sleep and eat, what to wear and bring, arrival time, do
   not discuss the case at the hearing).
7. Closing line ("If you have any questions tonight, please call me."), then a signature block: `[ATTORNEY]` on one line,
   `[FIRM]  |  Phone: ____________________` on the next.

### C4. Tables

| Table | Columns | What each holds |
|---|---|---|
| The Basics | label (bold, shaded), detail | rows `When`, `Where`, `Who will be there`, `How long`, `What to wear`, `What to bring`; detail may hold two lines (for example the time, then the arrival time) |
| Likely cross | `Possible question`, `What to keep in mind` | the question as defense would phrase it, in second person; one or two sentences of guidance, never an answer to adopt ("If that is what you said, agree." "Answer honestly.") |

### C5. Conventions

- Second person, short sentences, no legal terms (issues named in plain words), no cites, no page numbers in the text,
  no model labels.
- Doctors by "Dr. [SURNAME]"; the defense doctor as "[EMPLOYER]'s doctor, Dr. [SURNAME]"; the opposing lawyer as
  "[EMPLOYER]'s lawyer" (with "her" or "his").
- The five topic headings are the same topics, in the same order, as Witness 1 in kind B.
- Fonts and setup: section 0.3; no forced page breaks.

### C6. casefile today and gaps

No corresponding output. `hearing --client` produces attorney-facing `Direct examination` and `Likely cross` question
lists with evidence lines, `Consistency flags` and a one-paragraph instruction string (`hearing.INSTRUCTIONS`). Gaps:
- A client-facing document is a new kind: plain language, no cites, no model labels, no open items, a signature block.
  The quote and cite gates and the "Model's reading" labelling rule would need a defined exemption or a separate
  check for this audience.
- Logistics (place, time, arrival, what to bring, who attends) are not in `matter.toml`; they would be typed by the
  attorney at the run.
- The topic list should be generated once and shared with kind B so the numbering matches.
- No tables, no caution box, no checkbox bullets (renderer gaps as in B6).

---

## D. Deposition day-of prep sheet

### D1. Purpose and audience

A one- or two-page sheet for the morning of the client's deposition: what the records say on the body parts in
dispute, corrections to what the client said in yesterday's prep, items to reconcile, and three reminders. Audience:
the attorney (shown to or walked through with the client).

### D2. Caption block

```
            ATTORNEY WORK PRODUCT | PRIVILEGED & CONFIDENTIAL       (centered, bold, 8 pt)
              [PLAINTIFF SURNAME] Deposition: Day-of Prep Sheet      (centered, bold, 15 pt)
[PLAINTIFF SURNAME] v. [DEFENDANT], et al., C.A. No. [CASE NO.] ([COURT ABBREV.]) | DOA [M/D/YYYY] |
Deposition [MM/DD/YYYY], [time] | Trial [per TSO] | Prepared [MM/DD/YYYY]   (centered, 9 pt)
Sources: Med. Rec. = [compiled records index]; [OUR EXPERT] Rpt. = [DATE] report; Pl. Rog = Plaintiff's answers to
[DEFENDANT] interrogatories ([DATE]); Prep = [DATE] prep recording (summary).            (left, 8 pt)
```

### D3. Sections (bold numbered paragraph heads, navy, with a rule)

1. `1. The [BODY PART GROUP]: What the Records Say`: a bold-led paragraph "The short version to confirm with her (in
   her own words, only if true to her memory): ..."; the chronology grid (D4); a bold label
   `Corrections from yesterday's prep (Prep, [DATE])`; a numbered list, each item led by a bold phrase (the client's
   words in quotation marks, or the topic), then what the records show with cites, then what to do with her.
2. `2. Other Items to Reconcile Before She Testifies`: the reconcile table (D4).
3. `3. Reminders for Her`: three bullets (listen, pause, answer only the question; defer to the records for dates,
   diagnoses and which doctor did what; do not adopt counsel's words, with examples of the words to avoid).

### D4. Tables

| Table | Columns | What each holds |
|---|---|---|
| Chronology grid | `Date`, `[BODY PART 1]` (side in caps), `[BODY PART 2]`, `[BODY PART 3]`, `Cite` | one row per record date or date span (`M/D/YY`, or `M/YY to M/YY` for a gap); per body part a few words of finding or event, `Not mentioned`, `(none)`, `No treatment (gap)`, or blank; caps for the side and for the decisive event (`[SIDE]`, `[EVENT]`); cite as `Med. Rec. [N]-[N]` or `[OUR EXPERT] Rpt. [N]` |
| Reconcile | `Issue`, `What she said in prep`, `What the record shows`, `Action` | a short topic; her prep account; the record with cites (`Pl. Rog [N]`, `Med. Rec. [N]`, `IR`); one imperative sentence |

Widths seen: grid 0.69, 2.05, 2.05, 1.46, 1.25 in; reconcile 1.04, 2.01, 2.57, 1.88 in. 8 pt text.

### D5. Conventions

- Dense: 0.42 in and 0.5 in margins, 8 pt tables, no header or footer.
- The client is "her" or "she"; the expert by surname with "Dr." on first mention; defense counsel as "counsel".
- Cites per section 0.5 (civil forms); the sources line defines every abbreviation used.
- Corrections never tell her what to say; they say what the record shows and to confirm what she remembers.

### D6. casefile today and gaps

No corresponding output. Gaps:
- Needs the prep session as an input (a recording summary or the attorney's notes); casefile has no such source.
- Needs discovery responses (interrogatory answers) as a source with answer numbers; casefile has no such binder kind.
- A body-part by date grid needs facts tagged by body part and side; casefile facts carry category, date and provider,
  not body part.
- Narrow margins, small type and the no-header layout are not available in the renderer.

---

## E. Deposition prep outline (client deposed by the defense)

### E1. Purpose and audience

The full outline for preparing the client before the defense takes her deposition: how the defense will run it,
ground rules, the anticipated questions topic by topic with what the file shows and the prep note for each, the
discovery answers to fix, danger zones, documents to review and open items. Audience: the attorney, in the prep
session.

### E2. Caption block

```
            ATTORNEY WORK PRODUCT | PRIVILEGED & CONFIDENTIAL        (centered, bold, 11 pt)
        Plaintiff Deposition Preparation Outline: [PLAINTIFF FULL NAME]   (centered, bold, 15 pt)
          Anticipated Defense Examination on [TOPIC 1] and [TOPIC 2]  (centered, 12 pt)
```

Then a two-column caption table (`Item`, `Detail`, header shaded):

| Item | Detail |
|---|---|
| Caption | [PLAINTIFF FULL NAME] v. [every defendant, full names] |
| Court / Case No. | [COURT], C.A. No. [CASE NO.] |
| Medical expert | [OUR EXPERT], M.D., [PRACTICE] (report [M/D/YY]) |
| Date of accident | [Month D, YYYY] ([PLACE], [incident report time]) |
| Deponent | [PLAINTIFF FULL NAME] (DOB [MM/DD/YYYY]), Plaintiff |
| Deposition date and time | [TO BE CONFIRMED] |
| Trial date | [TO BE CONFIRMED per Trial Scheduling Order] |
| Defense counsel | [DEFENSE COUNSEL], [FIRM] (for [DEFENDANT]); [other counsel] [confirm] |
| Prepared | [Month D, YYYY] |

Then a bold-led paragraph `Citation key.` defining each cite form (Med. Rec. page numbers and binder tab, Pl. Rog with
the date of the answers, the expert report, the synopsis, the incident report, any log) and stating that no transcript
exists yet, so there are no page:line cites.

### E3. Sections (Heading 1 Roman numerals; Heading 2 lettered)

- `I. How the Defense Will Run This Deposition`: a paragraph on the expected order of examination and where the
  damaging documents will be used; Heading 2 `Defense liability themes` and `Defense treatment and damages themes`,
  each a bullet list led by a bold theme name, then the evidence with cites.
- `II. Ground Rules to Review With Ms. [SURNAME]`: about seven bullets (truth, do not guess; listen, pause, answer,
  stop; read any document before answering; do not adopt counsel's words; avoid absolutes; prep is privileged;
  prepare for embarrassing details).
- `III. [TOPIC 1]: Anticipated Questions`: a line "For each topic: the questions defense counsel is likely to ask,
  what our file shows, and the points to cover with her in prep."; Heading 2 lettered topics (`A.` to `H.`) in the
  order the defense will ask (background and employment, the day and route, the condition, warnings, how it happened,
  immediately after, statements and social media, related claims); under each, a "Q." list of anticipated questions,
  then a two-column table (E4).
- `IV. [TOPIC 2]: Anticipated Questions`: a line on how the defense will go provider by provider; Heading 2 lettered
  topics (`A.` prior history, then each provider or period in time order, the treatment gap, the principal treatment,
  alternative explanations, current condition and future treatment), same "Q." list and table; a final lettered
  topic `[OUR EXPERT]'s Report: What Defense Will Test Through Her` with a paragraph summarizing the report's
  opinions and the history table (E4).
- `V. Interrogatory Answers to Review and Supplement Before the Deposition`: a line, then the interrogatory table.
- `VI. Danger Zones Summary`: one bullet per danger, a noun phrase each.
- `VII. Documents to Review With Her Before the Deposition`: bullets.
- `VIII. Open Items for Counsel`: bullets, each an imperative (confirm, obtain, locate, serve, address, decide,
  reconcile).

### E4. Tables

| Table | Columns | What each holds |
|---|---|---|
| Caption (E2) | `Item`, `Detail` | as listed above |
| Per topic (one after each lettered topic) | `What the file shows`, `Prep note` | one row: the record facts with cites in parentheses; the attorney's guidance for the prep (what to pin down, what she should and should not do, what to obtain); equal widths 3.25 in |
| Expert report history | `History in the report`, `Why it matters for her testimony` | a short quote or paraphrase with `(Rpt. [N])`; whether it is a witness issue or a counsel issue and what to do |
| Interrogatories | `Rog`, `Issue`, `Action` | answer numbers (`[N], [N]`); what is missing or inconsistent; `Supplement.`, `Confirm ...`, `Clarify ...` |

### E5. Conventions

- Anticipated questions are phrased as defense counsel will ask them, in second person, short, several per bullet
  ("Where were you ...? Job title? How long ...?"), bulleted with the glyph `Q.`, not numbered.
- Theme bullets and danger bullets cite the record; ground rules and documents do not.
- The client is "Ms. [SURNAME]" in headings and "she" in text; defendants by short name; the expert by surname.
- Fonts: Times New Roman (section 0.3); header short caption; footer page number only.

### E6. casefile today and gaps

Corresponds to `casefile depo --deponent client --taken-by defense`. Current sections: `Case outline: our view`,
`Case outline: the defense view`, `Questions: primary`, `Questions: anticipated cross`, `Questions: redirect`,
`Danger zone`, `Points for our expert`, `Open items`, under the title `Deposition preparation`. Gaps:
- Caption: labelled header lines instead of the three centered lines and the caption table; no citation key.
- Section shape: when the defense takes the client's deposition, the example has no primary, cross and redirect
  split; it is "how the defense will run it", ground rules, then anticipated defense questions by topic with a
  file-versus-prep table per topic. casefile's three question sections fit a deposition we take, not this one.
- No defense themes section (liability and damages), no ground rules, no documents-to-review list.
- No interrogatory table: discovery responses are not an input (same as D6).
- `Points for our expert` belongs to doctor depositions; the client outline instead has the expert report history
  table (what in the expert's history the client's testimony must match).
- Cites: casefile `[page X]`; the example uses `Med. Rec. [N]` keyed to a compiled index, plus other source forms.
- Questions: casefile numbers them `1.` and follows each with `Rests on:` and model notes; the example lists them under
  `Q.` bullets and puts the evidence in the topic table.
- Renderer gaps as in B6 (tables, header, footer, fonts, margins).

---

## F. Gaps common to every casefile output

1. Renderer: `outputs.render` and `memo.render` write a level 0 title, Word headings and plain paragraphs on the
   default template. Needed: page setup (margins), base font per kind, heading styles as in 0.3, a running header and
   a page footer with PAGE and NUMPAGES fields, tables with shaded header rows and set widths, shaded callout
   paragraphs, checkbox and `Q.` bullets, indented and gray small-run paragraphs, page breaks before witness sections.
   `Paragraph` and `Section` have no table or style fields today.
2. Caption: add the privilege line, title line and caption line (Q59 item 84) from `matter.toml` (client name,
   opposing party, hearing or case number, date of accident, hearing or deposition date and time). The opposing
   party's name and the court and case number are not stored yet; `matterinfo.HEADER` would need them.
3. Header block: the `Label: value` lines, `Matter [number]` and the build line are casefile's own; the examples carry
   none of them. They could move to the end (for example under Open items) or into document properties.
4. Model labels: `Model's reading`, `Model's note`, `Rests on:` and `NOT FOUND` lines do not appear in the examples.
5. Cite forms: casefile prints `[page X]` or `[cite X]`; the examples print transcript page:line and source-key forms
   in parentheses.
6. The bill memo is a typed source (Q59 item 83): its items, ranges, balances and total should come from the
   attorney's memo, with blanks printed as underscores.

## G. Practice questions the examples do not settle

1. Hearing shape: should `casefile hearing` follow the witness-by-witness order (kind B), and if so where do the
   per-issue fact sections of Q59 item 86 go: inside the closing, as an appendix, or as a separate document?
2. Transcripts: will certified deposition transcripts be an input (file type, page and line numbering, which binder
   role), so casefile can build read-in scripts and schedules? Who chooses the portions: the model, or the attorney
   with the model proposing?
3. Our doctor's deposition prep (Q59 items 82 and 85) has no example among the five. Is there a sample of that
   document, or should it take kind E's shape (topics, questions, a file table per topic)?
4. Cite form in hearing documents: page:line for transcripts is clear; for records, Bates (standing memory: hearing prep
   asks which stamp), compiled index page (`Med. Rec. [N]`), or both?
5. Model labels: may attorney documents drop `Model's reading` and `Rests on:` lines in favor of the examples' trailing
   parentheticals, as long as every quote and cite is still gated? Must the client sheet carry no label at all?
6. Should casefile produce a client-facing document (kind C) at all, and if so is the attorney's name, firm and phone
   line typed once into the config?
7. Privilege wording and separator: the examples use an en dash in the workers' compensation privilege line; confirm the
   pipe form (`|`) everywhere, and the client sheet's `ATTORNEY-CLIENT COMMUNICATION` wording.
8. Fonts: Calibri for workers' compensation documents and Times New Roman for civil ones, by matter type, or one font?
9. Day-of sheet (kind D) and interrogatory table (kind E): what is the source for the prep session summary and for
   discovery responses, and where are they filed in the matter?
10. Leading questions on direct: is "(L)" marking and the leave-to-lead plan standard practice for every live client,
    or matter specific?
11. Defense cross tables (`Defense will likely read`) predict the other side's designations: should casefile draft
    them, and should it propose counter-designations?
12. Ratings at a glance: when two of our doctors testify, which one is the rater column, or one column per doctor?
13. Unknown values: `NEEDED` (casefile today), `[TO BE CONFIRMED]` or underscores; one rule for all kinds?
14. Live client as Witness 1: always first, or does the order of presentation vary and need a prompt?
15. Body-part tagging for the day-of grid: should facts gain a body part and side field, or should the grid be drawn
    from the attorney's own list of disputed body parts?
