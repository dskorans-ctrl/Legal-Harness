# The Librarian

> **Scope rule (owner, 2026-09-10).** One Librarian per project. On a new project create it blank —
> the header and the section headings only, no entries and no pre-flight bullets carried over from
> another project. Within a project it persists across sessions: every session reads it before building
> and the chair extends it at every round close. The failure-class catalog at the end of this file is
> the skill's cross-project knowledge; consult it, do not paste it into a project's Librarian.


`Librarian.md` lives at the repo root, not under `docs/loop/`, because every round's builders must
read it before the round even has a number — it outlives any one round's paper trail. It is the
project's running record of bugs, code issues and failures found in any pass, so the next pass
does not repeat them; it indexes mistakes across the project's other logs (a defect ledger, a
mistakes log, prior round work) without being the design or status log itself. Updated by: the
chair (or a delegated sonnet worker) at every round close — new entries for that round, survivors
folded into "Open items" — plus any builder who finds a new one mid-round, appended under the
current round heading on the spot rather than held for close. Every builder brief must cite it;
every builder report must state which entries it checked its work against — a brief that cites it
zero times is a brief the next round's builders will (correctly) treat as optional.

## Skeleton

```markdown
# Librarian

This file is the project's running record of bugs, code issues and failures found in any pass, so
the next pass does not repeat them. <one sentence naming the other logs it indexes but does not
replace>. Updated by: the chair at every round close (new entries for that round, survivors moved
to "Open items"); any builder who finds a new one mid-round appends it under the current round
heading. Every builder brief must cite this file; every builder report must state which entries it
checked its work against.

## Builder pre-flight

- <a question a builder should ask themselves before starting a class of work> — #<entry ID>
- <another one> — #<entry ID>
...

## Round <N> (<date>)

### <ID> — <one-line name of what broke>
**What broke:** <file:line, the observable symptom, a real measured number if there is one>.
**Why:** <the general class this is an instance of — the sentence that would stop it recurring
under a different file name>.
**Caught by:** <the probe, verifier cycle, or reviewer that found it>.
**Countermeasure:** <what now guards against it, with the file:line of the guard itself, or "none
shipped" if it's flagged rather than fixed>.
**Status:** fixed | open | pre-existing-on-main | design call pending owner.

## History before the loop (<any pre-loop passes/runs this project had>)

<same entry format, IDs prefixed differently (e.g. H- for "history") so they never collide with a
round's own numbering>

## Open items a future pass must not re-discover

Confirmed still red as of round <N>'s close. Filing any of these as a new bug wastes a cycle
re-deriving what is already known.

- **`<probe or symptom>`** — <the fact, in one line, with enough specificity that a search would
  find this line before a builder re-files it>.
```

## The entry format, in one line each

- **What broke** names the file:line and the actual symptom — a real number beats a description
  every time ("0.000 u of travel over 100 frames" tells the next reader exactly what to check).
- **Why** is the general class, not the specific incident — this is the line the pre-flight bullet
  quotes, because the next occurrence will be in a different file.
- **Caught by** names the mechanism, not a person — "verify cycle 1, a throwaway SceneTree probe"
  is reproducible information; "the reviewer noticed" is not.
- **Countermeasure** is either a real, cited fix, or an honest "none shipped" — a countermeasure
  that doesn't exist yet is still worth recording so nobody re-diagnoses the same gap.
- **Status** is one of a fixed vocabulary (`fixed`, `open`, `pre-existing-on-main`, `design call
  pending owner`) so "Open items" can be built by grep, not by re-reading every entry.

## The cross-project catalog

The failure-class catalog lives in `references/catalog.md` — the skill's record of bugs and fixes that
travel between projects. Consult it when writing a pre-flight or a probe; append to it at round close
when a project's Librarian gains a class the catalog does not have. Never paste it into a project's Librarian.
