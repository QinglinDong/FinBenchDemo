"""Sample PRBench-Finance items for the judge hack-resistance probe.

Reads ../../benchmarks/prbench/finance.parquet (the official release), keeps
single-turn conversations, and samples N items with a fixed seed. (The release
ships no graded final responses for single-turn items - response_0..8 are the
scripted dialogue turns of multi-turn items - so baseline responses are
generated separately by generate_responses.py.)

Output: data/items.jsonl, one line per item:
  task, topic, prompt, rubric
where rubric is a list of {id, title, weight, category} with weight the single
non-null signed weight from the release's six weight fields.
"""
import json
import random
from pathlib import Path

import pandas as pd

P2 = Path(__file__).parent
SOURCE = P2.parent.parent / "benchmarks" / "prbench" / "finance.parquet"
SEED = 42
N_ITEMS = 15

WEIGHT_FIELDS = [
    "critically_important_weight", "important_weight", "slightly_important_weight",
    "detrimental_weight", "critically_detrimental_weight", "slightly_detrimental_weight",
]


def extract_rubric(raw):
    rubric = []
    for crit in raw:
        ann = crit["annotations"]
        weight = None
        for f in WEIGHT_FIELDS:
            v = ann.get(f)
            if v is not None and not pd.isna(v):
                weight = float(v)
                break
        if weight is None:
            continue
        rubric.append({
            "id": crit["id"],
            "title": crit["title"],
            "weight": weight,
            "category": ann.get("criteria_category", ""),
        })
    return rubric


def main():
    df = pd.read_parquet(SOURCE)
    pool = df[df["turns"] == 1].copy()
    print(f"pool: {len(pool)} single-turn items")

    rng = random.Random(SEED)
    idx = sorted(rng.sample(range(len(pool)), N_ITEMS))
    sample = pool.iloc[idx]

    out = P2 / "data" / "items.jsonl"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        for _, row in sample.iterrows():
            rubric = extract_rubric(row["rubric"])
            f.write(json.dumps({
                "task": row["task"],
                "topic": row["topic"],
                "prompt": row["prompt_0"],
                "rubric": rubric,
            }) + "\n")
    n_crit = sum(len(extract_rubric(r)) for r in sample["rubric"])
    print(f"wrote {len(sample)} items, {n_crit} rubric criteria -> {out}")


if __name__ == "__main__":
    main()
