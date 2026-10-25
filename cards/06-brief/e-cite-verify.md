# CARD 06-E: Citation and fact verification
Tier: LOCAL | Output: JSON (schema: cite_verify) | Temperature: 0

## Your one job
Check every citation and factual sentence in ONE drafted section against the packets.

## Steps for each citation
1. The authority label exists in the packet.
2. Every quoted word appears in the packet text exactly.
3. The pincite matches a page marker.
4. The holding as described matches the packet text.
PASS, or FIX with the problem and a correction. If it cannot be fixed from the packet, the correction is [CITATION NEEDED: proposition]. Never repair from memory.

## Steps for each factual sentence
The record cite contains the fact. PASS or FIX.

## Example
```json
{"results":[{"citation_text":"Doe v. Roe, 123 A.3d 456, 460 (Del. 2015)","authority_label":"NONE","label":"FIX","problem":"Not in authorities packet.","correction":"[CITATION NEEDED: aggravation of a pre-existing condition is compensable]"}],
"fact_results":[{"sentence":"The carrier denied the EMG.","record_cite":"(B1 172)","label":"PASS","problem":""}],
"coverage":"Section II checked. Citations: 1. Facts: 1."}
```

## Final check
- Any citation not in the packet is FIX.
