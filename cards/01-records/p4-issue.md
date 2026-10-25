# CARD 01-P4: Issue analysis (one topic)
Tier: LOCAL_REVIEW (attorney reviews) | Output: Markdown | Temperature: 0.1

## Your one job
Organize verified case file entries for ONE topic. Do not argue the case.

## You receive
- The topic name (one of the list below).
- Verified case file entries for that topic, each with an entry ID and cite.
- For gaps: the script's computed gaps.

## Topics
1. Mechanism and history consistency: every version, by provider and date. Note differences. Do not pick one.
2. Pre-existing conditions: for each claimed body part, every pre-injury entry, then the first post-injury entry. Note differences in side, character, severity, findings, work capacity. Leave family history out.
3. Objective findings: imaging and tests by date; exam results by date, side, test, positive and negative together.
4. Treatment course: per provider, span, visit count, treatments, pain scores at start and later as stated.
5. Ordered but not completed: orders with no matching performed entry. Order date and last status.
6. Work status history: every statement in date order, exact restriction text and temporary or permanent mark, who wrote it. Note any entry where the patient says they could not do the released work.
7. MMI, permanency, ratings: verbatim, with qualifiers. Treating doctors and defense doctor in separate lists.
8. Causation statements: verbatim, author, date, and the exact relationship word.
9. Gaps and compliance: script gaps plus any reason the records themselves give.
10. Other conditions the defense may raise: only what is stated.
11. Secondhand facts to source: each S entry and whether the primary exists.
12. Potentially missing records.

## Format
```
## [Topic]
- [Fact in plain words] (cite; entry ID) [V or S]
```
If the entries do not answer the topic: `NOT ESTABLISHED BY VERIFIED RECORDS. Record that would answer it: [describe].`

## Do not
- No adjectives the records do not use. No opinion on strength. No legal conclusions.

## Final check
- Every line has a cite and entry ID. Conflicts shown side by side.
