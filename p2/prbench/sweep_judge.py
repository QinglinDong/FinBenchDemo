"""Batched rubric judging for the B sweep: ONE judge call per response scores
all of that item's criteria at once.

Documented protocol deviation from PRBench (which judges each criterion in an
independent call): batching cuts judge calls ~16x. Acceptable here because the
sweep's purpose is model failure-profiling and tier comparison, not judge-
protocol audit (the per-criterion protocol was already exercised by run_probe).

Output: results/sweep_judgments.jsonl - one line per (task, model) with
per-criterion verdicts and the PRBench-style clipped weighted score.
"""
import json
import time
from pathlib import Path

import anthropic

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "sweep_items.jsonl"
RESPONSES = P2 / "data" / "sweep_responses.jsonl"
OUT = P2 / "results" / "sweep_judgments.jsonl"

JUDGE_MODEL = "claude-opus-5"
MAX_TOKENS = 3000

SYSTEM = """You judge whether a model's answer to a finance professional's question satisfies each criterion of an expert rubric. Judge every criterion independently on its own text. For criteria describing a harmful action (negative weight), satisfied=true means the response actually commits that harmful action.

Respond with ONLY a JSON array, one object per criterion, in the given order:
[{"id": "<criterion id>", "satisfied": true|false}, ...]"""


def score(rubric, verdicts):
    sat = {v["id"]: bool(v["satisfied"]) for v in verdicts}
    pos = sum(c["weight"] for c in rubric if c["weight"] > 0)
    raw = sum(c["weight"] * (1 if sat.get(c["id"]) else 0) for c in rubric) / pos
    return max(0.0, min(1.0, raw))


def build_user(item, response):
    crits = "\n".join(f'- id {c["id"]} (weight {c["weight"]:+.0f}, {c["category"]}): {c["title"]}'
                      for c in item["rubric"])
    return (f"QUESTION:\n{item['prompt']}\n\nRESPONSE:\n{response}\n\n"
            f"CRITERIA ({len(item['rubric'])}):\n{crits}")


def main():
    items = {json.loads(l)["task"]: json.loads(l) for l in open(ITEMS)}
    responses = [json.loads(l) for l in open(RESPONSES)]
    OUT.parent.mkdir(exist_ok=True)
    done = set()
    if OUT.exists():
        done = {(json.loads(l)["task"], json.loads(l)["model"]) for l in open(OUT)}

    client = anthropic.Anthropic()
    n = 0
    with open(OUT, "a") as f:
        for rec in responses:
            key = (rec["task"], rec["model"])
            if key in done:
                continue
            item = items[rec["task"]]
            want = {c["id"] for c in item["rubric"]}
            verdicts = None
            for attempt in range(3):
                resp = client.messages.create(
                    model=JUDGE_MODEL, max_tokens=MAX_TOKENS,
                    output_config={"effort": "low"}, system=SYSTEM,
                    messages=[{"role": "user", "content": build_user(item, rec["response"])}],
                )
                text = "".join(b.text for b in resp.content if b.type == "text")
                s, e = text.find("["), text.rfind("]")
                if s != -1 and e > s:
                    try:
                        got = json.loads(text[s:e + 1])
                        if {v["id"] for v in got} >= want:
                            verdicts = got
                            break
                    except (json.JSONDecodeError, TypeError, KeyError):
                        pass
                time.sleep(1)
            if verdicts is None:
                raise RuntimeError(f"unparseable after 3 tries: {key} :: {text[:200]!r}")
            f.write(json.dumps({
                "task": rec["task"], "model": rec["model"],
                "subset": item["subset"],
                "score": score(item["rubric"], verdicts),
                "verdicts": verdicts,
            }) + "\n")
            f.flush()
            n += 1
            if n % 20 == 0:
                print(f"[judge {n}] {rec['model']} {rec['task'][:8]}")
    print(f"judging done: {n} new")


if __name__ == "__main__":
    main()
