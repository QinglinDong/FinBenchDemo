"""Aggregate the graded results into the headline tables.

Reads:
  results/grades.csv          (from grade.py)
  results/perturbation.csv    (from perturb.py)
  data/human_labels.csv       (optional; author adjudication - see
                               make_adjudication_template.py)

Writes results/summary.md with:
  1. Accuracy per model x grader (overall and by question type)
  2. Tier separation (adjacent-tier gaps) per grader
  3. Format-invariance probe results
  4. Grader-vs-human agreement (accuracy + Cohen's kappa) when labels exist
  5. Failure-category counts from the adjudicator
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

P2 = Path(__file__).parent
GRADES = P2 / "results" / "grades.csv"
PERTURB = P2 / "results" / "perturbation.csv"
HUMAN = P2 / "data" / "human_labels.csv"
OUT = P2 / "results" / "summary.md"

MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"]
GRADERS = ["naive_em", "improved"]


def read_csv(path):
    if not Path(path).exists():
        return []
    return list(csv.DictReader(open(path)))


def rate(rows, field):
    vals = [int(r[field]) for r in rows if r[field] != ""]
    return sum(vals) / len(vals) if vals else float("nan")


def kappa(pairs):
    """Cohen's kappa for binary (a, b) label pairs."""
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in pairs if a == b) / n
    pa1 = sum(a for a, _ in pairs) / n
    pb1 = sum(b for _, b in pairs) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe == 1:
        return float("nan")
    return (po - pe) / (1 - pe)


def main():
    grades = read_csv(GRADES)
    if not grades:
        raise SystemExit("No grades.csv - run grade.py first")
    perturb = read_csv(PERTURB)
    human = {(r["row_id"], r["model"]): r["human_verdict"].strip().lower()
             for r in read_csv(HUMAN) if r.get("human_verdict", "").strip()}

    lines = ["# P2 results summary", ""]

    # 1. accuracy per model x grader
    n = len({r["row_id"] for r in grades})
    lines += [f"## Accuracy by model and grader (n={n} items: "
              "38 basic + 46 assumption + 64 conceptual)", "",
              "| model | grader | overall | basic | assumption | conceptual |",
              "|---|---|---|---|---|---|"]
    for model in MODELS:
        mrows = [r for r in grades if r["model"] == model]
        for grader in GRADERS:
            by_type = {t: [r for r in mrows if r["question_type"] == t]
                       for t in ("basic", "assumption", "conceptual")}
            lines.append(
                f"| {model} | {grader} | {rate(mrows, grader):.1%} "
                f"| {rate(by_type['basic'], grader):.1%} "
                f"| {rate(by_type['assumption'], grader):.1%} "
                f"| {rate(by_type['conceptual'], grader):.1%} |")
    lines.append("")

    # 2. tier separation
    lines += ["## Tier separation (adjacent-tier accuracy gaps)", "",
              "| grader | haiku | sonnet | opus | sonnet-haiku | opus-sonnet | monotone? |",
              "|---|---|---|---|---|---|---|"]
    for grader in GRADERS:
        acc = [rate([r for r in grades if r["model"] == m], grader) for m in MODELS]
        gaps = [acc[1] - acc[0], acc[2] - acc[1]]
        monotone = "yes" if acc[0] <= acc[1] <= acc[2] else "no"
        lines.append(f"| {grader} | {acc[0]:.1%} | {acc[1]:.1%} | {acc[2]:.1%} "
                     f"| {gaps[0]:+.1%} | {gaps[1]:+.1%} | {monotone} |")
    lines.append("")

    # 3. perturbation probe
    if perturb:
        non_id = [r for r in perturb if r["variant"] != "identity"]
        lines += ["## Format-invariance probe (correct-by-construction gold variants)", "",
                  f"Probes: {len(perturb)} total, {len(non_id)} non-identity.", "",
                  "| grader | acceptance (all) | acceptance (non-identity) |",
                  "|---|---|---|"]
        for field, name in [("naive_em_accepts", "naive_em"),
                            ("numeric_match_accepts", "numeric stage of improved")]:
            lines.append(f"| {name} | {rate(perturb, field):.1%} "
                         f"| {rate(non_id, field):.1%} |")
        lines.append("")

    # 4. grader vs human
    if human:
        lines += ["## Grader vs. human adjudication", "",
                  f"Labeled pairs: {len(human)}", "",
                  "| grader | agreement | Cohen's kappa |",
                  "|---|---|---|"]
        for grader in GRADERS:
            pairs = []
            for r in grades:
                key = (r["row_id"], r["model"])
                if key in human:
                    pairs.append((int(r[grader]),
                                  1 if human[key] == "correct" else 0))
            po = sum(1 for a, b in pairs if a == b) / len(pairs)
            lines.append(f"| {grader} | {po:.1%} | {kappa(pairs):.3f} |")
        lines.append("")
    else:
        lines += ["## Grader vs. human adjudication", "",
                  "_data/human_labels.csv not found or empty - run "
                  "make_adjudication_template.py and fill in verdicts._", ""]

    # 5. failure categories (judged rows only)
    judged = [r for r in grades if r["judged"] == "1" and r["improved"] == "0"]
    if judged:
        lines += ["## Adjudicator failure categories (incorrect responses only)", "",
                  "| model | category | count |", "|---|---|---|"]
        cat = defaultdict(Counter)
        for r in judged:
            cat[r["model"]][r["failure_category"]] += 1
        for model in MODELS:
            for c, n in cat[model].most_common():
                lines.append(f"| {model} | {c} | {n} |")
        defensible = sum(1 for r in judged if r["defensible_alternative"] == "1")
        lines += ["", f"Incorrect responses flagged as *defensible alternative "
                      f"convention*: {defensible} / {len(judged)}", ""]

    OUT.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
