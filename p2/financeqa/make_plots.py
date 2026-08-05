"""Regenerate the four Benchmark A figures from checked-in results (no API).

Inputs: results/grades.csv, data/human_labels.csv. Outputs: results/plots/*.png.
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

P = Path(__file__).parent
PLOTS = P / "results" / "plots"

MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"]
LABELS = ["Haiku 4.5", "Sonnet 4.6", "Opus 4.6"]
COLORS = ["#8ecae6", "#219ebc", "#023047"]

TRUE = ("true", "1", "yes")


def load():
    return list(csv.DictReader(open(P / "results" / "grades.csv")))


def fig_tier_accuracy(rows):
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(MODELS))
    for off, grader, key in ((-0.2, "naive EM", "naive_em"), (0.2, "improved", "improved")):
        accs = []
        for m in MODELS:
            sub = [r for r in rows if r["model"] == m]
            accs.append(100 * sum(r[key].lower() in TRUE for r in sub) / len(sub))
        bars = ax.bar(x + off, accs, 0.4, label=grader,
                      color="#bbbbbb" if key == "naive_em" else None)
        if key == "improved":
            for b, c in zip(bars, COLORS):
                b.set_color(c)
        for b, v in zip(bars, accs):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("accuracy, all 148 items (%)")
    ax.set_title("Tier ladder: naive exact-match (0=0=0) vs improved grader")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS / "tier_accuracy.png", dpi=150)


def fig_difficulty(rows):
    per_item = defaultdict(int)
    for r in rows:
        if r["improved"].lower() in TRUE:
            per_item[r["row_id"]] += 1
    all_ids = {r["row_id"] for r in rows}
    counts = Counter(per_item.get(i, 0) for i in all_ids)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ks = [0, 1, 2, 3]
    vals = [counts.get(k, 0) for k in ks]
    bars = ax.bar([str(k) for k in ks], vals, color=["#9b2226", "#ee9b00", "#ee9b00", "#2a9d8f"])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, str(v), ha="center")
    ax.set_xlabel("tiers correct (of 3)")
    ax.set_ylabel("items")
    ax.set_title("Item difficulty: 57 dead / 26 discriminating / 65 free (148 items)")
    fig.tight_layout()
    fig.savefig(PLOTS / "difficulty_distribution.png", dpi=150)


def fig_failure_profile(rows):
    cats = ["missing_assumption", "wrong_convention", "wrong_value_or_arithmetic", "wrong_concept"]
    present = sorted({r["failure_category"] for r in rows
                      if r["failure_category"] not in ("", "none")})
    cats = [c for c in cats if c in present] + [c for c in present if c not in cats]
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(cats))
    for i, (m, lab, col) in enumerate(zip(MODELS, LABELS, COLORS)):
        sub = [r for r in rows if r["model"] == m and r["improved"].lower() not in TRUE]
        cnt = Counter(r["failure_category"] for r in sub)
        ax.bar(x + (i - 1) * 0.27, [cnt.get(c, 0) for c in cats], 0.27, label=lab, color=col)
    ax.set_xticks(x, [c.replace("_", "\n") for c in cats], fontsize=9)
    ax.set_ylabel("failed responses")
    ax.set_title("Failure profile by adjudicator category — missing_assumption does not shrink")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS / "failure_profile.png", dpi=150)


def fig_grader_confusion(rows):
    human = list(csv.DictReader(open(P / "data" / "human_labels.csv")))
    grade = {(r["row_id"], r["model"]): r for r in rows}
    mats = {}
    for key, name in (("naive_em", "naive EM"), ("improved", "improved")):
        m = np.zeros((2, 2), int)  # [human incorrect/correct][grader incorrect/correct]
        for h in human:
            g = grade[(h["row_id"], h["model"])]
            hv = 1 if h["human_verdict"].strip() == "correct" else 0
            gv = 1 if g[key].lower() in TRUE else 0
            m[hv][gv] += 1
        mats[name] = m
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6))
    for ax, (name, m) in zip(axes, mats.items()):
        ax.imshow(m, cmap="Blues", vmin=0, vmax=m.max())
        for i in range(2):
            for j in range(2):
                ax.text(j, i, m[i][j], ha="center", va="center",
                        color="white" if m[i][j] > m.max() * 0.6 else "black")
        ax.set_xticks([0, 1], ["grader: incorrect", "grader: correct"], fontsize=8)
        ax.set_yticks([0, 1], ["human:\nincorrect", "human:\ncorrect"], fontsize=8)
        ax.set_title(name, fontsize=10)
    fig.suptitle("Grader vs 63 blind human labels (κ: naive −0.000, improved 0.840)", fontsize=10)
    fig.tight_layout()
    fig.savefig(PLOTS / "grader_confusion.png", dpi=150)


if __name__ == "__main__":
    PLOTS.mkdir(exist_ok=True)
    rows = load()
    fig_tier_accuracy(rows)
    fig_difficulty(rows)
    fig_failure_profile(rows)
    fig_grader_confusion(rows)
    print("wrote 4 plots ->", PLOTS)
