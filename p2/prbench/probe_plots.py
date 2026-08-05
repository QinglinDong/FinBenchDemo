"""Regenerate the two probe figures from checked-in artifacts (no API).

Inputs: ../../benchmarks/prbench/finance.parquet, results/judgments.jsonl.
Outputs: results/plots/rubric_anatomy.png, results/plots/padding_deltas.png.
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from prepare_items import extract_rubric

P = Path(__file__).parent
PLOTS = P / "results" / "plots"


def fig_rubric_anatomy():
    fin = pd.read_parquet(P.parent.parent / "benchmarks" / "prbench" / "finance.parquet")
    weights = [c["weight"] for _, row in fin.iterrows() for c in extract_rubric(row["rubric"])]
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.arange(-10.5, 11.5, 1)
    n, bin_edges, patches = ax.hist(weights, bins=bins, edgecolor="white")
    for patch, edge in zip(patches, bin_edges):
        patch.set_facecolor("#9b2226" if edge < -0.5 else "#219ebc")
    neg = sum(1 for w in weights if w < 0)
    ax.set_xlabel("criterion weight")
    ax.set_ylabel("criteria")
    ax.set_title(f"PRBench-Finance rubric anatomy: {len(weights):,} criteria, "
                 f"{neg} ({neg / len(weights):.1%}) negative")
    fig.tight_layout()
    fig.savefig(PLOTS / "rubric_anatomy.png", dpi=150)


def fig_padding_deltas():
    recs = [json.loads(l) for l in open(P / "results" / "judgments.jsonl")]
    rubrics = defaultdict(dict)   # (task, protocol, condition) -> {crit: (weight, sat)}
    for r in recs:
        rubrics[(r["task"], r["protocol"], r["condition"])][r["criterion_id"]] = (
            r["weight"], r["satisfied"])

    def score(cell):
        pos = sum(w for w, _ in cell.values() if w > 0)
        raw = sum(w * (1 if s else 0) for w, s in cell.values()) / pos
        return max(0.0, min(1.0, raw))

    tasks = sorted({t for t, _, _ in rubrics})
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(tasks))
    for off, protocol, col in ((-0.2, "replica", "#219ebc"), (0.2, "hardened", "#023047")):
        deltas = [score(rubrics[(t, protocol, "padded")]) - score(rubrics[(t, protocol, "original")])
                  for t in tasks]
        ax.bar(x + off, deltas, 0.4, label=f"{protocol} (mean {np.mean(deltas):+.3f})", color=col)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x, [t[:6] for t in tasks], rotation=45, fontsize=8)
    ax.set_xlabel("item")
    ax.set_ylabel("padding Δ (padded − original)")
    ax.set_title("Zero-content padding does not inflate scores (15 items × 2 protocols)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS / "padding_deltas.png", dpi=150)


if __name__ == "__main__":
    PLOTS.mkdir(exist_ok=True)
    fig_rubric_anatomy()
    fig_padding_deltas()
    print("wrote 2 plots ->", PLOTS)
