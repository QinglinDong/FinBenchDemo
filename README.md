# FinBench — RWKW take-home: Finance evals

A survey, critique, runnable improvement, and failure analysis of public finance benchmarks, centered on **FinanceQA** (AfterQuery, 2025) with **PRBench-Finance** (Scale AI, 2025) as the contrast case.

## What's in each file

| file | part | contents |
|---|---|---|
| `selected_evals.md` | P1 | The finance-benchmark landscape (6 clusters + coverage gaps), comparison axes, and the two evals taken forward for deep study |
| `claude_run_eval_improvement.md` | P2 | Critique of FinanceQA (unpublished grader, format confound, ambiguous gold labels, contamination, single-document base), the improvement — a published two-stage grader — and the validity measurements (format-invariance probe, grader-vs-human agreement, tier separation) |
| `failure_modes.md` | P3 | Named taxonomy of how Claude fails on finance-practitioner tasks, with item-level evidence from the P2 runs |
| `leverage_finding.md` | P4 | How Anthropic could use one failure mode to improve Claude: intervention, pipeline stage, cost, and the measurement that confirms it worked |
| `vendor_brief.md` | P5 | One-page commissioning brief to extend the improved eval to ~200 items via a vendor |
| `p2/` | P2 code | Runner, graders, probes, analysis, the full dataset, and all result files |

## Run the P2 improvement in one command

```bash
cd p2 && ANTHROPIC_API_KEY=<your-key> ./run_all.sh
```

Details, per-step breakdown, and expected outputs: bottom section of `claude_run_eval_improvement.md`. The dataset (`benchmarks/financeqa/test.csv`, Apache-2.0) is checked in; a from-scratch rerun costs under $15 and is idempotent/resumable.

## `benchmarks/` — the surveyed evals, verbatim

Raw official data for eight of the P1 evals (FinanceQA, PRBench, FinQA, finqa-verified, FinanceBench open sample, TaxCalcBench, FinRetrieval, BigFinanceBench subset), downloaded unmodified so every P1 claim traces to a primary artifact. Catalog with counts and licenses: `benchmarks/README.md`.

## One thing we chose not to do, and why

See `not_done.md`.
