"""Sample the B sweep item set: 100 standard + 100 hard single-turn items.

standard = single-turn, not in finance_hard; hard = single-turn ∩ finance_hard.
Seed fixed. Output: data/sweep_items.jsonl (task, subset, topic, prompt, rubric).
"""
import json
import random
from pathlib import Path

import pandas as pd

from prepare_items import extract_rubric

P2 = Path(__file__).parent
SEED = 42
N_PER_SUBSET = 100


def main():
    fin = pd.read_parquet(P2.parent.parent / "benchmarks" / "prbench" / "finance.parquet")
    hard_ids = set(pd.read_parquet(P2.parent.parent / "benchmarks" / "prbench" / "finance_hard.parquet")["task"])
    single = fin[fin.turns == 1]
    pools = {
        "standard": single[~single.task.isin(hard_ids)],
        "hard": single[single.task.isin(hard_ids)],
    }
    rng = random.Random(SEED)
    out = P2 / "data" / "sweep_items.jsonl"
    n = 0
    with open(out, "w") as f:
        for subset, pool in pools.items():
            idx = sorted(rng.sample(range(len(pool)), N_PER_SUBSET))
            for _, row in pool.iloc[idx].iterrows():
                f.write(json.dumps({
                    "task": row["task"], "subset": subset, "topic": row["topic"],
                    "prompt": row["prompt_0"], "rubric": extract_rubric(row["rubric"]),
                }) + "\n")
                n += 1
    print(f"wrote {n} sweep items -> {out}")


if __name__ == "__main__":
    main()
