"""Format-invariance probe: the controlled-perturbation validity check.

For every sampled item whose gold answer contains a parseable primary number,
generate K surface variants of the gold answer that are CORRECT BY
CONSTRUCTION (same value, different formatting/scale/wording). Feed each
variant to each grader as if it were a model response. A good grader accepts
100% of them; every rejection is a measured format confound.

This is deterministic and costs no API calls for naive_em / numeric_match.
The judge is NOT probed here by default (cost control); the judge's validity
is measured against human labels in analyze.py instead.

Output: results/perturbation.csv and a printed summary.
"""
import csv
import json
import re
from pathlib import Path

from graders import naive_em, numeric_match, parse_numbers

P2 = Path(__file__).parent
SAMPLE = P2 / "data" / "items.jsonl"
OUT = P2 / "results" / "perturbation.csv"

# primary-number extraction for variant construction
NUM_ONLY = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def make_variants(gold):
    """Return list of (variant_name, text) that are value-equivalent to gold.

    Only built when the gold has an unambiguous primary interpretation:
    we take the first number and the gold's own scale markers.
    """
    interps = parse_numbers(gold)
    if not interps:
        return []
    m = NUM_ONLY.search(gold)
    if not m:
        return []
    raw = m.group(0)
    value = float(raw.replace(",", ""))

    is_pct = "%" in gold
    gold_l = gold.lower()
    in_millions = "million" in gold_l
    in_billions = "billion" in gold_l
    is_mult = bool(re.search(r"\d\s*x\b", gold_l))

    variants = [("identity", gold)]
    plain = f"{value:,.2f}".rstrip("0").rstrip(".")

    if is_pct:
        variants += [
            ("pct_word", f"{plain} percent"),
            ("pct_sentence", f"The figure is approximately {plain}%."),
        ]
    elif is_mult:
        variants += [
            ("mult_word", f"{plain} times"),
            ("mult_sentence", f"The ratio is {plain}x."),
        ]
    elif in_millions:
        bn = value / 1000.0
        bn_str = f"{bn:,.4f}".rstrip("0").rstrip(".")
        variants += [
            ("scale_word", f"${plain} million"),
            ("scale_shift_bn", f"${bn_str} billion"),
            ("suffix", f"${plain}M"),
            ("sentence", f"The company's figure for the period was ${plain} million."),
        ]
    elif in_billions:
        mn = value * 1000.0
        variants += [
            ("scale_word", f"${plain} billion"),
            ("scale_shift_mn", f"${mn:,.0f} million"),
            ("suffix", f"${plain}B"),
            ("sentence", f"The company's figure for the period was ${plain} billion."),
        ]
    else:
        variants += [
            ("no_symbols", plain.replace(",", "")),
            ("sentence", f"The answer is {plain}."),
        ]
    return variants


def main():
    items = [json.loads(line) for line in open(SAMPLE)]
    rows = []
    for item in items:
        for name, text in make_variants(item["answer"]):
            rows.append({
                "row_id": item["row_id"],
                "question_type": item["question_type"],
                "variant": name,
                "variant_text": text,
                "gold": item["answer"],
                "naive_em_accepts": int(naive_em(item["answer"], text)),
                "numeric_match_accepts": int(bool(numeric_match(item["answer"], text))),
            })

    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    non_identity = [r for r in rows if r["variant"] != "identity"]
    for grader in ("naive_em_accepts", "numeric_match_accepts"):
        acc_all = sum(r[grader] for r in rows) / total
        acc_var = (sum(r[grader] for r in non_identity) / len(non_identity)
                   if non_identity else float("nan"))
        print(f"{grader:24s} all={acc_all:.1%} ({total} probes)  "
              f"non-identity={acc_var:.1%} ({len(non_identity)} probes)")
    print(f"Wrote {total} probe rows -> {OUT}")


if __name__ == "__main__":
    main()
