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
