"""Draw a stratified adjudication subset and emit a blank labeling template.

The template (data/adjudication_template.csv) is filled in by a human and
saved as data/human_labels.csv with the `human_verdict` column set to
"correct" or "incorrect" for each (row_id, model) pair. It deliberately does
NOT show any grader's verdict, so the human labels blind.

Stratification: for each model, sample per question type so all three types
and all three models are represented. Seed fixed for reproducibility.
"""
import csv
import json
import random
from pathlib import Path

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "items.jsonl"
RESPONSES = P2 / "results" / "responses.jsonl"
OUT = P2 / "data" / "adjudication_template.csv"

SEED = 7
PER_MODEL_PER_TYPE = 7  # 7 x 3 types x 3 models = 63 pairs to label


def main():
    items = {json.loads(l)["row_id"]: json.loads(l) for l in open(ITEMS)}
    responses = [json.loads(l) for l in open(RESPONSES)]

    rng = random.Random(SEED)
    chosen = []
    models = sorted({r["model"] for r in responses})
    for model in models:
        for qtype in ("basic", "assumption", "conceptual"):
            pool = [r for r in responses
                    if r["model"] == model and r["question_type"] == qtype]
            k = min(PER_MODEL_PER_TYPE, len(pool))
            chosen.extend(rng.sample(pool, k))
    chosen.sort(key=lambda r: (r["model"], r["row_id"]))

    with open(OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["row_id", "model", "question_type", "question",
                         "gold", "gold_chain_of_thought", "response",
                         "human_verdict", "human_note"])
        for r in chosen:
            item = items[r["row_id"]]
            writer.writerow([
                r["row_id"], r["model"], r["question_type"],
                item["question"], item["answer"],
                item.get("chain_of_thought") or "",
                r["response"], "", "",
            ])
    print(f"Wrote {len(chosen)} pairs to label -> {OUT}")
    print("Fill human_verdict with correct/incorrect, save as data/human_labels.csv")


if __name__ == "__main__":
    main()
