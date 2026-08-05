# What we chose not to do, and why

Several deliberate omissions, most-consequential first. Each is a choice with a stated reason, not a time-out. (A sixth — the analyst-persona probe — was later executed per its pre-registration; results in P4 Stage 0.)

## 1. No cross-family judge — every LLM verdict here is Claude judging Claude

Both places an LLM produces verdicts — Benchmark A's adjudicator (claude-opus-5 grading Haiku/Sonnet/Opus 4.6 responses) and Benchmark B's probe + sweep judges (claude-opus-5 scoring Sonnet 4.6 probe responses and all 600 sweep responses from Haiku/Sonnet/Opus 4.6) — use a judge from the same model family as the graded models. Same-family judges can prefer their relatives' phrasing and conventions (self-preference bias), inflating absolute scores and potentially tilting tier gaps. The constraint: the provided key is Anthropic-only. What we did inside it: the judge is at least a *different model* from every graded model (no exact self-grading), and for Benchmark A the 63-pair blind human adjudication is the family-agnostic check — κ = 0.840 bounds how much family bias can distort that instrument. Benchmark B's probe has no human pass; its conclusions are stated as judge-conditional. What survives with no judge at all (computed, P2 §Judge-independence): 160/444 verdicts are purely deterministic; the tactical tier ladder stays monotone under deterministic-only grading (27.4/28.6/31.0%), and the assumption-subset ladder — the repo's headline numbers — is **100% judge-free** (6.5/13.0/17.4%). The judge also performs reference-anchored *verification* (against gold + gold CoT), not open preference judging — the high-exposure case for self-preference — and the probe's Δ is a same-judge contrast in which family bias differences out. The fix is one afternoon with a second vendor's key: rerun `p2/financeqa/grade.py` and `p2/prbench/run_probe.py` with a non-Claude judge (~$15), report per-judge κ against the same human labels, and read the judge-disagreement items.

## 2. Run-to-run consistency (check 4.5 — TBD for both benchmarks)

Every reported score is single-run. Bounding the variance needs 3–5 repeats at ~3× the inference spend. This is the exact gap our own survey criticizes public benchmarks for (pass@1 is not the score), so it is named rather than hidden.

## 3. The Stage-1 grader fix, quantified but not applied

The measured 7.9% false-accept channel (incidental-number matches on sentence-like golds) has a specified one-line fix costing ~$1.5 (63 re-routed judge calls). Deliberately not applied so every checked-in number remains exactly reproducible from checked-in code; the defect, its size, and the fix are documented in P2 instead.

## 4. Content-aware padding attack on Benchmark B

The zero-content padding attack failed to inflate scores (an honest negative, reported in B3). The stronger attack — boilerplate engineered against each item's criterion vocabulary — is designed but unrun; the harness ships, so it is a rerun, not a rebuild.

## 5. Per-domain economic weighting of the coverage map

P1's coverage histogram counts evals, treating every domain as equal. Ranking the six empty domains by economic stake (practitioner headcount × hours on task × model time-saved) is what would turn the gap list into a build priority — the first thing we'd add with more time, as stated in P1's Conclusion.
