# Cross-project catalog — failure classes and their countermeasures

This is the record of bugs and fixes that outlive any one project. A project's `Librarian.md` starts
blank and logs instances; this file logs **classes**, each with the countermeasure that stops it, the
project and date it was first seen, and the entry that documents it there. Consult it when writing a
builder pre-flight, a probe, or a verifier seed. Append at round close when a project's Librarian gains
a class this file does not have — the test is "would a builder on a different game repeat this?" If
the answer is no, it stays in the project's Librarian only.

Rules: one class per entry; state the countermeasure as something mechanical (a test shape, a rule a
prompt carries, a hook) rather than "remember to"; keep the origin (project, date, entry ID) so a
reader can go to the instance; never delete — mark a class superseded if a better countermeasure
replaces it. This file lives inside the skill, so repackage the skill after appending if you share it.

## Origin log

| Date | Project | Entries added |
|---|---|---|
| 2026-09-10 | Kingdom: Survival (rounds 1–3, plus its pre-loop art passes) | the initial 20 classes below |
| 2026-09-10 | Kingdom: Survival, round 3 | #21 dead lead |
| 2026-09-11 | Kingdom: Survival, round 3 close | #27 relationship claims in frames |
| 2026-09-11 | Kingdom: Survival, round 5 | #33 vacuous re-entrancy guard, disk-filling backtrace (filed as a second #28; renumbered at the close) |
| 2026-09-11 | Kingdom: Survival, round 5 | #34 backgrounded engine outlives its agent (filed as #29, deleted in a renumbering, re-landed at the round-5 close) |
| 2026-09-12 | Kingdom: Survival, round 5 close | #33 renumbered from a duplicate #28; #35 stale result on a no-result path, #36 append-only cache survives reset, #37 absolute staging, #38 rate gate on a small sample, #39 unaccountable instrument |
| 2026-09-12 | Kingdom: Survival, round 5 verify cycle 1 | #41 wrapper fail-open when the engine refuses the script, #42 nothing gates variety |
| 2026-09-10 | Kingdom: Survival, round 3 | #22 builder-diagnosis-as-claim, #23 engine contention, #24 lattice-phase re-test, #25 gate-with-surviving-control, #26 temp-dir-per-call harness |
| 2026-09-17 | Kingdom: Survival, round 6 close | #43 one-axis clearance on a diagonal lattice, #44 the click guarded but not the router, #45 a clearing sweep frees the permanent resource, #46 a wall-clock-timed driven playtest, #47 a single sample of an intermittent signal, #48 a window derived from the constant under test, #49 a rule fixed for one job class only, #50 a give-up in the wrong currency, #51 a single sample cannot attribute a trajectory, #52 a sandbox-denied pre-flight reads as clean, #53 a chair touching a live worker's tree |
| 2026-09-18 | Kingdom: Survival, round 7 close | #54 refutation-only-in-front-of-it, #55 leash gates choosing not finishing, #56 nearest-free-cell reachability lie, #57 count vs per-entity metric, #58 partial retry re-asks whole batch, #59 stale-frame capture read as record drift, #60 travelling record literal needs a same-session base control |
| 2026-09-18/19 | Kingdom: Survival, round 8 close (the art loop's first round — an instrument round; #71–#72 added at the V8 close) | #61 score delta with uncontrolled confounds, #62 scorer silently discards unexpected inputs, #63 blind instrument's neutral name read as the real id, #64 fresh checkout missing a generated cache, #65 content-liveness cannot detect a stale frame of correct content, #66 parallel authors re-recording one baseline, #67 staging spends its budget on refused actions, #68 threshold derived from the baseline not the seeded defect, #69 gate clause the defect itself satisfies, #70 capped categories bound the reachable score. **One candidate dropped:** "a completion agent ends its turn with graders still running" is a recurrence of #21 (dead lead) and #40 (watcher still armed), not a new class — logged as an instance at Librarian #R8-G07 |
| 2026-09-23 | Kingdom: Survival, round 9 close (closed short by the owner's map redesign) + round 9.5 | #73 sandboxed liveness probe reads a denial as a death, #74 multi-clause verdict read by its first clause, #75 three clean runs are a rate not an absence, #76 polishing art on an unproven layout, #77 a merged lane's regression hides until the whole tree is measured. **Instances, not new classes:** `quit()` overwriting an armed code (#R9-H08 = Librarian #R5-09), a deferred free leaving a registration (#R9-E10 = #R2-36), a probe's hand-rolled road legality (#R9-F05 = #H-16), a gate that measured length not seal (#R9-E03 = class 69), a batched rate gate (#R9-C05 = class 38), the grader model as part of the instrument (#R9-CH06 = class 61) |
| 2026-09-26 | Kingdom: Survival, round 10 close (the map redesign, layout + gameplay; art split to round 10b) | #78 a "fill everything between" recipe draws the opposite of the reference, #79 a self-sweep that excludes the authored inputs certifies nothing about them, #80 an independent checker catches the builder's green (then one shared function), #81 a verdict-changing ruling is not done until the instrument prints it, #82 a premise ruled from one isolation before its effect size, #83 a worker cut off by an account limit resumes in place if it committed as it went. **Instances, not new classes:** two engine runs in one call outrunning the harness ceiling (#R10-G4-04 / #R10-FIX2-06 = class 34's family), a necessary-condition gate the defect satisfies (#R10-FIX3-01 = class 69), a probe literal disagreeing with the generator constant it mirrors (#R10-FIX2-04 = class 48), a stale comment on a moved constant (#R10-FIX6-02 = #R1-26) |
| 2026-10-01 | Kingdom: Survival, round 10b close (the art on the new layout; gameplay finish line PASS, art OPEN) | #84 a seed survives because the guarded path never runs on the fixture, #85 a probe that decodes magnitude cannot see a sign, #86 a probe's default configuration differs from the system's (and a red relayed without its command), #87 frame hashes cannot be compared across captures of a live scene, #88 a cycle sized below the instrument's resolution, #89 a margin gate tipped by an unrelated fix and read rounded, #90 a gate that is off for a class of inputs prints like one that passed |
| 2026-10-02 | Kingdom: Survival, round 10.5c close (the pinned-island water-bake cache; V10.5c PASS) | #108 a cache key built from descriptions of the inputs, #109 a hit hooked at an entry the real caller does not use, #110 a reader that allocates before it bounds / a gate that trusts the record it judges, #111 a writing probe whose isolation check keeps going, #112 a begin/end key check blind to a change made and undone, #113 liveness inferred from a silent signal |
| 2026-10-03 | Kingdom: Survival, rounds 11 and 11b close (the night relight failed its art goal; 11b kept the fixes and reverted the look; merged by Q248) | #114 probe targets steer the look, #115 a grader's rubric carrying the score history, #116 an expected-gain figure with a surviving cap left out, #117 a coverage gate that accepts a missing measurement, #118 a revert left unguarded when its metric is deleted, #119 one exclusion feeding two consumers, #120 grading after seeing the defect in the crops |

## Failure-class catalog

One line each, generalised from entries this project's own `Librarian.md` has recorded. Cite the
matching class by name in a brief's §1/§2 wherever it applies — the point of a catalog is that the
tenth recurrence gets caught by a pre-flight question, not by a tenth fresh diagnosis.

- **Instrument measures the wrong region** — a heuristic (a color mask, a screen-space heuristic)
  stands in for ground truth and silently scores the wrong thing as the signal.
- **Probe certifies its own mechanism, not the outcome** — the check reads the same state variable
  the code under test manipulates, so a change to that bookkeeping passes the check for free.
- **Source grep for behaviour** — a probe greps source text for a function name or call instead of
  observing runtime state; a harmless rename breaks the check without breaking the game.
- **Units error** — two quantities of the same surface shape (a count, a distance) compared without
  checking they share a unit.
- **Wrong quantity / fixed offset** — a check measures a quantity adjacent to the one actually named
  by the claim, or uses one hard-coded reference point where the real target moves.
- **`expect=` measures the camera, not the content** — a frame-content assertion computes something
  nonzero (framing coverage, a bounding rect) even when the claimed content was deleted.
- **Hash/dedup distinctness by exact match** — exact-hash comparison (e.g. MD5) can't express "close
  enough to be the same," so near-identical outputs pass as meaningfully distinct.
- **Check reads the constant it bounds** — both sides of an assertion derive from the same constant,
  so the check moves whenever that constant does and can never catch a bad value.
- **Two masking guards** — two independent guards both fire on every test case built, so disabling
  either one alone still passes; each needs its own input that isolates it from the other.
- **Fail-open CLI default** — an unrecognised flag value silently falls back to a default instead of
  erroring, so a typo is indistinguishable from a deliberate, correct run.
- **Early return above a watchdog** — an early-return branch sits above the timeout/shutdown check
  that is supposed to fire on every path, so that branch can hang forever.
- **Dispatcher default overriding exit code** — a `match`/`switch` default branch runs after a real
  verdict was already set and overwrites it, so the wrong exit code ships regardless of the result.
- **Unregister from one system but not another** — an object is removed from the system that owns
  its logical bookkeeping (e.g. a spatial index) but left registered in a second system that also
  reacts to it (e.g. physics), producing a "removed" object nothing can see but everything still hits.
- **A child's number is relayed unmeasured** — a sub-agent's stated cause or measurement is copied
  into a report without the parent re-running it; the number can be wrong even when the fix is right.
- **Migration by list misses a member** — a set of things to migrate is enumerated as a list from
  memory rather than derived from the code, and the one member with no obvious entry point (no spawn
  path, no constructor call site) is the one silently skipped.
- **Over-correction** — a measured gap is closed in one move at the full measured distance instead
  of half of it, requiring a second, opposite correction later.
- **By-name exemption** — a metric that can't correctly classify some object gets a name-based
  carve-out instead of a fixed predicate, hiding every other object the same exemption also matches.
- **`git add -A` sweep** — a blanket stage-everything commit picks up unrelated in-flight output from
  a second process touching the same tree concurrently (regenerated assets, a scratch file).
- **fp32/fp64 mirror divergence** — the same formula implemented once for CPU (fp64) and once for
  GPU (fp32) diverges outside the range where both precisions agree, producing two different worlds
  from the same seed.
- **Stale comment reintroducing an old rule** — a comment or docstring states an invariant that was
  true once; code changes and nothing re-checks the comment, so it becomes a false claim nobody
  notices until a reader trusts it.
- **Concurrent mutation windows in a shared tree** — two agents (often parent/child) both edit and
  test against the same file at overlapping times, so one's temporary state (a seeded mutation, a
  scratch value) is what the other one's measurement actually reads.

### 21 — A lead that ends its turn with live children is dead
**Class:** a lane-lead agent returns ("I'll report when the children land") while its sub-agents are still running; nothing can wake it (no inter-agent messaging), the children's completion notices go to the chair, and the lane's work sits uncommitted until a human notices.
**Countermeasure:** the lead prompt says "never end your turn while a child is running — wait on it and commit its accepted work before returning"; the chair treats any child report that arrives directly, or a lead notification while children run, as a dead lead and spawns a completion agent at once; the agent log records the stall.
**Origin:** Kingdom: Survival, round 3 Lane B, 2026-09-10 (~8 h stalled) — Mistakes Log 2026-09-10; prompts.md §2.

### 22 — A builder's diagnosis of a probe's red is relayed as fix-ready fact
**Class:** a plausible code-level diagnosis of why a probe is red gets written into a report or ledger, and a lead or owner rules straight to a fix cycle implementing its remedy — without anyone having instrumented the specific failing instances to confirm the diagnosis actually holds there.
**Countermeasure:** before ruling on or spending a cycle implementing a named diagnosis's remedy, instrument the failing cases directly — print the mechanism's own measurement (a distance, a flag, a containment test) for the exact instances that are red — and choose the fix from that measurement, not from the diagnosis's prose. A diagnosis unmeasured against its own failing instances is a claim, not a finding.
**Origin:** Kingdom: Survival, round 3, 2026-09-10 — Librarian #R3-28 (R3-D5's "crossing rule" diagnosis, refuted by instrumenting the two open cells directly).

### 23 — Engine contention inflates timing gates into false FAILs
**Class:** two or more engine/probe processes (a bake, a boot, a census, a headless suite) running concurrently on one machine inflate each other's wall-clock numbers (`bake_ms`, `build_ms`, `first_frame_ms`, `boot_to_playable_ms`, a rendered probe's settle time), producing a FAIL against a budget that was only ever measured on an idle machine.
**Countermeasure:** measure every wall-clock or rendered gate with nothing else running; print the run's own load indicator (e.g. `bake_ms`) on the same line as the verdict — a timing FAIL with a fat `bake_ms` alongside it is contention, not a regression, and should be re-run idle before it is filed as a defect.
**Origin:** Kingdom: Survival, round 3, 2026-09-10 — Librarian #R3-27 (two suites contending on `build_ms`/`boot_to_playable_ms`) and #R3-D9 (`qa_clip` idle 3/10422 vs three-concurrent-probes 254/10423).

### 24 — A lattice/phase change re-tests every geometric guarantee it stands near
**Class:** changing a coarse lattice's phase or resolution to fix one geometric guarantee (a wall seal, a footprint's cell coverage) silently changes which cells read solid or free everywhere else that lattice is consulted — a ford deck, a gate's owning cell, a staging site's connectivity — because those other guarantees were only ever true for the OLD phase, never derived independently of it.
**Countermeasure:** after any lattice phase or resolution change, re-run every probe that depends on that lattice — not only the one the change targeted — before shipping; treat geometrically "unrelated" probes on the same lattice as in scope by default, not as a surprise if they move.
**Origin:** Kingdom: Survival, round 3, 2026-09-10 — Librarian #R3-18 (the `NAV_ORIGIN_OFF` re-phase), #R3-19 (a ford deck sealed by the same change), #R3-31 (gate cells reassigned to flanking walls by the same change).

### 25 — A gate shipped with a control that survived
**Class:** a new pass/fail gate (a settle check, a debounce, a threshold) is added to explain an otherwise-inconsistent measurement, but the gate's own control — the identical run with the gate disabled — reproduces the same result as with the gate enabled, meaning the gate has not been shown to cause the effect credited to it.
**Countermeasure:** never report a new gate's presence as itself the proof of the guarantee it's meant to provide; run the gate's own control (same conditions, gate seeded off) before shipping. If the control survives, ship the gate labelled unproven/uncalibrated, never as a passing safeguard — and say so in both the code's own header and the ledger.
**Origin:** Kingdom: Survival, round 3, 2026-09-10 — Librarian #R3-30 (`game._clip_settled`, R3-D9: the loaded run scored identically with the gate seeded off).

### 26 — Temp-dir-per-call harness hazard
**Class:** a scripted or agentic harness that invokes a fresh shell per step and relies on an environment temp-directory variable (e.g. `$TMPDIR`) for redirect targets can have that directory recreated between calls, silently vanishing a redirect target a prior call set up — the shell's own failure to write is then misread as the thing under test failing.
**Countermeasure:** never rely on a per-call-scoped temp directory surviving into a later call of the same logical run; write harness/probe output to a directory created once and referenced by an absolute, stable path for the whole run. Treat a sudden burst of fast, uniform failures as a harness signal to check before recording it as a finding.
**Origin:** Kingdom: Survival, round 3, 2026-09-10 — Librarian #R3-32 (six probes read as `exit=1` in seconds, traced to `$TMPDIR` recreated per Bash call).

### 27 — A frame's claim that is a relationship needs a gate measured from the frame's own anchor
**Class:** an image-capture gate that counts nouns anywhere in the world (`walls>=1, enemies>=1`) passes a frame whose claim is a relationship ("a Thief AT the pile") while the subject is 500 px away; presence-anywhere generalised to pictures.
**Countermeasure:** a state trigger that fires the shutter on the event (`when=<noun>:<radius>`, bounded by a max wait that reports a miss) and an `expect=near=<noun>:<radius>` clause measured from the frame's `look=` point, kind-filtered and fail-closed without an anchor; prove it by holding the subject away and watching the frame be deleted.
**Origin:** Kingdom: Survival, round 3, 2026-09-10 — Librarian R3-34.

### 28 — A constant proven only by its own read-back
**Class:** a tunable is wired into a subsystem (a pathfinding weight, a blend factor, a cost multiplier) and its gate seeds the constant and asserts the value the subsystem reports back — so the seed goes red on the read-back and green on everything the constant is supposed to influence. The mechanism may be inert and the gate cannot tell.
**Countermeasure:** measure the constant's EFFECT with a layer swap, not its value: run the same inputs with the layer the constant feeds removed from the system and put back, and compare the outcome. If the two agree, the constant is inert — report the gates it was supposed to move as REPORTED rather than asserted, and say so on the verdict line (`weight_effect=none`) so a later reader cannot mistake a green for a working mechanism.
**Origin:** Kingdom: Survival, round 4, 2026-09-10 — Librarian #R4-02 (`NavGrid.ROAD_WEIGHT` 0.67: red on `weight_read`, identical routes with the road layer in or out, on both presets, because `AStarGrid2D`'s octile heuristic is not weight-scaled).

### 29 — One rule, two guards, and the first one hides the second
**Class:** a single design rule is enforced in two places (a router that refuses a shape and a mutator that spares it; a validator and a clamp). On every input the staging can produce, the first guard fires first, so deleting the second changes nothing observable and its mutation SURVIVES — the rule looks doubly protected and is singly tested. This is `verification-discipline` Procedure 2's "two guards can mask each other" as it shows up in a game rule rather than in a test.
**Countermeasure:** for each guard, build an input that trips that guard and not the other — and where the map or the staging cannot produce one, call the second guard DIRECTLY through the production entry point with the same arguments its real caller passes, with a positive control beside it (the same call on an input it must NOT spare). Seed each guard separately; a rule is only as tested as its least-tested half.
**Origin:** Kingdom: Survival, round 4, 2026-09-11 — Librarian #R4-03 (R4-D2's belt rule: with `roads._leg_clear` refusing every belt, no road ever asked the cutting's `spare_belt` and its seed survived).

### 30 — A memoised predicate that grows an input keeps answering for the old ones
**Class:** a cached predicate's invalidation was written for the inputs it had; a later change adds a dependency on a different subsystem, and nothing in that subsystem's change path clears the cache. The predicate then returns a stale answer for the rest of the session — and because the cache is an optimisation, no test names it.
**Countermeasure:** when adding an input to a memoised predicate, revisit its invalidation in the same change: either hook the new input's own change signal, or give the cache an age. Then test it from the new input's side — mutate only the NEW dependency and assert the answer moves, and moves back.
**Origin:** Kingdom: Survival, round 4, 2026-09-11 — Librarian #R4-04 (`roads.linked_to_capital` cached until the road graph changed, after the link started depending on the nav grid).

### 31 — An owner ruling turns a passing regression case red through its STAGING
**Class:** a decision-maker changes a rule, and a regression suite written under the old rule goes red — not because its claim is wrong but because its setup is now illegal (a wall staged where walls are no longer allowed, an expected payout that a new cap now clamps). The pressure at that moment is to relax the assertion, which destroys the case's value permanently.
**Countermeasure:** restage to the new rule and never loosen it — move the staging until it is legal under the ruling, keep every original assertion, and where the new rule is the kind that could be dodged (a cap, a floor, a radius) add an assertion that the new rule BITES in this staging, so the restaged case cannot quietly become a test of the old world. Attribute each red with a diagnostic mutation before touching anything, so "stale staging" is a measurement and not an assumption.
**Origin:** Kingdom: Survival, round 4, 2026-09-11 — Librarian #R4-05 (three Phase-1 cases restaged against owner rulings Q42/Q49 and the purse cap; the cap's clamp is now asserted to bite).

### 32 — Green against a stand-in is green against the stand-in
**Class:** a lane blocked on another lane's interface ships a named placeholder and proves its own case against it. The case passes, the number is quoted in a report, and when the real implementation lands the case fails on a step the placeholder had made unnecessary — because the placeholder answered unconditionally where the real thing has preconditions (a ramp, a wait, an error path).
**Countermeasure:** a stand-in's green is provisional and must be labelled so in the report; re-run every number the moment the real implementation merges, and expect the first failure to be a MISSING STEP in the test rather than a defect in the code. Give the placeholder a name that cannot hide (`_LINK_STUB`) and a gate that fails while it is present, so the merge proves itself.
**Origin:** Kingdom: Survival, round 4, 2026-09-11 — Librarian #R4-07 (`case=link` never grew the road, because the stand-in reported a link without one).

### 33 — A re-entrancy guard keyed on "the cache is empty" recurses when the cache is legitimately empty
**Class:** a lazily-built table guards re-entry by testing its own emptiness; a generator that leaves the table empty mid-build makes the guard vacuous, and a deep recursion's backtrace can fill the disk and take every tool down with it.
**Countermeasure:** an explicit in-progress flag plus a hard depth cap that errors and returns; a probe that seeds the empty table and asserts the cap fires; engine stdout/stderr captured through a size cap in any harness that can run a build.
**Origin:** Kingdom: Survival, round 5 Lane A, 2026-09-11 — a 47 GB backtrace; ~2 h lost.

### 34 — A backgrounded engine outlives the agent that started it and writes outside every cap
**Class:** a worker backgrounds a long engine or build run; the worker ends, or is stopped, but the process survives — the harness's own stop does not kill it — and its output goes to a capture file that no project wrapper bounds. The disk fills and every tool on the machine stops.
**Countermeasure:** engine and build runs are never backgrounded by a worker; the ONE wrapper every run goes through refuses to start below a free-disk floor, enforces wall-clock and resident-memory ceilings, caps output, and records the real exit code of the process rather than the last stage of its pipeline. Where the harness itself caps foreground calls below a long run's duration, launch it and BLOCK on it in the same turn rather than leaving it unattended — and check nothing else is already running before launching, because "one at a time" is the property the ceilings assume. Recovery may be impossible from inside a sandbox that cannot list or kill processes, so the wrapper must make recovery unnecessary.
**Origin:** Kingdom: Survival, round 5 Lane A, 2026-09-11 — ~170 GB written twice; ~3 h lost. Re-landed at the round-5 close after being deleted in a renumbering, against this file's own "never delete" rule.

### 35 — A seed that produces nothing leaves the previous world in place
**Class:** a generator, loader or importer fails to produce a result, and the surrounding object updates the members that DESCRIBE the result (name, id, mode, seed) while leaving the result member itself pointing at the previous one. The "did it work" test — usually `result == null` — is then false, and the caller proceeds on stale data. A fallback nobody chose, and invisible precisely because every label says otherwise.
**Countermeasure:** the no-result path clears the result member first and the descriptive members with it; the test for failure is the result, never a status flag beside it. Prove it by running two inputs in one process where the second produces nothing, and assert the caller sees a failure rather than the first input's output — a suite that starts a fresh process per input can never see this.
**Origin:** Kingdom: Survival, round 5, 2026-09-12 — Librarian #R5-04 (`use_preset` left `_spec` on the previous island; two seeds reported a rejection naming an anchor at the identical coordinate, because both were validating a third seed's island). Against an explicit owner decision that there be no fallback.

### 36 — An append-only cache that survives reset() poisons the next configuration
**Class:** a build appends to a side array as it resolves things, and the teardown between configurations clears the primary caches but not the side array. The next configuration reads the previous one's entries through a parallel index, and the corruption is invisible to any test that uses one configuration per process.
**Countermeasure:** teardown clears every member the build appends to, and a probe runs the configurations INTERLEAVED — A, B, A, B — comparing all four output hashes and the lengths of the append-only arrays. Seeding the removal of the clears must turn that probe red with growing lengths (4/8/12/16), which is the signature.
**Origin:** Kingdom: Survival, round 5, 2026-09-12 — Librarian #R5-03 (`_ford_axes`/`_ford_rs` survived `reset()`; one preset's baked height field read the other preset's fords).

### 37 — A probe staged on absolute coordinates is staged on one world
**Class:** a regression case hard-codes a position, a distance or a pair of endpoints that were chosen against one map, scene or dataset. When a second one appears — a bigger level, a generated variant, another locale — the staging lands somewhere meaningless and the case fails on an assertion about something it never set up. The failure names the assertion, not the staging, so it reads as a regression in the code under test.
**Countermeasure:** scale or derive the staging from the world's own geometry, choosing the expression so it is EXACTLY the identity on the original world (a ratio that is 1.0 there) — then the original case is unchanged by construction rather than by re-measurement. And assert the staging succeeded, in its own words, BEFORE asserting anything about it: an empty route is "unstaged", not "the router dropped no waypoints".
**Origin:** Kingdom: Survival, round 5, 2026-09-12 — Librarian #R5-11 (a string-pull case staged at (500, -500), a point on the ×1 island; on the ×3 island A* returned no path at all and the case had been red on the generated preset unnoticed because the suite had only ever been run on the other one).

### 38 — A rate gate on a small sample is arithmetic dressed as evidence
**Class:** a gate is put on a RATE — a rejection percentage, a flake rate, an error rate — and the suite's default run is a handful of samples. The rate then quantises to the sample size (0/20/40/60 % at n=5), so either the gate is red on noise or, once slack is added for that, the effective threshold is so wide that nothing could fail it. Both readings are reported as gate results.
**Countermeasure:** state the minimum n at which the rate is ASSERTED and print `gated=0` with the reason below it, rather than widening the threshold until it passes. Keep every other assertion in the case live so it is never vacuous, and derive the threshold itself from a sweep large enough to resolve it. A gate that is not being applied must say so on its own verdict line.
**Origin:** Kingdom: Survival, round 5, 2026-09-12 — Librarian #R5-12 (a 20 % rejection gate derived from 20 seeds read `<=70.0` on the suite's default two, which no generator could fail).

### 39 — An instrument whose reading you cannot account for is not evidence
**Class:** a measurement is built to settle whether a gate is asking the right question, and its output is plausible but unexplained — identical values across cases that should differ, a constant offset, a number nobody can derive. The temptation is to use it anyway, because it points the way the author already suspected, and to relax the gate on the strength of it.
**Countermeasure:** delete the instrument and write the question down as open. A confounded measurement is worse than none, because it converts a known unknown into a false certainty — and a gate relaxed on it cannot be un-relaxed by anyone who was not there. Where the confound is a coordinate-space mismatch (a field measured in one space, sampled in another), say which space, because the next author will reach for the same instrument.
**Origin:** Kingdom: Survival, round 5, 2026-09-12 — Librarian #R5-15 (a distance-field gradient meant to detect a medial axis carried the warp's Jacobian; it read 0.832 on three unrelated seeds and the gate was left at 1.0 rather than loosened).

### 40 — A worker that reports done with a watcher still armed is re-woken forever
**Class:** a worker arms a background monitor or a backgrounded wait, reports its result, and exits; the harness keeps the watcher alive and re-invokes the worker on every event, each wake spawning more tasks — for days, invisibly to the chair, visibly to the owner as an ever-growing task count.
**Countermeasure:** every worker prompt ends with "stop every Monitor and background task you armed before you report"; the chair's completion checklist lists the live agents after each notice (a stop request on a bogus id returns the list) and stops any agent that has already reported; the agent log records the stop.
**Origin:** Kingdom: Survival, 2026-09-12 — a round-3 fix worker re-woken for two days; 64 tasks and growing.

### 41 — A probe wrapper that reports the engine's exit code is still fail-open when the engine never ran the script
**Class:** the wrapper captures the real exit code, but the engine returns 0 after printing "can't load the script" (wrong base class, missing file, parse error) — so a probe that never executed reads as a pass. Rendered-only scripts handed to the headless runner are the common trigger.
**Countermeasure:** the wrapper greps the captured log for the engine's refusal phrases and exits its own reserved non-zero code; prove it by handing the wrapper a script the engine cannot run (expect the refusal code) and by deleting the grep block (expect 0, the RED), then restore byte-identically.
**Origin:** Kingdom: Survival, round 5 verify cycle 1, 2026-09-12 — `run_probe.sh qa_clip` exited 0 on "doesn't inherit from SceneTree or MainLoop"; ledger R5-D12.

### 42 — Every guarantee is a floor, so nothing gates variety
**Class:** a procedural generator ships with a full sweep of per-seed guarantees and passes, but no probe asserts that seeds DIFFER: a seeded defect that collapses a random span to a constant (every coast the same width) survives everything.
**Countermeasure:** a `variety` case with a per-feature spread floor over N seeds (range or standard deviation of the features the design says vary), thresholds derived from the shipped spread and stated; seed it by zeroing one span.
**Origin:** Kingdom: Survival, round 5 verify cycle 1, 2026-09-12 — `COAST_W_SPAN` 0.90 → 0.0 SURVIVED 17 cases on 20 seeds; ledger R5-D10, owner Q51.

### 43 — A clearance derived on one axis is derived on one axis
**Class:** a spacing, corridor width or margin is worked out for the axis-aligned case — "leave one cell between them" — and applied to a grid whose router charges more on the diagonal. Placements at a bearing and a phase the derivation never considered weld shut, and the symptom is not "two things are too close": it is a region of the world that quietly stops being reachable, days later, in a system that does not mention spacing at all. The classic amplifier is a router configured to refuse diagonal moves beside an obstacle, which makes a one-cell corridor 4-connected: **a corridor narrower than a cell does not exist for the router, whatever the geometry says.**
**Countermeasure:** derive the margin from the LATTICE's diagonal pitch (`cell·√2`, or the graph's own worst-case step), and prove the number by sweeping bearings × sub-cell phases rather than by testing the axis-aligned pair — the sweep is the measurement, and the smallest margin that measures clean is the one to take (not the comfortable round number). Assert the region's reachable-cell count before and after a placement, because that is where the defect actually shows.
**Origin:** Kingdom: Survival, round 6, 2026-09-15 — Librarian round 6 / ledger R6-D2, R6-D8. `d >= rA + rB + CELL` left 43 of 175 bearing/phase placements welded and `+ CELL·√2` left zero; before it, the seventh building closed the capital's ring and the reachable region fell 7 148 → 59 cells.

### 44 — A placement rule guards the click and not the router, or the other way round
**Class:** a rule about where two things may coexist — a building and a road, a wall and a door, a cable and a duct — is implemented at ONE of the two moments at which they can meet. Guarding only the interactive placement leaves the automatic router free to draw its line through what is already standing; guarding only the router leaves the player free to build on the route. Either half alone passes its own test, and the failure arrives far downstream as a link, a path or a circuit that will not come back.
**Countermeasure:** name the rule once and give it two readers, explicitly — "placement guards the click, the router guards the route" — and put a probe on each direction that the other cannot satisfy. Where one side is declared indestructible by design, the OTHER side is the one that must give way, and the refusal must be visible at the moment of the click rather than inferred later.
**Origin:** Kingdom: Survival, round 6, 2026-09-16 — ledger R6-D20, R6-D21(c), R6-D23; GDD §12 row 115. A town's own tent took 20 cells of its supply road and killed the link permanently with no refusal and no message; the router, fixed first, was then found bending roads through standing buildings.

### 45 — A sweep that clears props clears the permanent thing the job was for
**Class:** a permanent, design-guaranteed resource (a node, a landmark, a fixed spawn) is implemented by extending the same base class as the disposable scenery around it, and inherits its group membership. Every clearing, culling or cleanup sweep in the project then removes it by CLASS while every piece of documentation says it is permanent. The worst instance is self-defeating: the infrastructure built to exploit the resource is what clears it.
**Countermeasure:** when a ruling makes a thing permanent, grep every sweep that can remove its CLASS, not its name, and add an explicit survival assertion to the generator's own guarantees (`<thing>_survives_clearing=1`) plus a per-seed plan-agreement check. Print the two lists — planned and live — before theorising about why a lookup fails; a census answers in seconds what a data-model story takes a cycle to disprove.
**Origin:** Kingdom: Survival, round 6, 2026-09-16 — ledger R6-D21(a), R6-D23. `lode.gd` extended `prop.gd`, so the road built to serve the quarry town freed the outcrop the town was founded on; the previous cycle had attributed it to a round-3-vs-round-5 data-model mismatch, and three of the four nodes were byte-exactly where they were planned.

### 46 — A driven playtest timed by the wall clock is not a gate
**Class:** a long scripted run — a playthrough, a soak, an end-to-end scenario — advances its simulation on real elapsed time while its actors step on a fixed tick. The two agree on AVERAGE, so nothing looks wrong, and the number of ticks inside one scripted interval is decided by machine load. The same seed is then not the same run: two executions of an identical tree differ by a couple of frames and produce materially different outcomes, and every gate downstream of the run inherits that. Freezing the simulation is not enough on its own — a chunked or budgeted BOOT takes a variable number of ticks, so a per-tick accumulator beside it starts the first interval at a different phase (the signature is two runs with an IDENTICAL frame count that part anyway).
**Countermeasure:** one flag moves every simulation loop and every timer onto the fixed step, the boot included, and every global RNG site is seeded from the run's own seed argument. The test for "is this loop simulation?" is whether it reads or writes state the run's ledger can see, not which file it lives in. Prove it by publishing a per-interval ledger and requiring two full runs to be MD5-equal, and keep a wall-clock control that still diverges — otherwise the equality is untested.
**Origin:** Kingdom: Survival, round 6, 2026-09-16 — ledger R6-D19(b), R6-D20; GDD §12 row 117c. Two 28-day runs of an identical tree differed by two frames and eleven seconds; after the fix, 84 dawn lines byte-identical and the wall-clock control parts at dawn 3.

### 47 — A single sample of an intermittent signal is a coin flip, and it reads green once
**Class:** a requirement about a state that FLICKERS — a lamp fed by yesterday's delivery, a health check, an intermittent connection — is gated by reading the state once, at one moment. The read is a coin flip: the same tree and the same seed give both answers, and whichever one the reporting run got is written down as the result. A green from this shape is indistinguishable from a real pass and is usually the one that gets quoted.
**Countermeasure:** a window plus a threshold, not a wider window: assert the state at SOME point up to the deadline AND on at least M of a named window after it, on two separate tokens, so flicker is measured instead of hidden. This is strictly stronger than the single sample it replaces, which is why it is not a loosening. If a previous cycle reported the single-sample gate green, re-run it before building on it.
**Origin:** Kingdom: Survival, round 6, 2026-09-15/16 — ledger R6-D19(c), R6-D20; owner Q95; GDD §12 row 117d. The Wood rung read 1100 / 1000 / 1100 on consecutive days and two runs of one tree gave `wood_lit_d15` 0 and 1; a cycle had already reported it green on one sample.

### 48 — A window, tolerance or budget derived from the constant it is checking
**Class:** the check that bounds a constant computes its own expected value FROM that constant — a stability window written as `to - from + 1`, a tolerance written as a fraction of the value under test, an expected count derived from the size being gated. Seeding the constant then moves both sides together and nothing goes red. It is the "proved to be SET, never proved to DO anything" failure produced by its own arithmetic, and it survives review because the expression looks like a derivation rather than a duplication. Its sibling: a probe that SELECTS its staging using the constant under test — seed the constant and the staging vanishes, the row reports `staged=0`, and only the read-back assertion goes red.
**Countermeasure:** every window length, tolerance and expected count gets its OWN literal, taken from the specification, with the derived value asserted equal to it as a separate line so a change goes red twice instead of quietly widening. A probe that gates a constant holds its own copy of the number it is gating, and stages with that copy. Only actually seeding the constant proves either.
**Origin:** Kingdom: Survival, round 6, 2026-09-15/16 — ledger R6-D18, R6-D20; Librarian #R4-02's shape reappearing inside the check written to catch it, and #R4-13's mechanism producing the staging half.

### 49 — A rule fixed for one job class and not for its siblings
**Class:** a defect is found in one actor's behaviour — a worker that commits to a target by straight-line distance with no route test — and the fix is applied where it was found. The identical code shape in the sibling classes is left alone, because the brief named a symptom and not a predicate. The siblings then reproduce the original defect verbatim, months later, and it is re-diagnosed from scratch.
**Countermeasure:** when a fix lands on one member of a family, grep the family for the PREDICATE (the distance test, the commitment, the give-up) and either fix every member in the same commit or name the ones left out, with their measured counters, in the report. A per-class counter (`<class>_saw_unreachable=0/N`) makes the omission visible on the verdict line rather than in the diff.
**Origin:** Kingdom: Survival, round 6, 2026-09-15/16 — ledger R6-D9(b), R6-D17, R6-D21(b), R6-D23(b). `_pick_reachable` was built for hunters; loggers and quarrymen kept picking by straight line for three fix cycles, and the Wood rung's red was re-attributed twice before it was applied to them.

### 50 — A give-up expressed in a different currency from the reach it guards
**Class:** a bail-out that exists to stop an actor pursuing something unreachable is measured in TIME while the reach it sits inside is measured in DISTANCE (or in routes, or in retries). The two are reconcilable only at one speed and one layout, so the rule works while the easy candidates last and then locks the actor out permanently — with every "is it stuck?" counter reading healthy, because it is not stuck: it is re-targeting. A give-up list that evicts by age turns the lock-out into a rotation, re-offering the same impossible candidate for ever.
**Countermeasure:** express the give-up in the same currency as the reach — route length, or a route test — and give the job a companion STATE ("nothing in reach") that it can act on and a probe can read, rather than leaving the give-up list as the only memory. Put a counter on the eviction ring itself; a rotation is invisible to every other instrument.
**Origin:** Kingdom: Survival, round 6, 2026-09-16 — ledger R6-D26; owner Q102. `CHOP_GIVEUP_S` 8 s at 95 u/s buys ~760 u of straight walking against a 640 u reach with the depot 272 u the other way; once the near grove was felled out every leg exceeded the give-up and both loggers cycled for the rest of a 28-day run with `kicks=0` and a valid route under them.

### 51 — A single sample cannot attribute a trajectory
**Class:** a diagnostic samples an actor once per interval — one position, one target, one destination a day — and a cause is inferred from the sequence: "it is commuting between A and B", "it is thrashing between two states". A finer trace refutes it, because a single sample cannot distinguish a journey from a coincidence of endpoints, and the wrong cause then drives a design ruling and a whole fix cycle.
**Countermeasure:** a diagnostic that attributes a WALK needs a CADENCE, not a sample; and before blaming a code path, check a counter that says the path RAN. Both are cheap, and the second is the one that fails fast: the workers in the instance below were holding nothing at 100 % of samples, so the delivery code being blamed was never entered at all.
**Origin:** Kingdom: Survival, round 6, 2026-09-16 — ledger R6-D24 (refuted) and R6-D26. A one-midday-sample trace produced an owner-confirmed design ruling about where workers deliver; a 5-second cadence on the same run showed one camp, one town, and `carry=0` throughout.

### 52 — A pre-flight check the sandbox denies reads as a clean result
**Class:** a worker guards a dangerous action with a pre-flight — "is anything already running?", "is the port free?", "does this process exist?" — using a facility the sandbox, container or permission model does not grant it. The call fails fast and the failure looks exactly like the all-clear the worker was hoping for, so the guard is not merely absent: it is confidently wrong. The same shape disables watchdogs written against the same facility.
**Countermeasure:** wait on an ARTEFACT the process itself writes (a run's own return-code file, a lock file, a socket) rather than on the absence of something the environment may not let you see; and where a guard depends on an environment capability, assert that capability first and refuse loudly when it is missing. Never widen the sandbox to make the guard work — move the guard to something inside it.
**Origin:** Kingdom: Survival, round 6, 2026-09-15/16 — ledger R6-D14, R6-D22; Librarian round 6. A `pgrep` pre-flight inside a worker returned "no such process" instantly because the sandbox cannot list processes at all, and the probe wrapper's own RSS watchdog, built on the same `pgrep`, never fires there either.

### 53 — A chair that touches a worker's tree or processes while the worker is live
**Class:** an orchestrator reads a worker as dead — it has not spoken for a while, or a notification arrived out of order — and intervenes on shared state: kills what it takes to be an orphaned process, amends or rebases the shared branch, or spawns a second agent to "finish the job". The worker is alive; two agents now write the same tree, or several long jobs run at once, and the damage is attributed to the worker's own code.
**Countermeasure:** before killing anything, check the process tree's PARENT chain and the agent's re-wake behaviour, and kill the wrapper's root rather than a child (a suite that shells one child per case has many). Before amending or rebasing, check whether any agent is live on that branch — an amend on a shared tree is never a bookkeeping change. Treat a completion notice that arrives while an agent's children are still running as a DEAD LEAD and re-spawn one completion agent, exactly one, rather than acting on the tree directly.
**Origin:** Kingdom: Survival, round 6, 2026-09-12 / 09-16 — ledger R6-D6 and the round-6 close. A `case=all` child engine was killed and a redundant completion agent spawned, leaving three engines running for ~12 minutes; separately a commit was amended on a shared tree while a worker was building on it.

### 54 — A refutation is only true of the cause in front of it
**Class:** A diagnostic investigates two (or more) suspected causes stacked in a pipeline — a downstream cause can only produce an observable symptom once an upstream cause stops suppressing it. Testing or "refuting" the downstream cause while the upstream one is still active reads as a clean refutation, but the refutation is only ever a statement about the downstream cause's behaviour with the upstream one still in front of it; fixing the upstream cause can immediately reveal that the downstream cause was real all along.
**Countermeasure:** state every refutation of a downstream cause with the upstream cause's status attached ("B refuted while A still active"), never as an unconditioned verdict; after fixing an upstream cause, re-open and re-test every downstream cause that was refuted underneath it before treating the chain as closed.
**Origin:** Kingdom: Survival, round 7 Lane A, 2026-09-18 — Librarian R7-A02, ledger R7-D3. The lane's own earlier commit message read "H2 refuted"; H2 (a pathfinder reporting a target reachable when it was not) was only unobservable while H1 (a leash aborting the approach before arrival) kept every hunt at `kills=0` from dawn 7 — fixing H1 exposed H2 within one run.

### 55 — A leash re-tested every tick gates finishing, not just choosing
**Class:** A distance leash is meant to gate which target may be chosen, but the same test is re-evaluated on every subsequent tick against the actor's current position rather than only at pick time. Once the real route to the chosen target is materially longer than the straight-line distance the leash measures, the actor's own straight-line distance crosses the leash mid-approach and the in-progress pursuit is aborted before it can ever finish, however close the actor already is by route.
**Countermeasure:** consult the leash only at selection time and let a committed target persist through the leash's later readings; gate abandonment of an in-progress pursuit by a distance-walked-versus-route-length rule instead, and prove the leash's scope by seeding the leash back into the per-tick recheck and confirming pursuit collapses.
**Origin:** Kingdom: Survival, round 7 Lane A, 2026-09-18 — ledger R7-D3, round07-laneA-report.md §3. `HUNT_RANGE` 680 is a straight line from the hunter while the route to a deer across the river measured 3.9–7.1× that line, so the hunter's own straight-line distance passed the leash within seconds of committing and the pick came back null every time (`kills=0` at every dawn from 7); seeding the leash back into the per-tick recheck reproduced it (`kills_shape=1` at a 3.18× detour).

### 56 — A path solver that cannot fail makes reachability lie
**Class:** A pathfinding routine built to always return something walks an unreachable goal out to the nearest free cell instead of failing, so a reachability check built on "did a path come back" — rather than on where the path actually ends — reports a goal reachable when it is standing on solid or occupied ground. A caller that trusts the check arrives at the substitute cell, stops short of the real goal, and the failure then looks like the caller giving up rather than like the check having lied.
**Countermeasure:** a reachability check tests the resolved path's END distance against the actual goal (or the goal cell's own solidity) before answering yes, not merely whether the solver returned a non-empty path; prove it by pointing the check at a goal buried in an obstacle's halo and confirming it now answers no.
**Origin:** Kingdom: Survival, round 7 Lane A, 2026-09-18 — Librarian R7-A05, ledger R7-D3. `find_path` walked a deer standing inside a grove trunk's nav halo out to the nearest free cell, so `can_reach` answered yes; the hunter arrived 27 u away against a 22 u kill test and stood there (`deer_solid=1 route_end_d=53`). Seeding the check to skip the end-distance test reproduced it at scale (`halo_targeted=594 kills_halo=0 route_end_d=54`).

### 57 — A count cannot classify a rule about which individuals
**Class:** A claim about individuals keeping their identity or role ("X stays X") is gated with an aggregate COUNT (a min==max equality, a total) instead of tracking the individuals themselves. Churn that replaces one member with another of the same count — one instance losing the role while a different instance gains it inside the same window — leaves the count unchanged and the gate green even though the claim is false for the specific individual; the same count can also go red on a legitimate, blameless change that violates nothing.
**Countermeasure:** track the specific individuals present at the claim's starting condition by id, and ask on every subsequent sample whether each one specifically still holds the role, reporting lost/gone/no-subject counts separately from any legitimate churn; validate the replacement by seeding a genuine loss and confirming the new metric reds while the old count-based one stays identical on the same run.
**Origin:** Kingdom: Survival, round 7 fix cycle 1, 2026-09-18 — Librarian R7-C01. `winter_farmers_min == winter_farmers_max` gated GDD 6.3 ("a winter farmer stays a farmer") and failed when farm5 finished on winter's dawn 27 and two idle hands filled its slots — nobody lost a job, the gate read `winter_farmers=8..10` as a violation. Tracking farmers by instance id and seeding an actual mid-winter job loss reds the new `winter_farmers_lost=1` while `winter_farmers=8..10` reproduces byte-identically on the same run.

### 58 — A partial retry that re-asks for the whole batch over-spends the remainder
**Class:** A script or job step requests N items, an environment limit (no free slot, no capacity) delivers fewer than N, and the caller's retry logic re-issues the request for the ORIGINAL N on the next attempt instead of for the shortfall still owed. Each retry then over-collects by however much the prior partial attempt already obtained, no single step's own report shows an overrun, and the total drifts above the intended budget invisibly across several attempts.
**Countermeasure:** a retryable step tracks and requests only its remaining owed amount, never the step's full original size; gate the total actually taken against the step's own summed budget as an explicit assertion, and carry the specific refusal cause — not just a resulting count — out of every partial attempt so a shortfall reads as its cause rather than as an unrelated resource shortage.
**Origin:** Kingdom: Survival, round 7 fix cycle 1, 2026-09-18 — Librarian R7-C03, ledger R7-10. `_yr_hire(n)`'s no-bed failure was retried at full step size by `_yr_do_step`, so `hire2_d` — budgeted for two villagers — took one on day 6, one on day 7 and two on day 8 (four total), producing the round-6 close's unexplained `hires=15` against the script's 13-villager budget. Reverting the remainder-tracking fix on the shipped tree left the seed vacuous (`hires=17`, SURVIVED, because no step there ever takes a partial batch), so the instance was reproduced instead on the round-6 tree (`hires=15`, `ledger_md5=7cfee16e6e0a796c5a042917c19418cd`).

### 59 — A rendered probe's stale frame reads as a record drift
**Class:** A screenshot- or render-based probe reads whatever frame the window server currently has presented rather than forcing a fresh render of the state under test. After a long-running or idle rendering process, the presented frame can be stale — left over from an earlier build or an earlier moment — and a base-versus-branch pixel or hash comparison built on it reports a large "drift" that has nothing to do with any code change between the two runs. The signature is every tree on the machine reading identical to every other tree while none of them reproduces the originally recorded reference.
**Countermeasure:** assert the capture is live before trusting its comparison (an independent liveness gate on the frame's own content, not on the comparison result), and on a red render-comparison, re-capture with a confirmed live framebuffer before concluding a regression — never before checking whether the capturing process itself is stale.
**Origin:** Kingdom: Survival, round 7 Lane B, 2026-09-17 — ledger R7-D1. `qa_classic_frames` read `match=0/2` with the editor app running 1.5 days; `r7/select`, the untouched base `5473676`, and the recording commit `65baa25` all rendered byte-identically to each other that day and none reproduced the recorded pair (`a8acecd1…`/`ca6e6c56…`). Lane A re-captured with a live framebuffer the next day (`FB_LIVE land_px=135041 gate=1`) and read `match=2/2` on the same digests, unchanged.

### 60 — A travelling record literal needs a same-session base as its control
**Class:** A pixel or hash baseline recorded once, on one machine and session, is treated afterward as a portable literal that any future run must reproduce exactly. A rendered capture depends on session-local state (a stale framebuffer, a driver, a font cache) the literal cannot encode, so a comparison against it silently stops testing the branch and starts testing an unstated environmental confound instead — a real red becomes indistinguishable from an environment that has simply moved on since the recording.
**Countermeasure:** capture a same-session BASE (the last-known-good tree) alongside the branch under test and compare branch-versus-session-base rather than branch-versus-recorded-literal; treat the recorded literal itself as suspect, not the branch, whenever the session-base also fails to reproduce it.
**Origin:** Kingdom: Survival, round 7 Lane B, 2026-09-17 — ledger R7-D1, round07-laneB-report.md §6. `qa_classic_frames`'s recorded pair (`a8acecd1…`/`ca6e6c56…`) reproduced at none of three same-day trees (`self_diff=0` in every run), so Lane B ran base (`5473676`) and branch (`r7/select`) in the same session instead and reported the comparison that mattered — base and branch hashed identically (`b8facfb7…`/`77fa01cd…` on both v0/v6) — rather than treating the un-reproduced literal as a regression.

### 61 — A score delta with uncontrolled confounds is not a finding
**Class:** A subjective or model-produced measurement (a grade, a rubric score, an LLM judge, a human panel) is taken before a change and after it, and the difference is read as the change's effect — while the *instrument* also moved between the two readings: a re-worded prompt, a different judge population, an added constraint, a new scoring rule. Every such difference is the sum of the subject's change and the instrument's, and nothing in the output separates them. The failure is not the confound, which is often unavoidable; it is acting on the delta, because the next round of work is then aimed by an arithmetic nobody can attribute.
**Countermeasure:** before the cycle runs, write down what each possible result will be taken to MEAN, with every confound named — a pre-registered reading rule. Then run the instrument's own CONTROL: re-measure the OLD subject (byte-identical inputs, re-derived deterministically if they must be rebuilt) under the NEW instrument, so the instrument's own contribution is a number rather than a worry. And treat a delta smaller than the instrument's within-cycle agreement as no measurement at all, whichever direction it points.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D19 / R8-D20, Librarian #R8-G01. A blind art grade fell 5.16 → 4.40 day after four art lanes merged, with three live confounds; re-grading the ORIGINAL frames (18/18 pack files byte-identical) under the new prompt read 3.98, so the prompt alone accounted for more than the entire observed fall, and the true art delta was +0.42 / −0.54 — inside the graders' own spread.

### 62 — A scorer that silently discards inputs it was not told to expect
**Class:** An aggregation step (a scorer, a parser, an importer) accepts a producer's output and keeps only the fields it was configured for, dropping the rest without a count, a warning or an error. The result is arithmetic over an unstated subset: two producers that behaved differently are averaged as though they had behaved the same, and the discard rate — which is the real finding — never appears anywhere. Tightening the producer's contract later then LOOKS like a scoring change when it is really the first time every input was used.
**Countermeasure:** every aggregation prints what it DROPPED alongside what it used — a count per producer per category, and zero printed explicitly as zero — and refuses, or at minimum flags, a run whose discard count is non-zero. When a producer's contract is tightened so the discards go to zero, treat the tightening as a NEW BASELINE and re-measure the old subject under it (class 61), never as a clarification.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D20, Librarian #R8-R04 / #R8-G01. `grade_score.py` discarded 48 and 50 surplus `SCORE` lines from the two graders of one cycle, averaging each frame over whatever set that grader happened to choose; one frame read 6.00 from a grader scoring two categories and 4.42 from a grader scoring three, and the gap was arithmetic, not judgement.

### 63 — A blind instrument's neutral name read as the real identifier
**Class:** An instrument deliberately anonymises and shuffles its inputs so the judge cannot use their identity — neutral filenames, randomised order, an answer key held outside the judge's reach. A downstream reader then quotes the judge's report using those neutral names in a context full of REAL identifiers of the same shape, and a defect reported against anonymous item N is acted on as though it were real item N. The anonymisation that makes the instrument trustworthy is exactly what makes its output unsafe to quote unresolved.
**Countermeasure:** every quoted item from a blind report is resolved through the answer key to the real identifier BEFORE any investigation is planned, and a report citing a neutral name states which cycle's key it belongs to. Make the two namespaces textually distinguishable where you can. As always, reproduce the defect on the resolved item before spending a bisect on it.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D21(a), Librarian #R8-G02. A chair ruling ordered "the full-buffer blur on the UI frame F8" fixed at the root; the grader's `f08` was the CONTROL frame, which the packer blurs on purpose, and the real F8's measured text-edge fraction was 0.1657 against the control's 0.0000. A four-tree bisect was queued and not spent.

### 64 — A fresh checkout or worktree renders differently because a generated cache is missing
**Class:** A build system keeps a generated, gitignored cache (imported textures, shader binaries, a package cache) that is produced by a workflow the automated entry point never runs. A fresh clone or `git worktree` therefore builds a subtly DIFFERENT artifact — assets silently failing to load, a fallback path taken — and any pixel, hash or performance comparison taken there differs from the recorded baseline by a large, consistent margin that looks exactly like a regression or like a machine-specific record. A liveness or content check cannot see it, because the output is real, current and wrong.
**Countermeasure:** a working copy that will produce a measurement populates the generated cache first (copy it from a checkout that has one) and proves it with a BASE CONTROL — the untouched reference reproducing its recorded value — before any branch number is quoted. Treat a resource-load error in a capture log as VOIDING that capture, and count those errors as a gate rather than reading them as noise.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — Librarian #R8-D01 / #R8-A03 / #R8-C02, ledger R8-D5 / R8-D6. Three lanes independently hit `match=0/2` on the classic reference pair from worktrees; `.godot/` is gitignored and `-s <script>` never builds it, so four ground textures failed to load, the ground drew untextured (+31.5/+32.6/+19.1 mean RGB over 21–45 % of the frame) and the resulting hashes were the exact pair a previous round had recorded as a machine-bound baseline. `cp -Rc .godot` restored `match=2/2` in the same session.

### 65 — A liveness check on CONTENT cannot detect a stale frame of correct content
**Class:** A capture-based probe guards against stale output with a content assertion — enough pixels of the right kind, a non-empty buffer, a plausible histogram. The guard passes on any frame that LOOKS right, including a perfectly rendered frame of an earlier moment: under window occlusion, compositor back-pressure or system load, presentation stops while the process keeps simulating, so the capture API keeps returning an old, complete, entirely plausible picture. The measurement is then of a different instant than the one under test, with no error anywhere.
**Countermeasure:** make the frame prove it is THIS run's frame, not merely a valid one — write a per-run nonce into the surface, capture, clear it, capture again, and require both halves; front the capture surface and keep it above other windows before the settle; retry the freshness grab a bounded number of times inside the run and REFUSE rather than quote. A refused capture is never quoted, and "the machine must be locked" is a hypothesis to measure (session state, load, the window's own presentation), not a conclusion.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D11 / R8-D13 / R8-D14, Librarian #R8-G04 / #R8-R03. Captures refused with `land_px=146`; the frame was a fully rendered boot banner while the same run's log showed the engine aiming a later vantage, with the display provably unlocked and on. An 8×8 nonce block plus an always-on-top fronted window fixed it (seeded: `attempts=3` passes, `attempts=6` refuses) — with the honest confound that machine load also fell 7.2 → 2.5 over the same window.

### 66 — Two parallel authors each correctly re-record the same baseline literal
**Class:** A recorded literal (a golden hash, a snapshot, an approved output) is governed by a rule of the form "re-record once, with a reason, against a base control". The rule is written for a SERIAL pipeline. Once several branches run in parallel and each is legitimately entitled to move that literal, each records a correct value against the same base — and the values are mutually exclusive, because each was captured on a tree missing the others' changes. Both authors obeyed the rule; whichever merges second is now comparing against a base that no longer exists, and the collision surfaces as a mysterious red at integration.
**Countermeasure:** the re-record is once per MERGE SET, not once per branch: branches report WHAT they will move and why, and the literal is captured once on the merged tree with a same-session capture of the last merged tree as its control, the per-branch reasons recorded together in the record's header. A branch that must measure locally does so against its own base and states that its literal is provisional.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D9 (the collision) / R8-D11(c) (the ruling), Librarian #R8-G03. Two lanes each re-recorded the classic reference pair once, both from the same base at `match=2/2`; one tree had an 8 px-taller HUD bar, the other a changed ground palette, and the merged tree re-recorded once against the first-merged lane's pair.

### 67 — A staging loop that spends its budget on refused actions and calls them done
**Class:** A test or capture fixture must reach a stated precondition ("five settlers", "three open orders") and drives it through an action that may legitimately be REFUSED by the system under test. The loop decrements its budget outside the success branch, so a refusal consumes the same budget a success would, and the compensating shortfall logic below it — which exists precisely to make the staging reach its number — finds nothing left to spend. The fixture then reports a world that does not meet its own precondition, and the resulting failure is attributed to whatever change happened to be in the tree.
**Countermeasure:** a staging loop counts the WORLD before and after and believes the world, instead of inferring success from having issued the action or from re-deriving the action's own acceptance clauses; and it prints its accounting unconditionally — wanted, succeeded, refused, achieved — so a shortfall reads as its cause. Seed it both ways: restore the miscounting and confirm the precondition goes red; force every action to be refused and confirm the accounting says so.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D15 / R8-D16, Librarian #R8-F01. A night frame's hire loop wanted six settlers, had two hires refused by an unrelated shipped rule, staged four against its own `settlers>=5`, and the packer refused the whole grade cycle; the defect was localised one variable at a time across four trees rather than bisected, and the briefed second cause (a new prop blocking a seat) was measured and refuted.

### 68 — A threshold derived from the baseline instead of from the seeded defect
**Class:** A new gate's limit is set by looking at where the system currently sits and leaving "some margin" — 1.4 against a believed 2.2, a budget 20 % above today's cost. Nobody measures where the DEFECT the gate exists to catch would land. If the baseline figure is itself stale or the defect is subtler than assumed, the margin swallows the defect entirely and the gate cannot go red for its own reason, while looking rigorous because it carries a number.
**Countermeasure:** a gate's threshold is fixed only after its seeded defect has been MEASURED, and the derivation — baseline, seeded value, chosen limit, and the headroom between limit and seed — goes in the gate's own header. If the seed passes, the threshold is tightened, never the seed weakened. Neighbour of class 48 (a tolerance derived from the constant it checks) and class 25 (a gate whose control survived).
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D4, Librarian #R8-A02 (recurrence of #R6-03). A night river/bank ratio gate was briefed at a ceiling of 1.40 derived from a stale baseline of 2.2; the true baseline is 0.661 and the brief's own seeded defect measures 1.121, so the gate had 112 % of headroom over the defect it was written for. Tightened to 0.90 on the measurement.

### 69 — A gate clause the defect state itself satisfies
**Class:** A check is written as a DIRECTIONAL claim about a symptom — "some of them arrive", "the count is above zero", "it is faster than before" — where the property that actually matters is an equality or a completeness invariant. The bug's own state satisfies the direction, so the gate is green on the very defect it was written for, on its first run, under its own seed. It is worse than no gate, because its green is now quoted as evidence.
**Countermeasure:** write the check as the INVARIANT (every one of N reaches the consumer; the two sets are equal; nothing is missing) and print both sides of it, then run the seed before trusting the pass — a gate that cannot be driven red by the defect it names is not finished. Neighbour of class 25; the distinguishing mark here is that the clause is satisfiable by the defect rather than by a surviving control.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D21(b), Librarian #R8-G06. A gate for "every night emitter reaches the shadow pass" first read `game > 0 while tree > 0`, printed PASS at `game=7 tree=17` — the bug exactly — and was rewritten to the invariant, which the same seed drives to `missing_sim_pos=10 FAIL`; shipped at `game=17 tree=17 missing_sim_pos=0`.

### 70 — Capped categories bound the reachable score, so incremental work cannot move it
**Class:** A weighted rubric, scorecard or SLA contains CAPS — rules of the form "if X is true, this category cannot exceed N" — alongside its weights. Work is planned as though the score were a weighted sum of improvable parts, so effort goes to whichever category looks furthest from target. But once several heavy categories are pinned at their caps by one or two structural properties, the reachable maximum is fixed and no amount of incremental work in the remaining categories can approach the target. Rounds of genuine improvement then produce deltas inside the instrument's noise, and the loop reads as "the work isn't landing" when it is landing somewhere that cannot pay.
**Countermeasure:** before planning a cycle, compute the score the rubric can REACH with every currently-breached cap still breached, and compare it with the target; if the reachable maximum is below target, the cycle's mandate is the CAPS and nothing else. Have the judges name which cap they applied and why, in their own words, and carry those quotes into the next brief — a cap is a structural statement about the artifact, not a score to be argued with.
**Origin:** Kingdom: Survival, round 8, 2026-09-18 — ledger R8-D22 / R8-D23, Librarian round-8 open items, GDD §12 row 141. Four blind cycles held an art grade at ~4 against a target of 8.5 while every per-category art delta sat inside the graders' agreement; both graders, independently and unprompted, applied a flat-island cap of 7.0 ("no hill, mountain, cliff or terraced grade change appears in any of the nine frames") and a repetition cap of 7.0 on six categories ("an identical, unrotated sprite is catchable by eye in all nine frames"). The next round's mandate was rewritten to target the caps first.

### 71 — A seeded stream's consumption is measured with a cursor, never inferred from a diff
**Class:** A procedural system draws every decision from ONE seeded generator in sequence. A change is judged "one extra draw" by reading the diff, and a fix is ruled on that count. But downstream branches decide whether later draws happen at all (a kind chooses whether a variant is rolled; a rejection loop runs a different number of tries), so the diff under-counts, and the "fix" drifts the stream further.
**Countermeasure:** before ruling on any change to a seeded stream, print the generator's cursor (draw count + state) at the end of each stage on the baseline and the candidate, and gate on equality; attribute a drift by same-session control one variable at a time; treat any content swap that changes geometry (footprints, nav radii) as an independent cause with its own control.
**Origin:** Kingdom: Survival, round 8, 2026-09-19 — ledger R8-D25 (the chair's ruling) refuted by R8-D26 / `tools/qa_r8_stream.gd`; Librarian R8-CH01, R8-H02, R8-H03; CLAUDE.md Mistakes Log 2026-09-19.

### 72 — An instrument's token grammar is part of its contract
**Class:** A scoring tool accepts identifiers matching a narrow pattern and silently normalises or renames anything else, so a verifier's cycle is filed under a name nobody asked for and later readers cannot find it.
**Countermeasure:** state the accepted grammar in the tool's header and refuse (non-zero, with the pattern printed) rather than rename; a verifier's cycle carries the verifier's name.
**Origin:** Kingdom: Survival, round 8, 2026-09-19 — V8's grade filed as `cycle=G3`; Librarian R8-CH03.

### 73 — A sandboxed liveness probe reads a denial as a death, and acts on it
**Class:** A lock, pool or supervisor reclaims a resource when its holder is "dead", and decides death with a liveness probe (`kill -0 <pid>`, a signal-0 send, a `/proc` read). Inside a sandbox, container or different user, the probe fails with a PERMISSION error for a process that is alive and outside the prober's view — and the code treats any failure as "no such process". Unlike a denied pre-flight that merely reads as all-clear (class 52), this misreading ACTS: it takes a live holder's slot, so two owners run where the lock promised one. Its test passes, because the tester's fake holder runs inside the same sandbox as the tester and is always visible.
**Countermeasure:** distinguish the errors — only "no such process" (ESRCH) means gone; "operation not permitted" (EPERM) is a denial and the holder is presumed alive. Prove the liveness test against a holder started OUTSIDE the tester's sandbox (or as another user), both ways, before the lock guards anything; apply the same rule to every holder the lock tracks, including its own queue.
**Origin:** Kingdom: Survival, round 9, 2026-09-23 — ledger R9-D23, Librarian #R9-H02. The chair's machine-wide engine lock reclaimed "dead" slots with `kill -0`; a sandboxed lane's base control read Lane X's live `test_phase2` holder as dead and took its slot (up to three engines where two were allowed); fixed in one line (`66b7e17`, ESRCH-only).

### 74 — A multi-clause verdict read by its first clause
**Class:** A long-running check prints one verdict line followed by several clauses (`also:` lines, a list of failing sub-conditions, a summary then details). A reader — often a coordinator reading many reports — takes the first failing clause as THE failure, writes "fails one clause", and schedules the next cycle against it. The other clauses stay live and unrecorded; each cycle fixes one thing while several are red, and the tally of what is wrong is wrong in every status line built from it.
**Countermeasure:** the ruling that follows a verdict quotes EVERY clause of EVERY run it cites, with a count ("6 clauses red: …"), never a paraphrase of the first; batch runners forward every child's trailing clauses and any output printed after a verdict, so nothing lives only in a child's log; a status line that says "one clause" names the other clauses as green.
**Origin:** Kingdom: Survival, round 9, 2026-09-21/22 — ledger R9-D9 / R9-D10 / R9-D11 each recorded `case=year` as failing ONE clause; R9-D12 found SIX, with five `also:` lines unread across fix cycles 2–4; Librarian #R9-CH01; batch forwarding `8840d1e`.

### 75 — Three clean runs are a rate, not an absence
**Class:** A hypothesis about an INTERMITTENT fault (a race, an occlusion, a flaky resource) is tested by running the scenario a few times; every run is clean, and the hypothesis is written up as refuted and the fix withheld (correctly citing "reproduce before fixing"). But a handful of clean runs of an intermittent fault only bounds its rate; the next run may reproduce it with the instrument armed. The mirror failure follows: a SEED that reproduced the fault one morning goes inert later, and the fix is left proven only by a single session's measurement.
**Countermeasure:** for an intermittent fault, arm the instrument that would name the cause and keep sampling past the first clean streak; report "not reproduced in N runs" with N, never "refuted". A fix for such a fault ships only with a seed that forces the mechanism on demand — re-prove the seed can still fail on the day the fix is verified, and state what the seed cannot reproduce.
**Origin:** Kingdom: Survival, round 9, 2026-09-21/23 — ledger R9-D3(b), R9-D6(c), R9-D25(a); Librarian #R9-H06. Stage 1a read three consecutive clean rendered captures as refuting window occlusion; the fourth reproduced it (`frames_drawn` frozen at 7 over 18 ticks, `land_px=146`). Stage 1d then found the minimise seed inert (0 `can_draw=0` ticks where the morning measured 20); the rig lane replaced it with minimise-then-restore (`can_draw=0` 53/53), proven both ways. Neighbour of classes 47 and 51.

### 76 — Polishing art on an unproven layout
**Class:** A project grades and polishes its art — lighting, texture, sprite variety, the look of terrain features — round after round on a map LAYOUT that has never itself been proven to play: where the clearings, barriers and chokepoints are, whether they read, whether they give the intended choices. When the layout is finally judged and redesigned, most of the art spend was on placements that no longer exist, and the grade's caps (a flat map, repeated props) were layout problems wearing art symptoms.
**Countermeasure:** layout before art, as a gated sequence: block the map out with flat placeholder shapes (class-coloured discs and bands), prove it with the map checks on every preset and the seed sweep, have the owner LOOK at the whitebox, and only then generate barrier and landmark art — no barrier sprite lands before the checks are green. Name the cut list up front so a squeeze cuts art variety, never the gameplay spine.
**Origin:** Kingdom: Survival, round 9 close / round 9.5, 2026-09-23 — owner Q177–Q181 (the map redesign; round 9 closed short with no grading), `docs/design/level-design.md` principle 7 and §8 rule 1, from the level-design review of the Ensemble Studios interview (Ian Fischer; Byrne, *Game Level Design*, pp. 190–192, whitebox pp. 232–234); Librarian #R9-CH07. Nine rounds graded art on a layout round 10 replaces. Neighbour of class 70 (the caps were structural).

### 77 — A merged lane's regression hides until the whole tree is measured
**Class:** Parallel branches each report green on their own gates, and each measures shared, load-sensitive quantities (boot time, frame time, a global visual metric) under the other branches' concurrent load, so those numbers are declared "not evidence" or not reported at all. The coordinator accepts the branch reports as final. After the merge, the whole tree is several seconds over a budget or measurably worse on a global metric, and the cost belongs mostly to ONE branch — which no report could have shown, because no report measured the merged tree or its own tip under quiet conditions.
**Countermeasure:** before accepting branch reports as final, measure the MERGED tree on every shared budget and global metric under exclusive conditions; when it moves, isolate by measuring each branch tip and each intermediate merge in the SAME session with the same probe, and attribute the cost by name. A branch report that could not measure a shared budget says so explicitly, and the coordinator carries that as an open measurement, not as a pass.
**Origin:** Kingdom: Survival, round 9, 2026-09-23 — ledger R9-D32(1)–(2), Librarian #R9-C01 / #R9-C02. Five lanes merged green; the close worker found classic boot at ~17.6 s against a 12.95 s budget (≈ +3.0 s from one lane's tip, 16 628 / 16 990 ms, ≈ +0.9 s from another) and the massif shadow 0.9 L\* worse, the same lane's; the lanes' own boot numbers had been taken under each other's load. Neighbour of classes 23 and 66.

### 78 — A rulebook recipe that says "fill everything between" draws the opposite of the reference
**Class:** A design document gives a generator a procedural recipe ("place the rooms, then fill everything between them with barriers so the space is full"). The recipe was written from principles, and the reference images were collected separately. The generator follows the recipe exactly and passes every guarantee written from the same document. Its first output is the inverse of what the references show (a dense forest with small clearings where the references show large open ground with discrete obstacles). Lanes are briefed to build on that output before anyone compares it with the references.
**Countermeasure:** the first generated output of a new recipe is drawn (a top-down class map is enough) and put BESIDE the reference images before any lane builds on it. Measure one number that separates the two readings (here, open ground as a share of dry land) on both the output and the references. Hold any expensive dependent work, such as restaging tests, until someone who has seen the references accepts the look. A recipe verb like "fill" names a quantity; write the target share down.
**Origin:** Kingdom: Survival, round 10, 2026-09-24 — ledger R10-D6, Librarian #R10-L01. Lane G's layout A came out ~40 % open ground against the They Are Billions references' large open areas. An open variant B (≈ 60 %) was built behind a switch, the owner chose it (Q201), and the 49-case restage waited for the choice. Neighbour of class 76 (layout before art: this is the same discipline applied to the layout itself).

### 79 — A self-sweep that excludes the authored or pinned inputs certifies nothing about them
**Class:** A generator or pipeline is certified by its own lane's sweep over "N random seeds, N/N pass". The inputs the product actually ships (a hand-authored level, a pinned default seed, the preset every player boots) are outside that sweep. Often they are also exempt from the runtime check that would catch them, because they are "known good" or "authored". The sweep is green, and the two inputs that matter are broken.
**Countermeasure:** every certifying sweep enumerates the shipped inputs FIRST (authored, pinned and default seeds), then the random range, and prints them by name. A runtime validation is never skipped for an input because it is authored. If the skip exists for boot time, the same check runs in the test suite as a named case. A lane report that quotes "N/N" states which inputs are in N.
**Origin:** Kingdom: Survival, round 10, 2026-09-24 — ledger R10-D8, Librarian #R10-L02, reconcile report `f8d6e72`. Lane G's guarantees read 20/20 on seeds 1–20. Seed 0 and classic, the two islands the game boots, had their landing cut off from 18–20 clearings by a gorge-sealed ford, and `validate_baked`'s reachability check was skipped for exactly those two (`game.gd:2808`). Fixed by `test_procgen case=authored` and validation on the authored islands (lane G2). Neighbour of classes 32 and 37.

### 80 — An independent checker is what catches a builder's green; keep them separate, then make them share one function
**Class:** A builder writes the thing and the checks that certify it, in one lane, from one reading of the rules. Its checks and its code share every misreading (here, a walk model with no slope rule), so its green is circular. A second lane that writes its own probes from the design document, without reading the builder's code, measures the result independently and goes red. The contradiction looks like noise ("probe bugs") until someone diagnoses it line by line.
**Countermeasure:** the builder and the checker are separate lanes with separate authors, and the checker writes from the design document, not from the builder's code. When they disagree, a diagnosis-only worker (no edits) rules each failing line as builder, checker or contract before anyone fixes anything. Once a rule's reading is settled, BOTH sides call ONE shared function (one walk rule, one census) with a disagreement count gated at 0. That closes the class and keeps the independence of the acceptance check.
**Origin:** Kingdom: Survival, round 10, 2026-09-24/26 — ledger R10-D7, R10-D8, R10-D11, R10-D17, R10-D21; Librarian #R10-L02, #R10-L03. Lane P's seven LD probes, written against a synthetic fixture, failed 27 lines on islands lane G certified green. The reconcile worker ruled 23 of them generator, 4 contract and 0 probe (as main cause). The fixes converged on shared functions: `WorldDef.walk_terrain_ok` (`gen_terrain_disagree=0`), `border_census`, `ld19_exposure` and `dead_connectors`. Neighbour of classes 22 and 77.

### 81 — A ruling that changes a verdict is not done until the instrument prints it
**Class:** A coordinator rules that a failing check line is "report-only", "deferred" or "the other team's half". The ruling is written in the decision log. Nobody changes the probe, so it keeps printing FAIL and exiting non-zero. Everyone inside the loop knows to read those lines as "known reds". A blind verifier, correctly ignoring the log, reads them as gates and fails the round. Meanwhile "known red" has become a habit that can hide a real regression on the same line.
**Countermeasure:** the brief that carries a verdict-changing ruling names the file and the line that will print it, and the ruling is closed only when that line prints the new label (`REPORTED`, `n/a (deferred: <where>)`). The demotion is seeded so that a real gate in the same probe still fails. A "known reds" list is never used in place of a probe change. A verifier's first run on the tree is the test of whether the rulings landed.
**Origin:** Kingdom: Survival, round 10, 2026-09-26 — ledger R10-D18, Librarian #R10-CH01 and #R10-FIX2-01. R10-D8, R10-D11 and R10-D17 ruled LD-22's twins, LD-23 and LD-1's steep banks report-only or art-side. `qa_ld_choice` and `qa_ld_readability` still exited 1 on all three islands, and V10a (blind) failed the round on them. Fix cycle 2 put the rulings into the probes (`6a2b85d`, `35b6f4b`), and cycle 2 of V10a passed.

### 82 — A premise ruled from one isolation drives work before its effect size is measured
**Class:** A red clause and a real defect sit next to each other (a building finds no seat; the clause is about that building's output). An isolation confirms the defect is real, and the coordinator rules the defect as the clause's cause, then spends a fix cycle on it. Nobody computed the most that fixing the defect could move the failing number. When it is fixed, the number moves by a fraction of the gap, and the clause turns out to fail on a different term. The same shape repeats when "reorder the script" or "move those buildings" is ruled as the fix for a capacity gate without testing whether those buildings hold the seat.
**Countermeasure:** before a cause drives work, write down the most it can move the failing number (arithmetic off the script table, or a removal test on the probe's own lattice), and compare that with the gap. A cause that cannot close the gap is recorded as a real defect, not as the explanation. Name the term the clause actually fails on (read both sides of a comparison). Look for the lever that binds; a pre-authorised lever is preferred to a structural hunt.
**Origin:** Kingdom: Survival, round 10, 2026-09-25/26 — ledger R10-D14(1) → R10-D16, R10-D20(2) → R10-D21 → R10-D22; Librarian #R10-CH02, #R10-PREP-02, #R10-FIX4-05, #R10-FIX5-01. The farm-room premise could add about 5 crops against a 27 g gap, and the clause flipped on meat; it closed on the owner's pre-authorised spawn-interval lever. Two rulings later, removal tests showed that neither the script reorder nor moving the Lodge and Tower freed the tier-2 seat; the measured radius (320 u) did. Neighbour of classes 22 and 54.

### 83 — A worker cut off by an account limit is resumable in place, if every worker commits as it goes
**Class:** Long-running workers are stopped mid-task by something outside the loop: an API rate or usage limit, a context compaction, a crash. If a worker holds its progress only in its working tree or its context, the coordinator must choose between re-spawning from scratch (repeating hours of work) and guessing what state the tree is in. A coordinator that simply retries can loop against the limit.
**Countermeasure:** every worker commits at each coherent step (WIP commits are fine), and never leaves an engine or watcher running across a turn boundary. On a stop, the coordinator records each worker's last commit and checks that no process holds a shared resource (the engine lock). It resumes each worker IN PLACE, with its own context (a message to the same agent), rather than re-spawning. If the limit trips again, it stops spawning and tells the owner; it never retries in a loop.
**Origin:** Kingdom: Survival, round 10, 2026-09-24/25 — ledger R10-D13, Librarian #R10-H01. The account's weekly API limit (HTTP 429) cut off lanes T and G5 for about 14 h. Both had committed as they went (`07a48dd`, `6418fa8`), the lock was empty, and both resumed via SendMessage and merged (`8596af2`, `3459823`). Neighbour of classes 21 and 40.

### 84 — A seeded defect survives when the guarded code path never runs on the fixture
**Class:** A fix adds a guard around a path that only fires in a minority case (a retry after a blocked first attempt, a side-picker when the first candidate is closed). The probe runs on a fixture where the first attempt always succeeds, so the path is never executed. The mutation that inverts the guard leaves the probe green, and the seed that "proved the probe can fail" was a seed of some other line.
**Countermeasure:** for every guard a fix adds, name the input that makes it fire and stage that input in a case (a blocked first seat, a cell whose neighbours cancel). Seed the guard's own inversion, and count a seed only when it turns that case red. A verifier's survivor list is a work list: unguarded code is recorded as unguarded, not as covered by the nearest green line.
**Origin:** Kingdom: Survival, round 10b, 2026-10-01 — Librarian #R10b-V01, #R10b-V02 (V10b survivors (b), (c); `logger_camp.gd:280` and `_open_side` both stayed `LD-25 PASS`; `grep` of `tools/` for either name returned nothing). Neighbour of #69 and #79.

### 85 — A probe that decodes a signed field's magnitude cannot see its sign
**Class:** A baked field stores a signed value (a distance to the nearest stamp, a side of a line) and a later pass tidies the result (a seam pass that zeroes opposite-sign neighbours). The probe counts taps whose magnitude is wrong. A field with the wrong SIGN has the right magnitude and is then hidden by the tidy-up, so the probe reads clean while the data is inverted.
**Countermeasure:** the probe decodes the sign against the nearest source (or counts cells whose sign disagrees with the nearest stamp) and is seeded with the sign inversion, not only with a magnitude change. Any tidy-up pass that can hide a defect is bypassed or counted by the probe so a mutation cannot disappear into it.
**Origin:** Kingdom: Survival, round 10b, 2026-10-01 — Librarian #R10b-V03. `scripts/tracks.gd:368`: the midpoint mutation read `ghost_taps=40789 FAIL`; the sign inversion read `ghost_taps=0 PASS` (`drawn_cells` 32273 to 32181). Neighbour of #69.

### 86 — A probe's default configuration differs from the system's, and a red relayed without its command carries the mismatch
**Class:** A harness helper builds its context from a default (here the classic island) while the thing it measures boots from a different default (the gameplay island). A run that omits the argument measures one configuration against another's tables and prints a confident red under one label. A coordinator relays the red without the command line that produced it; two workers then bisect and classify a defect that does not exist, and a finish line is held.
**Countermeasure:** a booting probe takes the configuration explicitly and refuses without it, or asserts after boot that the booted configuration equals its context's; every relayed result quotes its exact command line, and a coordinator reproduces a finding with the command written down before it enters a brief or holds a gate.
**Origin:** Kingdom: Survival, round 10b, 2026-09-30 — ledger R10b-D22 (the claim) and R10b-D23 (the correction), Librarian #R10b-CX-11 (the harness) and #R10b-CH01 (the chair's relay). Cost: two Sonnet workers (95 k + 109 k tokens) and a held C-4. Neighbour of #22 and #54.

### 87 — Frame hashes cannot be compared across captures of a live scene
**Class:** A verifier is told to compare a graded pack's file hashes with the previous cycle's manifest. The scene is not still (sway, water time, walkers), so two captures on the SAME code differ in most pixels (60.5 % here, mean |delta| 5.1), and a cross-cycle difference of the same size is indistinguishable from noise. An equality check would never pass; an inequality proves nothing.
**Countermeasure:** use a deterministic pixel instrument for "did the picture change" (a pinned-vantage comparison against a recorded reference that reads `self:0/ref:0`) and measure the same-session repeat-capture noise floor before reading any frame difference. Grading packs that re-encode do not preserve hashes either, so pack integrity is checked against the key, not the previous pack.
**Origin:** Kingdom: Survival, round 10b, 2026-10-01 — Librarian #R10b-V06, ledger R10b-D19 and R10b-D28. 10 of 10 pack hashes differed from G3's manifest; two captures of one frame on one tree differed in 60.5 % of pixels. Neighbour of #59 and #65.

### 88 — A work cycle sized below the instrument's resolution cannot be verified
**Class:** An instrument can resolve a change only above a stated reading rule (here 0.51 points, from two repeat reads of identical frames). Successive content cycles each move the score by a fraction of that, so every step reads "no measurable change", while the findings the graders name stay the same in kind. Three cycles of effort are spent and none can be shown to have worked.
**Countermeasure:** before a cycle, state its expected move and compare it with the instrument's resolution; a cycle expected to move less than the rule is aimed at one named content gap that all graders cite, one cause per round, and its result is read as part of the series (the trend across cycles with the controls holding), never as a single step. If the score is held by caps, price the cap lift, not the increment.
**Origin:** Kingdom: Survival, round 10b, 2026-09-28 to 10-01 — Librarian #R10b-CH04, ledger R10b-D12, D17, D20 and D28: G1 4.95/5.08, G2 5.08/5.10, G3 5.43/5.35, V10 5.19/5.48, every step inside 0.51. Neighbour of #61 and #70.

### 89 — A margin gate tipped by an unrelated correctness fix, and a margin relayed rounded
**Class:** A gate passes by a hair (a reading of -12.1 against a limit of -12). An unrelated correctness fix to another input of the same shader moves the reading by 0.02 to 0.04 and the gate goes red. The report that restored it quoted a rounded figure that overstated the margin, so the next reader believed it was safe.
**Countermeasure:** record the UNROUNDED reading and the smallest step of the tuning constant that flips the gate; re-run every gate that shares an input after any change to that input; restore a margin by the smallest half-step of the constant, with the instrument's own literal never loosened; attribute the move by hunk-revert isolation (revert one hunk, re-measure, on the same session) before choosing what to move.
**Origin:** Kingdom: Survival, round 10b, 2026-10-01 — ledger R10b-D25 to D27, Librarian #R10b-V07. `b84a6b5`'s tracks hunk moved blob116 from -12.12/-12.14 to -11.96/-11.98; `UNION_SHADOW_STRENGTH` 0.96 to 0.97 restored -12.15/-12.19; V10b read -12.1 on both captures, about 0.1 dL. Neighbour of #48 and #68.

### 90 — A gate that is off for a class of inputs prints like one that passed
**Class:** A liveness or content floor is applied only above a threshold that one whole class of inputs (dark night frames) falls under. Those inputs print the gate line with the gate switched off (`gate=0`), which reads like a pass to anyone scanning for the line, while no content floor protects them.
**Countermeasure:** the verdict says which proof stands in the gate's place (a refusal-backed freshness token, a counterfactual that differs from the beauty frame) and cites it per frame; a verifier checks that the substitute proof is present for every input the gate skips. A floor that cannot apply to a class is replaced by one that can, or the class is named as covered only by the substitute.
**Origin:** Kingdom: Survival, round 10b, 2026-10-01 — Librarian #R10b-V05. All five night `LDLOOK` frames print `FB_LIVE gate=0`; their liveness rests on `FB_TOKEN present=1 cleared=1 fresh=1` and `LDLOOK_LIVE PASS`. Neighbour of #65.

### 91 — A probe's own child processes escape the wrapper's output cap
**Class:** A wrapper caps the output of the process it launches. A probe that launches children of its own (a repeat harness, a sweep) captures each child's output in memory through a second stream the wrapper never sees, so a runaway child (a recursion backtrace) can fill memory while the wrapper's log stays small.
**Countermeasure:** the probe caps each child's stdout and stderr itself (a poll loop that stops at a byte limit, kills the child and counts the run not-ok); a self-test feeds a child that emits more than a tiny cap (`yes` against 64 KB) and asserts the kill; the child's real exit code is read from the process API, never from a shell wrapper's `$?`.
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-CX-01, #R10.5-FIX1-01/02. Child of #34.

### 92 — An exception predicate wider than the exception it was approved for
**Class:** An owner or chair approves "a known, named failure is tolerated"; the code tolerates a family (any failure whose text starts with the same prefix), so a crash after the named failure, or a different failure of the same subsystem, counts as success.
**Countermeasure:** write the predicate as the conjunction of every clause of the approved sentence (exit code, exactly one failure, that failure's exact text, every other verdict PASS); give it a table-driven self-test with one case per clause, and mutate each clause off in turn to prove its case goes wrong; log the ruling with the predicate beside it.
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-CX-02, ledger R10.5-D3/D5, Q235. Neighbour of #81.

### 93 — "All runs agree" over empty values
**Class:** An aggregator checks that N children produced one distinct value (digest, hash). A missing field defaults to an empty string for every child, so the set has one element and agreement is reported over nothing; the field's own verdict line is never read.
**Countermeasure:** require each field to be PRESENT and non-empty, and its verdict line to exist and end PASS, before it participates in an agreement check; self-test cases for "field missing", "verdict FAIL" and "all empty".
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-CX-03. Neighbour of #65.

### 94 — Two code paths that must produce one image decode it differently
**Class:** A primary path (a converter writing a binary cache) and a fallback path (loading the source when the cache is missing) each carry their own decode; import settings (an alpha-border fix) make the pixels differ, so a sprite's look changes when the cache is deleted or regenerated, and the fallback may be null for assets the editor never imported.
**Countermeasure:** one shared decode function used by both paths; a probe forces the fallback for every asset and compares to the frozen manifest (`fallback=1`), with the converter re-run proven byte-identical.
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-CX-04.

### 95 — A baseline recorder that enumerates the frozen reference, with "raw" fields taken after the mutation
**Class:** (a) The tool that re-records a baseline lists the old baseline's inputs, so a changed input keeps the old reference and a new input is missing, and the deliberate re-record workflow cannot resolve either. (b) A manifest field labelled "raw" is read after the preparation function edited the object in place (a getter that returns the live image), so the evidence of the untouched reference is the prepared data under another name.
**Countermeasure:** the recorder enumerates the source of truth that changes and is proven by recording a changed and a new input in a scratch directory; raw fields are read from a copy before preparation, and the check fails when a raw field equals its prepared twin.
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-CX-05, #R10.5-CX-07. Neighbour of #87.

### 96 — A digest or ledger that passes without covering what it claims
**Class:** (a) A digest that claims invariance of a drawn result enumerates fields by hand and misses one the game draws (rotation), so a change to it passes; a field added later may be time-dependent. (b) A completeness ledger (every load, every stage) passes on "non-empty", so a regression that logs one row reads PASS.
**Countermeasure:** (a) a tooth per field that must move the digest, a seeded change to each drawn field, and two children at different times before a field is recorded; (b) the expected set is computed structurally and independently of the ledger, and every member must have a row (`n=1 instantiated=125 missing=124 FAIL`).
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-CX-06, #R10.5-CX-08, #R10.5-FIX1-03. Neighbour of #84.

### 97 — An instrument that observes through the audited code's own label cannot see a bypass
**Class:** A probe proves "nothing reads the old format" by reading a log that the loader writes about itself. A direct load elsewhere never touches the log, so the property is true only by accident and every seed that bypasses the loader stays green.
**Countermeasure:** a poison test: replace the old files with unparseable stubs in a worktree and run the full path (boot, frames, the parity probe); keep a control that reverts the loader to read the old format first and must be refused on the same stubs, so the stubs are proven visible; delete the old files when the round that no longer needs them lands.
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-V01 (V10.5 limitation L1). Neighbour of #84 and #85.

### 98 — A percentage gate loses its resolution when the total shrinks
**Class:** "Unaccounted time under 2 % of the total" was calibrated when the total was large. An optimisation that cut the total by a third moved the blind threshold to about 560 ms, so an untimed stage below it passes while the gate looks unchanged.
**Countermeasure:** keep a second, resolution-free guard (a typed list of required stage names, each of which must have a timer) beside any percentage gate, and re-derive the gate's blind threshold in absolute units whenever the total moves; the verifier seeds one stage under the threshold and checks the second guard catches it.
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-V02 (V10.5 limitation L2; seeds 6a and 6b).

### 99 — A near-zero timer explained by a plausible mechanism and never counterfactually tested
**Class:** A phase timer read about 0 ms and two builder reports explained it ("the old format already carried its mip chain"); both were false, and the timer was near zero because it bracketed only the call after the work had been done. The claim then propagated into a parity argument.
**Countermeasure:** when a measured cost reads about zero, run the counterfactual (does the timed operation happen at all, in this path?) before writing a reason down; a reason that rests on a property of the data is checked on the data (the file's declared flags), not inferred from the timer.
**Origin:** Kingdom: Survival, round 10.5, 2026-10-01 — Librarian #R10.5-V03 (V10.5 report error R1). Neighbour of the 2026-09-09 Mistakes Log entries on unreproduced premises.

### 100 — A CLI launched from a background command with open stdin waits for input forever
**Class:** A tool that reads its prompt from stdin when none is given (Codex `exec`) is started from a compound background command; stdin stays open, the tool waits, its log stops at a one-line "reading input" notice, and the chair reports "still running" without looking. Earlier runs worked only because they happened to get EOF.
**Countermeasure:** every such launch ends `< /dev/null`; the launcher checks that the log grows within seconds and again at the first status report; a 39-byte log is a hang.
**Origin:** Kingdom: Survival, round 10.5b, 2026-10-01 — Librarian #R10.5b-01 (9 h 9 min of wall clock).

### 101 — A CHECK in a brief that passes with the guarded code removed
**Class:** A brief's seed CHECK is written from the design and passes through a path the mutation does not touch (a refused context that falls to a fixture and exits in 1 s with the halt deleted), or a range gate counts an untouched default value as data (128 read as "stamped": a correct encoder read thousands of bad cells).
**Countermeasure:** run each brief CHECK against its own seed before the brief is accepted (builders do, and replace it by the discriminating form, e.g. "the refusal line is the only output"); exclude the untouched default from "present" and add a coverage gate (`checked > 0`).
**Origin:** Kingdom: Survival, round 10.5b, 2026-10-01 — Librarian #R10.5b-03. Neighbour of #84 and #90.

### 102 — An error sentinel that is also a legal value
**Class:** One string holds both "which value was rejected" and "was anything rejected"; the rejected value is the empty string, which means "no error", so the refusal is skipped for exactly the input that most needs it.
**Countermeasure:** store the rejected value in a non-empty form (`<empty>`) or keep a separate boolean; a test passes the empty and whitespace-only values.
**Origin:** Kingdom: Survival, round 10.5b, 2026-10-01 — Librarian #R10.5b-04 (found by Codex).

### 103 — A family-wide fix proved on the named members, with an assert-after-boot standing in for a refusal-before-boot
**Class:** A harness fix is applied to the probes the brief lists and proved on two; one member of the family was classed "already asserting after boot", so a missing argument ran a full wrong-island boot before failing. Separately, a label fixed by one line (`set_meta`) with no post-boot check in nine probes turns green again on the wrong island if that line is bypassed or goes stale.
**Countermeasure:** fix at the shared layer; the verifier inventories EVERY member of the family and runs each with no argument, reading what it booted; refuse before the expensive step, and keep a cheap post-boot assert as the second layer.
**Origin:** Kingdom: Survival, round 10.5b, 2026-10-01 — Librarian #R10.5b-05, -06, -07. Neighbour of #86 and #97.

### 104 — A "report-only" exception that is the default, or that tests the kind of thing it excuses rather than its measured property
**Class:** A gate ruled "report-only for an atomic unit measured over the limit" ships as report-only for EVERY frame (cycle 1), then as report-only for any frame that ran a unit of the slow KIND, whatever the unit's own time (cycle 2): a stall in unrelated code on the same frame passes. Each refusal was the probe excusing more than its ruling, not a game defect.
**Countermeasure:** the shipped default is the strict form; the excuse is a predicate over the excused thing's own measurement (`gap - unit_ms <= slack`), fails closed when the measurement is missing, and names what it excused; the verifier seeds a stall one step outside the excused thing (an unrelated file, the same frame) and a stall on every frame, and the builder's self-test carries timed cases.
**Origin:** Kingdom: Survival, round 10.5f, 2026-10-02 — Librarian #R10.5f-01, -02 (V10.5f refused twice). Parent: #R10.5-CX-02.

### 105 — A stage-total timer standing in for a per-unit timer; a one-unit rule that sits a millisecond from firing
**Class:** The excuse's "unit time" is a stage-key delta, so a stall bracketed under the same key is booked as the unit; and the rule "exactly one unit" is narrower than "an atomic unit" with a clean-tree margin of 1.6 ms (a legitimate small-unit join fires it at a 27 ms budget).
**Countermeasure:** time the unit with its own timer around the unit alone; for a narrowed rule, measure the clean tree's margin against it before shipping and record it, or widen the rule to its ruling.
**Origin:** Kingdom: Survival, round 10.5f, 2026-10-02 — Librarian #R10.5f-03, -04 (V10.5f cycle 3 limits).

### 106 — An input freeze built from memory, and a freeze probe whose baseline was taken after a reset
**Class:** A boot freeze guards the inputs the builder recalled (selection was missed, `inputs_seen=2`); the probe that checks it re-takes its baseline at a phase start, so deleting the early freeze still passes.
**Countermeasure:** enumerate input handlers rather than recall them; hold a key from the first frame and count handler hits; take the baseline from the first booting frame and track movement per phase segment; delete each freeze line as a seed and watch the probe go red.
**Origin:** Kingdom: Survival, round 10.5f, 2026-10-02 — Librarian #R10.5f-05, -06 (W3, then Codex).

### 107 — A watchdog that outlives its job
**Class:** A monitor armed for a long job keeps running after the job reports and raises a stall alarm on finished work.
**Countermeasure:** stop the watchdog when its job reports; check the report before acting on an alarm. Neighbour of #43–#53's re-wake class.
**Origin:** Kingdom: Survival, round 10.5f, 2026-10-02 — Librarian #R10.5f-07.

### 108 — A cache key built from descriptions of the inputs, not from the inputs the work reads
**Class:** The key hashes a lossy or upstream fingerprint (a quantised spec hash, a stored graph hash, a file's size, a fresh read of the source file) while the work reads other things (live copies of the tables, raw array values, the code that actually loaded). A mutation of what the work reads leaves the key unmoved, and the cache returns another world's result.
**Countermeasure:** trace the work's call graph and list every table, array and static it reads; hash those bytes at the moment the work starts; hash the code that LOADED (static init), not the file now on disk; key an array by values, never `size()`; one key tooth per input class, each moved alone and each dropped from the key to prove exactly one goes red; and compare hit against a live run on every output field.
**Origin:** Kingdom: Survival, round 10.5c, 2026-10-02 — Librarian #R10.5c-01, -03, -04 (Codex plan #2-#4, round #1, #2).

### 109 — A cache hit hooked at an entry the real caller does not use
**Class:** The early return for a hit is put in the function the brief names (`bake_begin`); the real caller enters through another function (`bake_step`) that tests readiness once, calls the first, and carries on into the work. The hit loads, then the solver runs over it. Tests that call the first function directly pass.
**Countermeasure:** read every caller of the work before hooking; put the short-circuit where each caller returns; report a work counter (`rows=0` on a hit, `2596` live) and assert it, because equal output proves nothing about whether the work ran.
**Origin:** Kingdom: Survival, round 10.5c, 2026-10-02 — Librarian #R10.5c-02 (Codex plan #1).

### 110 — A reader that allocates before it bounds, and a gate that trusts the record it judges
**Class:** A file reader calls `get_buffer(length)` before comparing the length to the expected size, so a padded file is read in full before it is refused. Alongside: a "generated seeds never write" gate reads the cache's own `pinned` flag, so a regression that mis-classifies the seed also fools the gate.
**Countermeasure:** check size against the expected length first and report `read_bytes=0` on refusal; a gate takes its classification from its own arguments (preset, seed), never from the system it checks, and a forced misclassification is its seed.
**Origin:** Kingdom: Survival, round 10.5c, 2026-10-02 — Librarian #R10.5c-05, -06 (Codex round #3, #4).

### 111 — A writing probe whose isolation check records a failure and keeps going
**Class:** The probe notes that its sandbox directory override failed and runs the next cases anyway, which write and prune the user's real production data. A probe killed mid-case also leaves its temp directory behind.
**Countermeasure:** a failed isolation precondition stops the probe before any write; the probe sweeps dead-pid directories at start (`kill -0`, not-permitted counts as alive); seed the failure (override ignored) and watch the production directory stay unchanged.
**Origin:** Kingdom: Survival, round 10.5c, 2026-10-02 — Librarian #R10.5c-07 (Codex round #5, #6).

### 112 — A begin/end key check that cannot see a change made and undone in between
**Class:** A cache writer re-computes its key at completion and compares with the key at start. An input changed after the start and restored before the end passes, so a result computed under the changed input is stored under the clean key and then served as a hit forever.
**Countermeasure:** write only when nothing else ran between the work's frames, or re-key at every step, or re-verify a sample of rows at write; keep the torn case (change an input for rows A..B, restore it) as a standing tripwire probe and re-run it whenever a round adds work that can touch an input mid-way. Not reachable today means filed, not fixed.
**Origin:** Kingdom: Survival, round 10.5c, 2026-10-02 — Librarian #R10.5c-08 (V10.5c L1).

### 113 — Liveness inferred from a silent signal, and a cause reported before it is confirmed
**Class:** A sub-agent is called stalled because its transcript did not grow for 20 minutes, and a file's old mtime is read as proof its command never ran; the cause (a pending permission prompt) is then told to the owner as fact. A tool call in flight produces no transcript; the run was working.
**Countermeasure:** treat transcript size as no liveness signal during a tool call (the harness caps one at 600 s); check the process tree, the lock, the output location the command actually writes, and the agent's own report; tell the owner only what is confirmed, naming unknowns as unknown; correct in the ledger the moment it is wrong. Neighbours: #43-#53 (re-wake), #107.
**Origin:** Kingdom: Survival, round 10.5c, 2026-10-02 — Librarian #R10.5c-10 (R10.5c-D6, D7).

### 114 - Probe targets that steer the look
**Class:** A builder is given a numeric target from a probe for a visual quantity (saturation, rim chroma, glow share, ground gain). The probe goes green and the picture gets worse, because the quantity is a proxy the real judges (blind graders, the owner) do not reward. Needing to lower the gates to stay legible was the early warning.
**Countermeasure:** look numbers are guards that reject the known-bad, never goals; the brief states the look target in the judges' own words; the chair looks at the 1x and 3x crops against the last graded pack before every grading cycle (a standing gate); a cheap one-grader pre-read is a candidate; on a failed round revert every look change that has no positive judge sentence and keep the non-visual fixes.
**Origin:** Kingdom: Survival, round 11, 2026-10-02/03 - Librarian #R11b-01 (night 5.48 -> 4.81 against green probes; 11b restored V10's pixels).

### 115 - A grader's rubric that carries the score history
**Class:** A document the graders read in full gained a section with previous grades ("V10 5.19 / 5.48") because an as-built record and the rubric lived in one file. The graders are no longer blind to the baseline.
**Countermeasure:** a graded input holds rules only; grade from a throw-away worktree with the rubric replaced by the graded commit's bytes; a checker proves md5, line count, absence of score text, a single changed file and the pinned prompt head, with the contaminated file as its known-bad control; then move the record out to its own file.
**Origin:** Kingdom: Survival, round 11, 2026-10-02 - Librarian #R11-01 (Codex plan review; `tools/frozen_rubric.py`).

### 116 - An expected-gain estimate that left a surviving cap out
**Class:** A brief's predicted score gain multiplies each category's lift and forgets a cap or clamp that survives it, so a half-success was written as a clear win (+0.47 against a 0.51 resolution).
**Countermeasure:** recompute with every cap applied; pre-register the full-success and half-success values and what each reads as ("no measurable change", not a near miss); a result outside even the half-success is a failed round, not a near miss.
**Origin:** Kingdom: Survival, round 11, 2026-10-02 - Librarian #R11-02 (R11-D1 -> R11-D2).

### 117 - A coverage gate that accepts a missing measurement
**Class:** A receipt or coverage line passes when a measurement is absent, indistinguishable from a target that is merely not gated; a grab that silently fails leaves the suite green.
**Countermeasure:** missing is a FAIL on its own line, separate from the target's verdict; the required set is enumerated and printed (`required=11 ... missing=[]`); seed the grab away and watch it go red. Neighbour of #62, #41.
**Origin:** Kingdom: Survival, round 11b, 2026-10-03 - Librarian #R11b-04 (Codex round #1), #R11b-03, #R11b-11.

### 118 - A revert left unguarded when its metric is deleted
**Class:** A tuned constant is reverted and the probe that steered it is deleted (rightly, #114), leaving nothing that notices the constant moving again; the verifier's seed survives.
**Countermeasure:** before deleting the metric, keep a minimal tripwire on the reverted quantity (a floor against the graded pack, not a target) and run the seed that restores the bad value; record the gap as open if it is not built.
**Origin:** Kingdom: Survival, round 11b, 2026-10-03 - Librarian #R11b-09 (V11b seed S3).

### 119 - One exclusion list feeding two consumers
**Class:** A selection excludes an element (a building's own emitter) so one consumer (the shadow's casting source) is right; a second consumer (contact grounding) reads the same selection and is starved of the element it needs.
**Countermeasure:** give each consumer its own selection and name the difference in code; a probe per consumer (`OWN_GROUNDING` 0.860 -> 1.000; `LIGHT_CLASSES owner_is_building=1`).
**Origin:** Kingdom: Survival, round 11b, 2026-10-03 - Librarian #R11b-07 (Codex round #4).

### 120 - Sending a round to grading after the defect was already visible
**Class:** The coordinator looks at before/after crops, names a defect the graders have named before, and the round proceeds to an expensive blind grading cycle anyway; the grade then reports the defect as a finding.
**Countermeasure:** a visible, named defect in the crops stops the round (fix or re-brief) before grading; the crop look is a gate with a recorded verdict, not a progress check. Neighbour of #114.
**Origin:** Kingdom: Survival, round 11, 2026-10-02/03 - Librarian #R11-03 (R11-D4, R11-D7).

### 121 - A brief that names the dominant writer from reading code
**Class:** A brief attributes a visual defect to one writer (the hearth tint lerp) by reading the code; the one-variable controls show another writer (the pool warm term) dominates and the named one is second.
**Countermeasure:** step 0 before any fix: kill each writer alone, then all off (an all-off column means an unlisted writer: STOP); the fix is the smallest change to the convicted writer. Neighbour of #R11b-02.
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-01.

### 122 - A kill that does not reach the pixels
**Class:** A control that "turns a writer off" is a no-op because a per-frame update rewrites the property (`_process` rewrote `modulate.a`), so the writer reads "inert" while still drawing.
**Countermeasure:** a control shows a positive readback that the kill changed the thing it kills; an "inert" verdict without one is not evidence.
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-02.

### 123 - Step 0 on one condition taken to cover another
**Class:** The diagnostic that convicted a writer at night was assumed to hold at dusk; the shipped dusk panel kept the defect.
**Countermeasure:** run step 0 for every time of day the defect is graded on; the chair's crop gate looks at every panel before review.
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-03.

### 124 - A claimed no-op that was not measured
**Class:** A report asserted a scaling factor was 1 at night (so a change would not move night); measured it was 0.593 (dusk 0.556).
**Countermeasure:** a "no change here" claim carries the reading (the factor, a before/after crop pair); the next worker re-measures it.
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-04.

### 125 - A guard that finds its subject by proximity
**Class:** The hearth guard fell back to the nearest chimney when the hearth plume vanished and PASSED on the wrong object.
**Countermeasure:** bind the guard to the owner of the subject and FAIL when it is absent; add a positive-evidence counterfactual and seed the subject away (`plume=none FAIL`).
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-05.

### 126 - A pass quoted from a builder's own capture pair that does not reproduce
**Class:** `UNMOVED chimney diff_px=0 PASS` came from the builder's captures; a fresh verifier run against two `main` captures read above the allowance (two chimney boxes overlap the hearth box; rendered captures never diff to zero).
**Countermeasure:** re-run a builder's PASS from fresh captures with the rig's capture-to-capture spread printed; keep regions that must stay unmoved out of the changed object's footprint.
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-06 (open).

### 127 - A census rule with no noise floor
**Class:** A fail-closed rule counted NEW grader-named classes as regressions; the same census on frames the round never touched finds 13 NEW classes, so it could not tell noise from a change.
**Countermeasure:** measure the floor on untouched frames and require the class's pixels to have moved beyond the rig's spread (Q251: >= 2 graders AND moved pixels).
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-07.

### 128 - A scorer grammar stricter than the grader's prompt
**Class:** The scorer requires `why=` tokens the grader prompt did not make unmissable; one grader's first file was refused and re-emitted.
**Countermeasure:** keep the raw file, report the re-emission, and make the required token part of the prompt's own output checklist.
**Origin:** Kingdom: Survival, round 12, 2026-10-03/04 - Librarian #R12-08.

### 129 - A step 0 whose single-writer kills are all null
**Class:** Every one-variable kill of the suspected writers reads null, and the brief re-tunes a constant anyway; the cause is the model.
**Countermeasure:** when all single-writer kills are null, run a draw-stage trace (value at each stage of the draw) before re-briefing.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-01.

### 130 - A chair's unmeasured cause relayed into a brief
**Class:** The ledger names a cause as a hypothesis (the pool re-lights the shadow) and it steers a brief; measurement refutes it. Neighbour of #121.
**Countermeasure:** measure a cause before it is relayed; label it UNMEASURED and do not brief on it.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-02.

### 131 - Capture jitter read as a regression
**Class:** Two captures of one tree differ by up to 12.5 % because time-driven shader motion (foliage wind on a boot-dependent TIME) is not pinned.
**Countermeasure:** pin the time-driven term for the harness before any pixel census; print the pin state per capture.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-03.

### 132 - Hard planes from a full-alpha root
**Class:** A new overlay shape renders as hard geometric planes because its root is a full-alpha region on open ground, not because of its texture.
**Countermeasure:** inscribe the root in the base's footprint and read the produced texels; look at the root first.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-04.

### 133 - A shadow planned without the light's pool
**Class:** A shadow shape is built and tuned while the light's pool caps what is visible (casters at the pool's rim); the shape passes and the goal does not.
**Countermeasure:** plan shadow and pool together; measure the visible tail length at the casters before building.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-05.

### 134 - An equality probe that compares a thing with itself
**Class:** PIN_PATCH_EQUAL compared the pin patch with one derived from the same source, so it could not fail.
**Countermeasure:** compare against an independently pinned hash (`PIN_PATCH_SHA256`) and check the git return codes; seed the mismatch.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-06.

### 135 - Readings printed after a failed control
**Class:** The census tool printed MOVED/UNMOVED after its own live control failed.
**Countermeasure:** a failed or missing control forces every dependent reading UNEVALUABLE inside the function that prints it.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-07.

### 136 - A node-count guard that passes with orphans
**Class:** FAN_NODES counted through the owner's bookkeeping and missed orphan nodes.
**Countermeasure:** count real and orphan nodes by independent enumeration; seed an orphan.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-08.

### 137 - A recorded md5 whose seed does not reproduce
**Class:** A verify record names seed A with an md5 that reproduces only with seed B (the printed label may differ from the passed argument).
**Countermeasure:** quote the full command line with every md5 and re-run it on `main` before quoting it (OPEN).
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-09.

### 138 - Plan-review churn before any pixel moves
**Class:** Four brief revisions and two plan reviews (~1.0 M tokens) specified a model first exercised at the crop gate.
**Countermeasure:** after the second revision, build a throwaway probe of the riskiest assumption before a third.
**Origin:** Kingdom: Survival, round 12b, 2026-10-04 - Librarian #R12b-10.

### 139 - A refuted hypothesis, a convicted layer
**Class:** Step 0 refuted the brief's cause (pitch) yet the kills convicted one layer; choosing a lever from the refuted story would have been wrong.
**Countermeasure:** trace the draw stages of one image before choosing a lever (#R12b-01 generalised).
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-01.

### 140 - A blur that assumes texture axes = screen axes
**Class:** A sheared texture's across-sun taps blurred ~2 px while along-sun taps blurred ~240 px, so an unsmoothed sum survived.
**Countermeasure:** axis-aware blur (`blur_x_scale`, default 1.0 identical); move by half steps and re-measure.
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-02.

### 141 - Widening a blur without its padding and texel budget
**Class:** Clipped tails (alpha 0.2084 at the border), then the old budget exceeded the 4096-texel cap (4124).
**Countermeasure:** pad and budget follow the kernel; guards `qa_union_pad` and `UNION_TEXEL_CAP`, seeded with the old budget.
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-03.

### 142 - A shader-side fix that texel digests cannot prove
**Class:** No texel moves, so digests stay equal; a seed inverting the level gate survived because boot never reaches it.
**Countermeasure:** guard on pixels and on the uniform's value through day -> dusk -> day (`UNION_COMB_GATE`).
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-04.

### 143 - Ground drift in a pixel census
**Class:** TIME terms in the ground shader, road-wear ticks and wandering units moved pixels no shadow touches (0.5-10 %).
**Countermeasure:** opt-in pins with logged state, spread proven 0.0000, no exclusion mask; keep pins off rows whose margin moves with the pinned phase.
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-05.

### 144 - A pre-registered close rule that contradicts an accepted chair path
**Class:** A literal HARNESS-CLOSE on every green gate because the lever came from an authorised deviation.
**Countermeasure:** the brief names the close path for a lever from an authorised deviation.
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-06.

### 145 - A watchdog that matches itself
**Class:** `pgrep -f` matched the watchdog; a Codex capacity failure also needed a retry.
**Countermeasure:** track the started PID, close stdin, retry on capacity failure.
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-07.

### 146 - Thin margins at their edge
**Class:** `DUSK_MODEL` 2.45 at a 0.05 tolerance and `qa_union_plateau` 8/9 with one outlier.
**Countermeasure:** record the margin with the result; do not widen tolerances silently.
**Origin:** Kingdom: Survival, round 12c, 2026-10-05 - Librarian #R12c-08.

### 147 - A dev server that watches paths other processes write
**Class:** The owner's running game reloaded whenever a worktree or a capture rebuilt an html file under the watched tree.
**Countermeasure:** the watcher ignores build and agent output directories by path segment (a recursive glob would also freeze reload inside a worktree checkout); verify red then green (output touches silent, a source edit still reloads).
**Origin:** Victory Realm, round 11, 2026-10-14 - Librarian #R11-14 (ledger R11-D2).

### 148 - A check exclusion bounded only by a minimum sample
**Class:** A band check leaves out figures near an overlay and needs 6 judged; the overlay can grow until over half the sample is excluded and the check still passes on exactly 6, and a defect confined to the excluded figures is never judged. Neighbour of #38, #119.
**Countermeasure:** cap the left-out share as well as the judged floor, or judge the excluded subjects on a frame with the overlay hidden; seed a larger overlay and watch it go red.
**Origin:** Victory Realm, round 11, 2026-10-14 - Librarian #R11-16 (V11c2 F-c2-1, seed S5b).

### 149 - Avoidance that reads positions, not destinations
**Class:** A unit avoids hexes its mates hold now and have arrived on, then steps onto a marching mate's end hex, which becomes shared when that mate arrives; the earlier fix closed only the arrived case. Neighbour of #44, #49.
**Countermeasure:** avoidance reads each mate's committed destination as well as its position; fuzz with marching mates and count ticks of shared hex.
**Origin:** Victory Realm, round 11, 2026-10-14 - Librarian #R11-12 (Codex #1, open as R11-CX-1).

### 150 - A scan that reports a candidate as passing without running every check on it
**Class:** A search over candidate ticks or frames printed "passes" from a subset of the content checks; the chosen candidate then failed a check the scan never read, and a ruling was made on the first verdict. Neighbour of #126.
**Countermeasure:** the scan prints every check's verdict per candidate, a candidate passes only if all are ok, and the report names the checks run; the builder reruns the full set on the chosen candidate before recording.
**Origin:** Victory Realm, round 12, 2026-10-14 - Librarian #R12-24 (9a, returns 0009 and 0010).

### 151 - A tuning lever whose direction was asserted, not derived
**Class:** A brief said "lower the constant gives more of X"; the comparison it feeds (`men >= K x need`) does the opposite, so following the text moves the metric the wrong way and can trigger a needless escalation.
**Countermeasure:** for each lever the brief states the comparison it feeds and the direction it moves each metric, read from the code, and the first measurement moves it once each way.
**Origin:** Victory Realm, round 12, 2026-10-14 - Librarian #R12-17 (Codex brief review finding 8).

### 152 - A stock limit standing where the owner asked for a rate
**Class:** "Slow expansion" was specified as a schedule of allowed holdings; unused allowances accumulate and can be spent at once, and losses or conquest create allowances, so the rate is unbounded and the acceptance metric punishes legitimate play.
**Countermeasure:** specify a minimum gap since the last event for a rate, count events made separately from items held, and pin both with a seed that spends banked allowance.
**Origin:** Victory Realm, round 12, 2026-10-14 - Librarian #R12-16 (Codex brief review finding 7).

### 153 - A new formula that was never run on the old fixtures
**Class:** A rewritten score goes to zero on the exact fixture an existing test requires positive, and a filter applied to the order but not to the decision input removes the feasible action as well.
**Countermeasure:** the brief evaluates the new formula on every existing fixture for that rule and names the tests that must stay green; each filter is applied to the input the decision reads, with a control where the filtered item changes the decision.
**Origin:** Victory Realm, round 12, 2026-10-14 - Librarian #R12-13 (Codex brief review findings 1 and 13).

### 154 - Two entry points for one job, only one aware of pending state
**Class:** A single-action preflight validated against the committed state while the batch path validated against the state plus the queue, so the second of two fast clicks passed and the engine refused it. The same shape appears when a predicate reads "now" (current displacement) where the fact is "ever" (it was a drag).
**Countermeasure:** route every entry point through one validator that sees the queue, and store a fact that happened as a flag set at the event, not recomputed from the current position; seed each by reverting the call.
**Origin:** Victory Realm, round 12, 2026-10-14 - Librarian #R12-04, #R12-05.

### 155 - A rule whose boundary only a recorded session pins
**Class:** A seeded defect in a distance bound (`=== 1` to `<= 2`) passed every unit test, scenario row and baseline and was caught only by an end-to-end replay, because no test named the rule; a replay-only guard fails late and says nothing about which rule moved. Neighbour of #79.
**Countermeasure:** each rule gets a unit case at its boundary on either side; when a seeded defect is caught by one row alone, add the case before closing.
**Origin:** Victory Realm, round 12, 2026-10-14 - Librarian #R12-25 (V12 F-1, open as LOW).
