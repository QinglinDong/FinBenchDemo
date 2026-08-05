"""Figures for the B sweep: tier ladder, score distributions, category heatmap.

Outputs to results/plots/ (no API).
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "sweep_items.jsonl"
JUDG = P2 / "results" / "sweep_judgments.jsonl"
PLOTS = P2 / "results" / "plots"

MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"]
LABELS = ["Haiku 4.5", "Sonnet 4.6", "Opus 4.6"]
COLORS = ["#8ecae6", "#219ebc", "#023047"]


def main():
    items = {json.loads(l)["task"]: json.loads(l) for l in open(ITEMS)}
    recs = [json.loads(l) for l in open(JUDG)]
    PLOTS.mkdir(exist_ok=True)

    # 1. tier ladder: standard vs hard grouped bars
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.35
    x = np.arange(len(MODELS))
    for off, subset, color_shift in ((-width / 2, "standard", 1.0), (width / 2, "hard", 0.55)):
        means = []
        for m in MODELS:
            sc = [r["score"] for r in recs if r["model"] == m and r["subset"] == subset]
            means.append(sum(sc) / len(sc))
        bars = ax.bar(x + off, means, width, label=subset,
                      color=[c for c in COLORS], alpha=color_shift)
        for b, v in zip(bars, means):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.3f}",
                    ha="center", fontsize=9)
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("mean PRBench-style score")
    ax.set_title("PRBench-Finance sweep: tier ladder, standard vs hard (100+100 items)")
    ax.legend(title="subset")
    ax.set_ylim(0, 0.62)
    fig.tight_layout()
    fig.savefig(PLOTS / "sweep_tier_ladder.png", dpi=150)

    # 2. per-item score distributions (box) by model x subset
    fig, ax = plt.subplots(figsize=(7, 4))
    data, positions, colors = [], [], []
    for i, m in enumerate(MODELS):
        for j, subset in enumerate(("standard", "hard")):
            data.append([r["score"] for r in recs if r["model"] == m and r["subset"] == subset])
            positions.append(i * 2.4 + j)
            colors.append(COLORS[i])
    bp = ax.boxplot(data, positions=positions, widths=0.8, patch_artist=True,
                    medianprops={"color": "black"})
    for patch, c, j in zip(bp["boxes"], colors, [0, 1] * 3):
        patch.set_facecolor(c)
        patch.set_alpha(1.0 if j == 0 else 0.55)
    ax.set_xticks([i * 2.4 + 0.5 for i in range(len(MODELS))], LABELS)
    ax.set_ylabel("per-item score")
    ax.set_title("Per-item score distribution (solid = standard, faded = hard)")
    fig.tight_layout()
    fig.savefig(PLOTS / "sweep_score_distribution.png", dpi=150)

    # 3. unsatisfied-rate heatmap: category x model (positive criteria)
    cat_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in recs:
        rub = {c["id"]: c for c in items[r["task"]]["rubric"]}
        for v in r["verdicts"]:
            c = rub.get(v["id"])
            if c is None or c["weight"] <= 0:
                continue
            cat_stats[c["category"]][r["model"]][1] += 1
            if not v["satisfied"]:
                cat_stats[c["category"]][r["model"]][0] += 1
    cats = sorted(cat_stats, key=lambda c: -cat_stats[c][MODELS[0]][0] / max(cat_stats[c][MODELS[0]][1], 1))
    grid = np.array([[cat_stats[c][m][0] / cat_stats[c][m][1] for m in MODELS] for c in cats])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(grid, cmap="YlOrRd", vmin=0.3, vmax=0.85, aspect="auto")
    ax.set_xticks(range(len(MODELS)), LABELS)
    ax.set_yticks(range(len(cats)), cats, fontsize=9)
    for i in range(len(cats)):
        for j in range(len(MODELS)):
            ax.text(j, i, f"{grid[i, j]:.0%}", ha="center", va="center", fontsize=9,
                    color="white" if grid[i, j] > 0.7 else "black")
    ax.set_title("Unsatisfied rate by rubric category (positive criteria)")
    fig.colorbar(im, label="unsatisfied rate")
    fig.tight_layout()
    fig.savefig(PLOTS / "sweep_category_heatmap.png", dpi=150)
    print("wrote 3 plots ->", PLOTS)


if __name__ == "__main__":
    main()
