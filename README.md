# FinBench 

A survey, critique, runnable improvement, and failure analysis of public finance benchmarks, centered on **FinanceQA** (AfterQuery, 2025) with **PRBench-Finance** (Scale AI, 2025) as the contrast case.

## Contents

- [What's in each file](#whats-in-each-file)
- [Run the P2 improvements in one command](#run-the-p2-improvements-in-one-command)
- [`benchmarks/` — the surveyed evals, verbatim](#benchmarks--the-surveyed-evals-verbatim)
- [What we chose not to do, and why](#what-we-chose-not-to-do-and-why)

## What's in each file

Files carry `P1.`–`P5.` ordering prefixes; they are the assignment's `selected_evals.md`, `claude_run_eval_improvement.md`, `failure_modes.md`, `leverage_finding.md`, and `vendor_brief.md` respectively.

| file | part | contents |
|---|---|---|
| `P1.selected_evals.md` | P1 | Finance task hierarchy (D1–D12), six-criteria benchmark filter (C1–C6), 20-eval landscape with per-row criteria scoring and coverage histogram, four deep dives, and the P2 target selection |
| `P2.claude_run_eval_improvement.md` | P2 | Two benchmarks, each critique → runnable improvement → validity measurement: FinanceQA (the missing grader, rebuilt and validated) and PRBench-Finance (judge hack-resistance probe + hardened protocol) |
| `P3.failure_modes.md` | P3 | Named failure-mode taxonomy of how Claude fails finance-practitioner work: four modes with item-level evidence, distilled from Benchmark A's graded runs |
| `P4.leverage_finding.md` | P4 | How Anthropic could use one failure mode to improve Claude: intervention, pipeline stage, cost, and measurement — scoped to Benchmark A |
| `P5.vendor_brief.md` | P5 | One-page commissioning brief extending Benchmark A to ~200 items via a vendor |
| `p2/` | P2 code | `financeqa/` (runner, graders, probes, human labels, results) and `prbench/` (padding attack, judge protocols, results) — each with its own `run_all.sh` |

## Run the P2 improvements in one command

```bash
cd p2 && ANTHROPIC_API_KEY=<your-key> ./run_all.sh
```

Runs both benchmarks (FinanceQA grader, then the PRBench probe and 3-tier sweep). Per-step breakdowns: sections A4 and B4 of `P2.claude_run_eval_improvement.md`. All datasets are checked in under `benchmarks/`; a from-scratch rerun costs roughly $50 total and is idempotent/resumable.

## `benchmarks/` — the surveyed evals, verbatim

Raw official data for the four deep-dived evals plus the BlueFin public sample kept as demotion evidence (FinanceQA, PRBench-Finance, TaxCalcBench, SpreadsheetBench 2, BlueFin), downloaded unmodified so every P1 claim traces to a primary artifact. Catalog with counts and licenses: `benchmarks/README.md`.

## What we chose not to do, and why

**No cross-family judge — every LLM verdict here is Claude judging Claude.** Both places an LLM produces verdicts — Benchmark A's adjudicator (claude-opus-5 grading Haiku/Sonnet/Opus 4.6 responses) and Benchmark B's probe + sweep judges (claude-opus-5 scoring all 600 sweep responses) — use a judge from the same model family as the graded models. Same-family judges can prefer their relatives' phrasing and conventions (self-preference bias), inflating absolute scores and potentially tilting tier gaps.

The constraint: the provided key is Anthropic-only. What we did inside it:

- The judge is at least a *different model* from every graded model — no exact self-grading.
- For Benchmark A, the 63-pair blind human adjudication is the family-agnostic check: κ = 0.840 bounds how much family bias can distort that instrument. Benchmark B's probe has no human pass; its conclusions are stated as judge-conditional.
- What survives with no judge at all (computed, P2 §Judge-independence): 160/444 verdicts are purely deterministic, and the assumption-subset ladder — the repo's headline numbers — is **100% judge-free** (6.5/13.0/17.4%).
- The judge performs reference-anchored *verification* (against gold + gold CoT), not open preference judging, and the probe's Δ is a same-judge contrast in which family bias differences out.

The fix is one afternoon with a second vendor's key: rerun `p2/financeqa/grade.py` and `p2/prbench/run_probe.py` with a non-Claude judge (~$15), report per-judge κ against the same human labels, and read the judge-disagreement items.

Smaller scope choices are documented where they arose: run-to-run consistency (P2 check 4.5 TBD), the deferred Stage-1 grader fix (P2 §A3), the untested content-aware padding attack (P2 §B3), the per-domain economic weighting (P1 Limits).
