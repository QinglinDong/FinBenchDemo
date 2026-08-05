# What we chose not to do, and why

## No cross-family judge — every LLM verdict here is Claude judging Claude

Both places an LLM produces verdicts — Benchmark A's adjudicator (claude-opus-5 grading Haiku/Sonnet/Opus 4.6 responses) and Benchmark B's probe + sweep judges (claude-opus-5 scoring Sonnet 4.6 probe responses and all 600 sweep responses from Haiku/Sonnet/Opus 4.6) — use a judge from the same model family as the graded models. Same-family judges can prefer their relatives' phrasing and conventions (self-preference bias), inflating absolute scores and potentially tilting tier gaps.

The constraint: the provided key is Anthropic-only.

What we did inside that constraint:

- The judge is at least a *different model* from every graded model — no exact self-grading.
- For Benchmark A, the 63-pair blind human adjudication is the family-agnostic check: κ = 0.840 bounds how much family bias can distort that instrument. Benchmark B's probe has no human pass; its conclusions are stated as judge-conditional.
- What survives with no judge at all (computed, P2 §Judge-independence): 160/444 verdicts are purely deterministic; the tactical tier ladder stays monotone under deterministic-only grading (27.4/28.6/31.0%), and the assumption-subset ladder — the repo's headline numbers — is **100% judge-free** (6.5/13.0/17.4%).
- The judge performs reference-anchored *verification* (against gold + gold CoT), not open preference judging — the high-exposure case for self-preference — and the probe's Δ is a same-judge contrast in which family bias differences out.

The fix is one afternoon with a second vendor's key: rerun `p2/financeqa/grade.py` and `p2/prbench/run_probe.py` with a non-Claude judge (~$15), report per-judge κ against the same human labels, and read the judge-disagreement items.

*(Other deliberate scope choices are documented where they arose: run-to-run consistency as check 4.5 TBD and the deferred Stage-1 grader fix in P2's Benchmark A sections; the untested content-aware padding attack in P2 §B3; the skipped per-domain economic weighting in P1's Hierarchy Coverage and Limits.)*
