"""Convert the checked-in FinanceQA dataset (../benchmarks/financeqa/test.csv,
downloaded once from https://huggingface.co/datasets/AfterQuery/FinanceQA,
Apache-2.0) into data/items.jsonl — all 148 items, no sampling.

row_id = 0-based row index in the CSV (matches the HF dataset-viewer row_idx).
"""
import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
SOURCE_CSV = Path(__file__).parent.parent.parent / "benchmarks" / "financeqa" / "test.csv"


def main():
    with open(SOURCE_CSV, newline="") as f:
        rows = []
        for i, row in enumerate(csv.DictReader(f)):
            row["row_id"] = i
            rows.append(row)
    if len(rows) != 148:
        raise SystemExit(f"Expected 148 rows, got {len(rows)}")

    out = DATA_DIR / "items.jsonl"
    with open(out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    counts = {}
    for r in rows:
        counts[r["question_type"]] = counts.get(r["question_type"], 0) + 1
    print(f"Wrote {len(rows)} items -> {out}; type counts: {counts}")


if __name__ == "__main__":
    main()
