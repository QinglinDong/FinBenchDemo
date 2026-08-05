#!/bin/bash
# Reproduce the PRBench judge hack-resistance probe end to end.
# Prereq: ANTHROPIC_API_KEY in the environment (or in ../../.env); pip install anthropic pandas pyarrow.
set -euo pipefail
cd "$(dirname "$0")"

if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -f ../../.env ]; then
  set -a; source ../../.env; set +a
fi

python3 prepare_items.py       # ../../benchmarks/prbench/finance.parquet -> data/items.jsonl (15 items, seed 42)
python3 generate_responses.py  # claude-sonnet-4-6 answers each item once -> data/responses.jsonl
python3 run_probe.py       # 15 items x {original,padded} x {replica,hardened} judged per criterion (cached, resumable)
python3 analyze.py         # -> results/summary.md

# B sweep: 200 items (100 standard + 100 hard) x 3 tiers, batched judging (~$22)
python3 sweep_prepare.py   # -> data/sweep_items.jsonl (seed 42)
python3 sweep_generate.py  # 600 responses, resumable -> data/sweep_responses.jsonl
python3 sweep_judge.py     # 600 batched claude-opus-5 judgments, resumable -> results/sweep_judgments.jsonl
python3 sweep_analyze.py   # -> results/sweep_summary.md
python3 sweep_plots.py     # -> results/plots/sweep_*.png
