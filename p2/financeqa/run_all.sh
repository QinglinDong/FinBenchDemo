#!/bin/bash
# Reproduce the P2 improved-eval numbers end to end.
# Prereq: ANTHROPIC_API_KEY in the environment (or in ../../.env), python3 + `pip install anthropic`.
set -euo pipefail
cd "$(dirname "$0")"

if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -f ../../.env ]; then
  set -a; source ../../.env; set +a
fi

python3 prepare_items.py   # ../../benchmarks/financeqa/test.csv (checked in) -> data/items.jsonl
python3 run_models.py      # 148 items x 3 models -> results/responses.jsonl (idempotent)
python3 perturb.py         # format-invariance probe -> results/perturbation.csv (no API cost)
python3 grade.py           # 3 graders incl. opus-5 adjudicator -> results/grades.csv (judge cached)
python3 analyze.py         # headline tables -> results/summary.md
python3 make_plots.py     # -> results/plots/ (4 Annex A figures, no API)
# Optional (P4 Stage 0, ~$5): python3 probe_persona.py  # -> results/persona_grades.csv
