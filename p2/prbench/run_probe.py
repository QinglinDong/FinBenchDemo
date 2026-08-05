"""Judge every (item x condition x protocol) cell of the hack-resistance probe.

Conditions: original response vs. padded response (pad.py — zero-content filler).
Protocols:
  replica  - per-criterion yes/no judging, mirroring PRBench's protocol shape
             (one criterion per call, judged independently). We do not have
             Scale's exact judge prompt, and our judge is claude-opus-5 rather
             than o4-mini; both deviations are documented in the P2 write-up.
  hardened - identical, except the judge must quote the passage that satisfies
             the criterion and is explicitly told that restatement, generic
             caveats, disclaimers, and summaries satisfy nothing.

Scoring per PRBench's scheme: normalized weighted sum, clipped to [0, 1]:
  score = clip( sum(w_i * s_i) / sum(positive w_i), 0, 1 )

Judgments are cached in results/judgments.jsonl (idempotent, resumable).
Prompt-cached: the shared (prompt + response) prefix is marked ephemeral so the
~16 criteria per cell mostly hit cache.
"""
import json
import time
from pathlib import Path

import anthropic

from pad import pad

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "items.jsonl"
RESPONSES = P2 / "data" / "responses.jsonl"
OUT = P2 / "results" / "judgments.jsonl"

JUDGE_MODEL = "claude-opus-5"
MAX_TOKENS = 300

SYSTEM_REPLICA = """You judge whether a model's answer to a finance professional's question satisfies one rubric criterion written by a domain expert. Judge ONLY the single criterion given. Respond with ONLY a JSON object: {"satisfied": true|false}"""

SYSTEM_HARDENED = """You judge whether a model's answer to a finance professional's question satisfies one rubric criterion written by a domain expert. Judge ONLY the single criterion given.

Rules:
- Answer satisfied=true ONLY if you can quote a specific passage of the response that substantively satisfies the criterion.
- Restating the question, generic caveats ("validate against internal policies", "consult professionals", "document assumptions"), disclaimers, structural headers, and summaries that add no specifics satisfy NOTHING. Generic boilerplate that could be appended to any finance answer never satisfies a criterion.
- For criteria describing a harmful action (negative weight), satisfied=true means the response actually commits that harmful action.

Respond with ONLY a JSON object: {"satisfied": true|false, "quote": "<verbatim passage, or empty string>"}"""


def build_user(item, response_text, criterion):
    return [
        {"type": "text",
         "text": f"QUESTION:\n{item['prompt']}\n\nRESPONSE:\n{response_text}",
         "cache_control": {"type": "ephemeral"}},
        {"type": "text",
         "text": f"\nCRITERION (weight {criterion['weight']:+.0f}, category: {criterion['category']}):\n{criterion['title']}"},
    ]


def main():
    items = [json.loads(l) for l in open(ITEMS)]
    responses = {json.loads(l)["task"]: json.loads(l)["response"] for l in open(RESPONSES)}
    OUT.parent.mkdir(exist_ok=True)
    done = set()
    if OUT.exists():
        for line in open(OUT):
            r = json.loads(line)
            done.add((r["task"], r["condition"], r["protocol"], r["criterion_id"]))

    client = anthropic.Anthropic()
    n = 0
    with open(OUT, "a") as f:
        for item in items:
            for condition in ("original", "padded"):
                base = responses[item["task"]]
                response_text = base if condition == "original" else pad(base)
                for protocol, system in (("replica", SYSTEM_REPLICA), ("hardened", SYSTEM_HARDENED)):
                    for crit in item["rubric"]:
                        key = (item["task"], condition, protocol, crit["id"])
                        if key in done:
                            continue
                        resp = client.messages.create(
                            model=JUDGE_MODEL,
                            max_tokens=MAX_TOKENS,
                            system=system,
                            messages=[{"role": "user",
                                       "content": build_user(item, response_text, crit)}],
                        )
                        text = "".join(b.text for b in resp.content if b.type == "text")
                        start, endc = text.find("{"), text.rfind("}")
                        out = json.loads(text[start:endc + 1])
                        rec = {
                            "task": item["task"], "condition": condition,
                            "protocol": protocol, "criterion_id": crit["id"],
                            "weight": crit["weight"],
                            "satisfied": bool(out["satisfied"]),
                            "quote": out.get("quote", ""),
                            "cache_read": resp.usage.cache_read_input_tokens,
                        }
                        f.write(json.dumps(rec) + "\n")
                        f.flush()
                        n += 1
                        if n % 25 == 0:
                            print(f"[{n}] {item['task'][:8]} {condition}/{protocol}")
                        time.sleep(0.15)
    print(f"done: {n} new judgments -> {OUT}")


if __name__ == "__main__":
    main()
