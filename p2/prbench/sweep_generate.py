"""Generate sweep responses: 200 items x 3 tiers (thinking off, bare prompt).

Output: data/sweep_responses.jsonl (resumable).
"""
import json
import time
from pathlib import Path

import anthropic

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "sweep_items.jsonl"
OUT = P2 / "data" / "sweep_responses.jsonl"
MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"]
MAX_TOKENS = 1500


def main():
    items = [json.loads(l) for l in open(ITEMS)]
    done = set()
    if OUT.exists():
        done = {(json.loads(l)["task"], json.loads(l)["model"]) for l in open(OUT)}
    client = anthropic.Anthropic()
    n = 0
    with open(OUT, "a") as f:
        for model in MODELS:
            for item in items:
                if (item["task"], model) in done:
                    continue
                resp = client.messages.create(
                    model=model, max_tokens=MAX_TOKENS,
                    messages=[{"role": "user", "content": item["prompt"]}],
                )
                text = "".join(b.text for b in resp.content if b.type == "text")
                f.write(json.dumps({"task": item["task"], "model": model,
                                    "response": text}) + "\n")
                f.flush()
                n += 1
                if n % 25 == 0:
                    print(f"[gen {n}] {model}")
                time.sleep(0.2)
    print(f"generation done: {n} new")


if __name__ == "__main__":
    main()
