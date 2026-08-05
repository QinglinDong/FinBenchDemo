"""Aggregate the B sweep into tier ladders and failure profiles.

Outputs results/sweep_summary.md:
  1. Mean PRBench-style score per tier, overall and standard vs hard
  2. Hard-vs-standard gap per tier (is "hard" still hard for 2025-26 models?)
  3. Per-category unsatisfied rates (positive criteria) per tier
"""
import json
from collections import defaultdict
from pathlib import Path

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "sweep_items.jsonl"
JUDG = P2 / "results" / "sweep_judgments.jsonl"
OUT = P2 / "results" / "sweep_summary.md"

MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"]
LABELS = ["Haiku 4.5", "Sonnet 4.6", "Opus 4.6"]


def main():
    items = {json.loads(l)["task"]: json.loads(l) for l in open(ITEMS)}
    recs = [json.loads(l) for l in open(JUDG)]

    lines = ["# PRBench B sweep — results",
             "", f"Items: {len(items)} (100 standard + 100 hard single-turn); "
             f"judged responses: {len(recs)}; batched-criteria judging (deviation documented in sweep_judge.py).", ""]

    # 1-2. tier ladder
    lines += ["## Tier ladder (mean PRBench-style score)", "",
              "| model | overall | standard | hard | hard − standard |", "|---|---|---|---|---|"]
    for m, lab in zip(MODELS, LABELS):
        sub = [r for r in recs if r["model"] == m]
        ov = sum(r["score"] for r in sub) / len(sub)
        st = [r["score"] for r in sub if r["subset"] == "standard"]
        hd = [r["score"] for r in sub if r["subset"] == "hard"]
        st_m, hd_m = sum(st)/len(st), sum(hd)/len(hd)
        lines.append(f"| {lab} | {ov:.3f} | {st_m:.3f} | {hd_m:.3f} | {hd_m-st_m:+.3f} |")
    lines.append("")

    # 3. category profile
    cat_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # cat -> model -> [unsat, tot]
    for r in recs:
        rub = {c["id"]: c for c in items[r["task"]]["rubric"]}
        for v in r["verdicts"]:
            c = rub.get(v["id"])
            if c is None or c["weight"] <= 0:
                continue
            cat_stats[c["category"]][r["model"]][1] += 1
            if not v["satisfied"]:
                cat_stats[c["category"]][r["model"]][0] += 1

    lines += ["## Unsatisfied rate by criteria category (positive criteria)", "",
              "| category | " + " | ".join(LABELS) + " | n/model |", "|---|---|---|---|---|"]
    order = sorted(cat_stats, key=lambda c: -cat_stats[c][MODELS[0]][0]/max(cat_stats[c][MODELS[0]][1], 1))
    for cat in order:
        cells = []
        for m in MODELS:
            u, tot = cat_stats[cat][m]
            cells.append(f"{u/tot:.0%}" if tot else "—")
        ntot = cat_stats[cat][MODELS[0]][1]
        lines.append(f"| {cat} | " + " | ".join(cells) + f" | {ntot} |")

    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
