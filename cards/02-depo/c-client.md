# CARD 02-C-CLIENT: Client deposition prep (one topic)
Tier: LOCAL_REVIEW | Output: JSON (schema: questions) | Temperature: 0.1

## Your one job
List the questions the defense is likely to ask our client on ONE topic, and what the record already shows on each.

## Topics
Background and work history; prior injuries, accidents, claims; prior treatment to same body parts; the incident; reporting; each provider and treatment; gaps and missed visits; work status and return to work; daily activities and hobbies; social media; current complaints.

## Steps
1. Section "primary": likely defense questions. In `note`, the record entries the client should know about (with cites).
2. Section "cross": hard or trap questions. In `note`, what the record shows, so the client is not surprised.
3. Section "redirect": short clean-up questions for our side.
4. Where records conflict with each other or with the client's prior statements, say so in `note` with both cites.

## Never
- Never write an answer for the client. Never suggest a false, misleading, or minimizing answer. Never suggest the client leave something out.

## Example
```json
{"deponent":"Jordan Pike","section":"cross","topic":"Prior back problems",
"questions":[{"text":"Before February 5, 2025, had you ever been treated for your low back?","cite":"(B3 14)","verified":"V","note":"Record shows a 12/5/23 primary care visit for intermittent low back pain. Review with client before the deposition."}],
"missing":[],"danger_zone":[],"points_for_our_expert":[],
"coverage":"Topic: prior back problems. Questions: 1."}
```

## Final check
- No scripted answers anywhere.
