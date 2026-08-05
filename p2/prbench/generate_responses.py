"""Generate the baseline responses for the probe items.

One mid-tier model (claude-sonnet-4-6, thinking off) answers each sampled
PRBench prompt once. These are the "original" condition; pad.py derives the
"padded" condition from them deterministically. Using a single generator for
all items keeps the padding contrast clean — the probe measures the judge, not
the responder.

Output: data/responses.jsonl (idempotent, resumable).
"""
import json
import time
from pathlib import Path

import anthropic

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "items.jsonl"
OUT = P2 / "data" / "responses.jsonl"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1500


def main():
    items = [json.loads(l) for l in open(ITEMS)]
    done = set()
    if OUT.exists():
        done = {json.loads(l)["task"] for l in open(OUT)}

    client = anthropic.Anthropic()
    n = 0
    with open(OUT, "a") as f:
        for item in items:
            if item["task"] in done:
                continue
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": item["prompt"]}],
            )
            text = "".join(b.text for b in resp.content if b.type == "text")
            f.write(json.dumps({"task": item["task"], "model": MODEL,
                                "response": text}) + "\n")
            f.flush()
            n += 1
            print(f"[{n}] {item['task'][:8]} ({resp.usage.output_tokens} out tokens)")
            time.sleep(0.3)
    print(f"done: {n} new responses -> {OUT}")


if __name__ == "__main__":
    main()
