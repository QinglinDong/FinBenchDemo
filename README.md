# FinBench 

A survey, critique, runnable improvement, and failure analysis of public finance benchmarks, centered on **FinanceQA** (AfterQuery, 2025) with **PRBench-Finance** (Scale AI, 2025) as the contrast case.

## Contents

- [What's in each file](#whats-in-each-file)
- [Run the P2 improvement in one command](#run-the-p2-improvement-in-one-command)
- [`benchmarks/` — the surveyed evals, verbatim](#benchmarks--the-surveyed-evals-verbatim)
- [One thing we chose not to do, and why](#one-thing-we-chose-not-to-do-and-why)

## What's in each file

Files carry `P1.`–`P5.` ordering prefixes; they are the assignment's `selected_evals.md`, `claude_run_eval_improvement.md`, `failure_modes.md`, `leverage_finding.md`, and `vendor_brief.md` respectively.

| file | part | contents |
|---|---|---|
| `P1.selected_evals.md` | P1 | Finance task hierarchy (D1–D12), six-criteria benchmark filter (C1–C6), 20-eval landscape with per-row criteria scoring and coverage histogram, four deep dives, and the P2 target selection |
| `P2.claude_run_eval_improvement.md` | P2 | Two benchmarks, each critique → runnable improvement → validity measurement: FinanceQA (the missing grader, rebuilt and validated) and PRBench-Finance (judge hack-resistance probe + hardened protocol) |
| `P3.failure_modes.md` | P3 | Named taxonomy of how Claude fails on finance-practitioner tasks, with item-level evidence from the P2 runs |
| `P4.leverage_finding.md` | P4 | How Anthropic could use one failure mode to improve Claude: intervention, pipeline stage, cost, and the measurement that confirms it worked |
| `P5.vendor_brief.md` | P5 | One-page commissioning brief to extend the improved eval to ~200 items via a vendor |
| `p2/` | P2 code | `financeqa/` (runner, graders, probes, human labels, results) and `prbench/` (padding attack, judge protocols, results) — each with its own `run_all.sh` |

## Run the P2 improvements in one command

```bash
cd p2 && ANTHROPIC_API_KEY=<your-key> ./run_all.sh
```

Runs both benchmarks (FinanceQA grader, then the PRBench probe). Per-step breakdowns: sections A4 and B4 of `P2.claude_run_eval_improvement.md`. All datasets are checked in under `benchmarks/`; a from-scratch rerun costs roughly $30 total and is idempotent/resumable.

## `benchmarks/` — the surveyed evals, verbatim

Raw official data for the four deep-dived evals plus the BlueFin public sample kept as demotion evidence (FinanceQA, PRBench-Finance, TaxCalcBench, SpreadsheetBench 2, BlueFin), downloaded unmodified so every P1 claim traces to a primary artifact. Catalog with counts and licenses: `benchmarks/README.md`.

## What we chose not to do, and why

Six deliberate omissions with reasons — cross-family judge validation first: see `not_done.md`.
