"""Aggregate the probe judgments into the headline hack-resistance numbers.

For each protocol:
  - mean PRBench-style score (normalized weighted, clipped 0-1) on original
    vs. padded responses
  - padding inflation Delta = mean(padded) - mean(original); per-item deltas
  - fidelity check: hardened protocol should track replica on ORIGINAL
    responses (it must resist padding, not deflate real answers)

Writes results/summary.md.
"""
import json
from collections import defaultdict
from pathlib import Path

P2 = Path(__file__).parent
JUDG = P2 / "results" / "judgments.jsonl"
ITEMS = P2 / "data" / "items.jsonl"
OUT = P2 / "results" / "summary.md"


def score(cell):
    pos = sum(w for w, _ in cell if w > 0)
    if pos == 0:
        return None
    raw = sum(w * s for w, s in cell) / pos
    return max(0.0, min(1.0, raw))


def main():
    items = {json.loads(l)["task"]: json.loads(l) for l in open(ITEMS)}
    cells = defaultdict(list)  # (task, condition, protocol) -> [(weight, satisfied)]
    for line in open(JUDG):
        r = json.loads(line)
        cells[(r["task"], r["condition"], r["protocol"])].append(
            (r["weight"], 1 if r["satisfied"] else 0))

    scores = {k: score(v) for k, v in cells.items()}
    tasks = sorted(items)

    lines = ["# PRBench hack-resistance probe — results", "",
             f"Items: {len(tasks)}; judgments: {sum(len(v) for v in cells.values())}", "",
             "| protocol | mean score (original) | mean score (padded) | padding inflation Δ | items inflated / deflated / unchanged |",
             "|---|---|---|---|---|"]
    per_item = {}
    for protocol in ("replica", "hardened"):
        orig = [scores[(t, "original", protocol)] for t in tasks]
        padd = [scores[(t, "padded", protocol)] for t in tasks]
        deltas = [p - o for o, p in zip(orig, padd)]
        per_item[protocol] = deltas
        up = sum(1 for d in deltas if d > 1e-9)
        down = sum(1 for d in deltas if d < -1e-9)
        same = len(deltas) - up - down
        lines.append(
            f"| {protocol} | {sum(orig)/len(orig):.3f} | {sum(padd)/len(padd):.3f} "
            f"| {sum(deltas)/len(deltas):+.3f} | {up} / {down} / {same} |")

    ro = [scores[(t, "original", "replica")] for t in tasks]
    ho = [scores[(t, "original", "hardened")] for t in tasks]
    fid = sum(h - r for r, h in zip(ro, ho)) / len(tasks)
    lines += ["",
              f"Fidelity check (original responses only): hardened − replica mean score = {fid:+.3f} "
              "(near zero = hardening resists padding without deflating real answers).",
              "", "## Per-item padding inflation", "",
              "| task | topic | replica Δ | hardened Δ |", "|---|---|---|---|"]
    for t in tasks:
        lines.append(f"| {t[:12]} | {items[t]['topic'][:32]} "
                     f"| {per_item['replica'][tasks.index(t)]:+.3f} "
                     f"| {per_item['hardened'][tasks.index(t)]:+.3f} |")

    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12]))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
