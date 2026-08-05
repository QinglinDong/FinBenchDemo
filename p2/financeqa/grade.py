"""Grade all model responses with three graders and write results/grades.csv.

Graders:
  naive_em      - normalized exact string match (baseline reimplementation of
                  the paper's unpublished "exact match" grading)
  numeric_match - deterministic scale/format-invariant numeric equivalence
  improved      - two-stage: numeric_match, with an LLM adjudicator
                  (claude-opus-5) deciding every case numeric_match does not
                  auto-accept. The adjudicator grades strictly (no partial
                  credit, matching the paper) but separately records whether a
                  "wrong" answer used a professionally defensible alternative
                  convention — that flag feeds the label-noise analysis.

Idempotent: judged verdicts are cached in results/judge_cache.jsonl.
"""
import csv
import json
import re
from pathlib import Path

import anthropic

from graders import naive_em, numeric_match

P2 = Path(__file__).parent
SAMPLE = P2 / "data" / "items.jsonl"
RESPONSES = P2 / "results" / "responses.jsonl"
JUDGE_CACHE = P2 / "results" / "judge_cache.jsonl"
GRADES_CSV = P2 / "results" / "grades.csv"

JUDGE_MODEL = "claude-opus-5"
JUDGE_MAX_TOKENS = 2000
CONTEXT_CHAR_LIMIT = 8000

JUDGE_SYSTEM = """You are grading answers to FinanceQA, a benchmark of financial-analyst questions computed from a 10-K. Grading is strict and binary, like the original benchmark: no partial credit.

You are given the question, the source context, the gold answer with the annotator's chain of thought, and a candidate answer. Decide:

1. verdict: "correct" if the candidate's final answer is numerically equivalent to the gold answer under ANY formatting, scale, rounding (within 0.5%), or sign-presentation convention (e.g. "$32,095 (in millions)" == "$32.1B" == "32,095 million dollars"). If the candidate gives multiple values, grade the one it presents as its final answer. Otherwise "incorrect". A candidate that refuses, gives no number when the gold is a number, or answers a different question is "incorrect".
2. defensible_alternative: true ONLY if the candidate is "incorrect" but arrived at its different value through a professionally defensible alternative convention or assumption a practicing analyst could justify (e.g. a different but standard adjusted-EBITDA definition), executed without arithmetic errors. This does NOT change the verdict.
3. failure_category: one of "none" (if correct), "wrong_value_or_arithmetic", "missing_assumption" (did not make the assumption the gold requires, e.g. answered with the unadjusted figure or said the data is unavailable), "wrong_concept" (misunderstood what metric was asked), "refused_or_incomplete", "format_only" (numerically equivalent but you judged incorrect for a non-numeric reason - this should be rare).

Respond with ONLY a JSON object:
{"verdict": "correct"|"incorrect", "defensible_alternative": true|false, "failure_category": "...", "reason": "<one sentence>"}"""

JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def judge_prompt(item, response):
    context = (item.get("context") or "")[:CONTEXT_CHAR_LIMIT]
    return f"""QUESTION:
{item['question']}

CONTEXT (10-K excerpt):
{context}

GOLD ANSWER:
{item['answer']}

GOLD CHAIN OF THOUGHT:
{item.get('chain_of_thought') or '(none)'}

CANDIDATE ANSWER:
{response}"""


def load_jsonl(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in open(path)]


def call_judge(client, item, response):
    resp = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=JUDGE_MAX_TOKENS,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": judge_prompt(item, response)}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    m = JSON_RE.search(text)
    if not m:
        raise ValueError(f"Judge returned no JSON: {text[:200]}")
    out = json.loads(m.group(0))
    assert out["verdict"] in ("correct", "incorrect"), out
    return out


def main():
    items = {r["row_id"]: r for r in load_jsonl(SAMPLE)}
    responses = load_jsonl(RESPONSES)
    if not responses:
        raise SystemExit("No responses found - run run_models.py first")

    cache = {(r["row_id"], r["model"]): r for r in load_jsonl(JUDGE_CACHE)}
    client = anthropic.Anthropic()

    rows = []
    with open(JUDGE_CACHE, "a") as cache_f:
        for rec in responses:
            item = items[rec["row_id"]]
            gold, resp_text = item["answer"], rec["response"]
            em = naive_em(gold, resp_text)
            nm = numeric_match(gold, resp_text)

            key = (rec["row_id"], rec["model"])
            if nm is True:
                # deterministic accept - no judge needed for the verdict
                verdict, defensible, category, reason = "correct", False, "none", "numeric match"
                judged = False
            else:
                if key not in cache:
                    out = call_judge(client, item, resp_text)
                    entry = {"row_id": rec["row_id"], "model": rec["model"], **out}
                    cache[key] = entry
                    cache_f.write(json.dumps(entry) + "\n")
                    cache_f.flush()
                    print(f"judged {rec['model']} row {rec['row_id']}: "
                          f"{out['verdict']} ({out['failure_category']})")
                out = cache[key]
                verdict = out["verdict"]
                defensible = bool(out.get("defensible_alternative"))
                category = out.get("failure_category", "other")
                reason = out.get("reason", "")
                judged = True

            rows.append({
                "row_id": rec["row_id"],
                "question_type": rec["question_type"],
                "model": rec["model"],
                "naive_em": int(em),
                "numeric_match": "" if nm is None else int(bool(nm)),
                "judged": int(judged),
                "improved": int(verdict == "correct"),
                "defensible_alternative": int(defensible),
                "failure_category": category,
                "judge_reason": reason,
                "gold": items[rec["row_id"]]["answer"],
                "response": rec["response"],
            })

    rows.sort(key=lambda r: (r["model"], r["row_id"]))
    with open(GRADES_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} graded rows -> {GRADES_CSV}")


if __name__ == "__main__":
    main()
