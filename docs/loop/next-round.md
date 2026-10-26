Use the app-loop skill. Read docs/loop/HANDOFF.md first.

Run the round 1 re-brief of casefile (owner Q24) on `loop/round-01`. Remote Control on. First ask the
owner which tiers to use this session. Then: a Fable brief limited to one shared Python path-identity
check for `src/casefile/config.py` and `scripts/run.sh`, with table-driven alias tests and one test per
D12 exit branch, covering V3-1 to V3-4 and verify2 N2. Then a Codex plan review, the Fable revision,
the build, the full critic round (Codex code review, output critic, blind verifier, in that order, each
separate) and fix cycles (cap three). Close with R1-12 (spec §11 as-built), the round report, the
Librarian and the agent log; fast-forward `main`; open `loop/round-02`; owner check-in. No real client
data at any point. Do not start round 2. At close, write the handoff and the next-round prompt, prompt
the owner to `git push origin main`, and stop.
