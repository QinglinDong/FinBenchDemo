"""Stage 0 of the P4 plan (pre-registered in P4.leverage_finding.md): the
analyst-persona prompting probe.

Re-runs the 46 assumption items with a persona system prompt that explicitly
licenses the analyst move Mode 1 abdicates — constructing undisclosed inputs
via standard conventions. Everything else (user prompt, grader) is identical
to the baseline run, so the delta vs. results/grades.csv isolates elicitation.

Interpretation rule (fixed in advance, P4 Stage 0): the recovered fraction of
the baseline->prompted gap is the share of Mode 1 that is elicitation, not
capability; it gates Stages 1-2.

Outputs: results/persona_responses.jsonl, results/persona_judge_cache.jsonl,
results/persona_grades.csv, and a printed comparison table.
"""
import csv
import json
import time
from pathlib import Path

import anthropic

from graders import numeric_match
from grade import JUDGE_MODEL, JUDGE_SYSTEM, judge_prompt, JSON_RE

P2 = Path(__file__).parent
ITEMS = P2 / "data" / "items.jsonl"
BASE_GRADES = P2 / "results" / "grades.csv"
RESP_OUT = P2 / "results" / "persona_responses.jsonl"
CACHE = P2 / "results" / "persona_judge_cache.jsonl"
GRADES_OUT = P2 / "results" / "persona_grades.csv"

MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"]
MAX_TOKENS = 2048

PERSONA_SYSTEM = (
    "You are a buy-side analyst hand-spreading this company. When a required "
    "input is not disclosed, construct it using standard analyst conventions, "
    "state the assumption you made, and still produce a number. "
    "Provide concise answers."
)


def build_user_prompt(item):
    context = item.get("context") or ""
    return f"Context:\n{context}\n\nQuestion: {item['question']}\n\nProvide a concise answer."


def load_jsonl(path):
    if not Path(path).exists():
        return []
    return [json.loads(l) for l in open(path)]


def main():
    items = [i for i in load_jsonl(ITEMS) if i["question_type"] == "assumption"]
    print(f"{len(items)} assumption items x {len(MODELS)} models")
    client = anthropic.Anthropic()

    # --- responses (resumable)
    done = {(r["row_id"], r["model"]) for r in load_jsonl(RESP_OUT)}
    with open(RESP_OUT, "a") as f:
        for model in MODELS:
            for item in items:
                if (item["row_id"], model) in done:
                    continue
                resp = client.messages.create(
                    model=model, max_tokens=MAX_TOKENS, system=PERSONA_SYSTEM,
                    messages=[{"role": "user", "content": build_user_prompt(item)}],
                )
                text = "".join(b.text for b in resp.content if b.type == "text")
                f.write(json.dumps({"row_id": item["row_id"], "model": model,
                                    "response": text}) + "\n")
                f.flush()
                time.sleep(0.3)
    print("responses complete")

    # --- grading (same two-stage grader as baseline)
    item_by_id = {i["row_id"]: i for i in items}
    cache = {(r["row_id"], r["model"]): r for r in load_jsonl(CACHE)}
    rows = []
    with open(CACHE, "a") as cf:
        for rec in load_jsonl(RESP_OUT):
            item = item_by_id[rec["row_id"]]
            nm = numeric_match(item["answer"], rec["response"])
            if nm is True:
                verdict, category = "correct", "none"
            else:
                key = (rec["row_id"], rec["model"])
                if key not in cache:
                    resp = client.messages.create(
                        model=JUDGE_MODEL, max_tokens=2000, system=JUDGE_SYSTEM,
                        messages=[{"role": "user",
                                   "content": judge_prompt(item, rec["response"])}],
                    )
                    text = "".join(b.text for b in resp.content if b.type == "text")
                    out = json.loads(JSON_RE.search(text).group(0))
                    entry = {"row_id": rec["row_id"], "model": rec["model"], **out}
                    cache[key] = entry
                    cf.write(json.dumps(entry) + "\n")
                    cf.flush()
                out = cache[key]
                verdict, category = out["verdict"], out.get("failure_category", "other")
            rows.append({"row_id": rec["row_id"], "model": rec["model"],
                         "persona_correct": int(verdict == "correct"),
                         "failure_category": category})

    rows.sort(key=lambda r: (r["model"], r["row_id"]))
    with open(GRADES_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # --- comparison vs baseline
    base = [r for r in csv.DictReader(open(BASE_GRADES))
            if r["question_type"] == "assumption"]
    print(f"\n{'model':20s} {'baseline':>9s} {'persona':>9s} {'delta':>7s}  missing_assumption base->persona")
    for model in MODELS:
        b = [r for r in base if r["model"] == model]
        p = [r for r in rows if r["model"] == model]
        ba = sum(int(r["improved"]) for r in b) / len(b)
        pa = sum(r["persona_correct"] for r in p) / len(p)
        bm = sum(1 for r in b if r["failure_category"] == "missing_assumption")
        pm = sum(1 for r in p if r["failure_category"] == "missing_assumption")
        print(f"{model:20s} {ba:9.1%} {pa:9.1%} {pa-ba:+7.1%}  {bm} -> {pm}")


if __name__ == "__main__":
    main()
