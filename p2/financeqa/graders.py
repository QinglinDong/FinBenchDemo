"""Deterministic graders for FinanceQA short answers.

Two graders live here:

  naive_em(gold, response)      - normalized exact string match. This is the
      baseline: the paper specifies "exact correct matches" with human graders
      and never published grader code, so a naive automated reimplementation
      is string EM after light normalization.

  numeric_match(gold, response) - scale/format-invariant numeric equivalence.
      Parses the gold answer into one or more (value * scale) interpretations
      (handling $, commas, parentheses-negatives, %, x-multiples, and scale
      words like "million"/"(in millions)"/"B"/"mm"), parses every number in
      the response the same way, and reports a match if any response
      interpretation equals any gold interpretation within REL_TOL.

Known limitation (documented, and quantified by the human-adjudication step):
numeric_match can false-accept when a response mentions the gold value in a
non-answer role (e.g. quoting an input line item). Sign flips (expense shown
as positive vs parenthesized) are accepted and flagged via abs-value matching.
"""
import re

REL_TOL = 0.005  # 0.5% relative tolerance

SCALE_WORDS = {
    "thousand": 1e3, "thousands": 1e3,
    "million": 1e6, "millions": 1e6, "mn": 1e6, "mm": 1e6,
    "billion": 1e9, "billions": 1e9, "bn": 1e9,
    "trillion": 1e12, "trillions": 1e12,
    "k": 1e3, "m": 1e6, "b": 1e9,
}

NUM_RE = re.compile(
    r"(?P<paren>\()?\s*"
    r"(?P<dollar>\$)?\s*"
    r"(?P<neg>-)?"
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"\s*(?P<closeparen>\))?"
    r"(?P<tail>\s*(?:%|percent\b|x\b|[kKmMbB]\b|bn\b|mm\b|mn\b|"
    r"thousands?\b|millions?\b|billions?\b|trillions?\b))?"
)

GLOBAL_SCALE_RE = re.compile(
    r"\(?\s*in\s+(thousands|millions|billions)\b", re.IGNORECASE
)


def _tail_scale(tail):
    if not tail:
        return None
    t = tail.strip().lower()
    if t in ("%", "percent"):
        return "pct"
    if t == "x":
        return "mult"
    return SCALE_WORDS.get(t)


def parse_numbers(text):
    """Return a list of interpretation-sets, one per number found in text.

    Each interpretation-set is a set of candidate absolute values for that
    number (bare value, scale-word-applied value, percent-as-fraction, ...).
    """
    if not text:
        return []
    global_scale = None
    gm = GLOBAL_SCALE_RE.search(text)
    if gm:
        global_scale = SCALE_WORDS[gm.group(1).lower()]

    results = []
    for m in NUM_RE.finditer(text):
        raw = m.group("num").replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        negative = bool(m.group("neg")) or (
            bool(m.group("paren")) and bool(m.group("closeparen"))
        )
        if negative:
            value = -value

        interps = {value}
        scale = _tail_scale(m.group("tail"))
        if scale == "pct":
            interps.add(value / 100.0)
        elif scale == "mult" or scale is None:
            pass
        else:
            interps.add(value * scale)
        if global_scale:
            interps.add(value * global_scale)
        results.append(interps)
    return results


def _values_match(a, b):
    if a == b:
        return True
    denom = max(abs(a), abs(b))
    if denom == 0:
        return False
    # abs-value comparison: tolerate sign-convention flips on expenses
    return abs(abs(a) - abs(b)) / denom <= REL_TOL


def numeric_match(gold, response):
    """True if any number in the response is scale/format-equivalent to any
    number in the gold answer. Requires every gold number to be matched when
    the gold contains a single number (the common case); with multiple gold
    numbers, requires the first (primary) gold number to be matched."""
    gold_nums = parse_numbers(gold)
    if not gold_nums:
        return None  # gold is non-numeric; deterministic grading undefined
    resp_nums = parse_numbers(response)
    if not resp_nums:
        return False
    primary = gold_nums[0]
    for interps in resp_nums:
        for gv in primary:
            for rv in interps:
                if _values_match(gv, rv):
                    return True
    return False


_WS = re.compile(r"\s+")


def normalize(s):
    s = (s or "").strip().lower()
    s = _WS.sub(" ", s)
    return s.rstrip(".")


def naive_em(gold, response):
    return normalize(gold) == normalize(response)
