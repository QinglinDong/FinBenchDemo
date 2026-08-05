"""Query the three model tiers on all 148 FinanceQA items.

Replicates the paper's prompt exactly (FinanceQA, arXiv:2501.18062, Sec. 3):
  system: "You are a helpful assistant. Provide concise answers."
  user:   "Context:\n{context}\n\nQuestion: {question}\n\nProvide a concise answer."

All three models run without extended thinking (Haiku 4.5 has thinking off by
default; Sonnet 4.6 / Opus 4.6 run without thinking when the parameter is
omitted), so the tier comparison measures the base model, not thinking budget.

Output: results/responses.jsonl (one line per item x model; idempotent — reruns
skip pairs already present).
"""
import json
import time
from pathlib import Path

import anthropic

P2 = Path(__file__).parent
SAMPLE = P2 / "data" / "items.jsonl"
OUT = P2 / "results" / "responses.jsonl"

MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"]
SYSTEM = "You are a helpful assistant. Provide concise answers."
MAX_TOKENS = 2048


def build_user_prompt(item):
    context = item.get("context") or ""
    return f"Context:\n{context}\n\nQuestion: {item['question']}\n\nProvide a concise answer."


def main():
    OUT.parent.mkdir(exist_ok=True)
    items = [json.loads(line) for line in open(SAMPLE)]

    done = set()
    if OUT.exists():
        for line in open(OUT):
            rec = json.loads(line)
            done.add((rec["row_id"], rec["model"]))

    client = anthropic.Anthropic()
    n_new = 0
    with open(OUT, "a") as f:
        for model in MODELS:
            for item in items:
                key = (item["row_id"], model)
                if key in done:
                    continue
                resp = client.messages.create(
                    model=model,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM,
                    messages=[{"role": "user", "content": build_user_prompt(item)}],
                )
                text = "".join(b.text for b in resp.content if b.type == "text")
                rec = {
                    "row_id": item["row_id"],
                    "question_type": item["question_type"],
                    "model": model,
                    "response": text,
                    "stop_reason": resp.stop_reason,
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                }
                f.write(json.dumps(rec) + "\n")
                f.flush()
                n_new += 1
                print(f"[{n_new}] {model} row {item['row_id']} ok "
                      f"({resp.usage.output_tokens} out tokens)")
                time.sleep(0.3)
    print(f"Done. {n_new} new responses; total pairs now "
          f"{len(done) + n_new} / {len(items) * len(MODELS)}")


if __name__ == "__main__":
    main()
