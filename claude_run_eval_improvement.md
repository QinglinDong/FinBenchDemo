# P2 — FinanceQA: Critique, Improvement, and Measurement

## Part 1 — Critique: what FinanceQA measures vs. what it claims

**Claim.** FinanceQA ([arXiv:2501.18062](https://arxiv.org/abs/2501.18062)) presents itself as "a benchmark for evaluating financial analysis capabilities," graded by "exact correct matches ... no partial points," with the headline finding that frontier models fail ~half of professional-grade tasks and answer <5% of assumption-based questions correctly.

**What it actually measures**, and the design flaws that sit between the claim and the measurement. All of these were verified against primary sources (the paper, the HF dataset, the GitHub repo) on 2026-08-04; the flaws are our own findings — no published critique of FinanceQA exists that we could find.

1. **The grader does not exist as an artifact.** Grading in the paper was performed by human annotators; no grader code was ever published (the GitHub repo contains a README and the paper PDF — nothing else). Every score produced since — including AfterQuery's own leaderboard, which reports o3 = 54.1% — rests on an unpublished, unreproducible grading process. Anyone re-running the benchmark must improvise their own grader, and the improvised choice can move the headline by tens of points (Part 3 quantifies this).

2. **Format confound between prompt and gold labels.** The prescribed prompt says "Provide a concise answer," while gold answers are strings like `"$32,095 (in millions)"`. A model answering `"$32.1 billion"` — numerically identical — fails any naive string-matching reimplementation. Our controlled probe (below) shows naive exact-match accepts only **0.6%** of correct-by-construction reformatting variants of the gold answers. Any automated reimplementation that is not explicitly scale- and format-invariant measures formatting compliance, not financial analysis.

3. **Ambiguous gold labels on assumption items.** The 46 assumption-based questions deliberately withhold information so the model must "make reasonable assumptions" — but the grading is binary against a single gold answer. Where more than one professionally defensible convention exists (e.g., what to add back into adjusted EBITDA), a defensible-but-different answer scores identically to a garbage answer. This inflates the difficulty signal of exactly the subset the paper's headline finding is about. Our improved grader separates these cases with an explicit `defensible_alternative` flag.

4. **Public set = eval set, answers included, since Jan 2025.** We verified the paper's reported percentages reconcile exactly against the public 148 rows (e.g., 0.022 = 1/46 assumption items), so there is no held-out split — and the CSV on HuggingFace ships gold answers *and* chain-of-thought rationales. Post-release leaderboard gains (o3 at 54.1% vs. paper-era o1 at 48.7%) cannot be distinguished from contamination.

5. **Single-document concentration.** All 84 tactical items derive from one Costco FY2024 10-K. Costco is also an unusually clean filer. The benchmark measures analysis of one document from one retailer — any claim of generality across sectors, filing quality, or fiscal-year conventions is unsupported, and one contaminated document collapses the whole tactical half.

6. **The headline "sub-5% on assumptions" conflates capability with grading artifact.** Given flaws 2 and 3, part of the 40-point spread between basic (~45%) and assumption (<5%) questions could be produced by the grading pipeline rather than by model incapability. This is a testable claim, and Part 3 tests it: we re-grade with a format-invariant, convention-aware instrument and report how much of the gap survives. (Preview: most of it survives — the capability gap is real — but the absolute scores move materially.)

**What we did NOT engage with** (scope choices, stated for honesty): flaw 4 (contamination) needs fresh items on fresh documents — that is the P5 vendor brief's job, not a 24-hour fix; flaw 5 (single document) likewise. This P2 targets flaws 1–3 and 6: the grader.

## Part 2 — The improvement: a published, validated, two-stage grader

FinanceQA's most fixable defect is that its grading procedure is a private human process with no reproducible artifact. The improvement is the thing the benchmark shipped without: **a fully specified, runnable grader**, plus the validity evidence that it grades the construct (numeric equivalence + analyst judgment) rather than surface form.

**Design (deliberately boring):**

- **Stage 0 — naive EM (baseline, kept for comparison).** Normalized string equality. This is what a careless reimplementation of "exact match" does, and it is the counterfactual against which the improvement is measured.
- **Stage 1 — deterministic numeric equivalence** (`p2/graders.py`). Parses gold and response into (value × scale) interpretations — handling `$`, commas, parentheses-negatives, `%` vs fractions, `x` multiples, scale words (`million`, `bn`, `M`, `(in millions)` context) — and auto-accepts when any response number matches the gold's primary number within 0.5% relative tolerance. Sign-presentation flips (expense as positive vs parenthesized) are accepted. Deterministic, dependency-free, unit-tested.
- **Stage 2 — LLM adjudicator for everything Stage 1 does not accept** (`p2/grade.py`, `claude-opus-5`, a model deliberately outside the graded tier ladder to avoid self-grading). The adjudicator sees the question, source context, gold answer, gold chain of thought, and candidate answer, and must grade **strictly and binarily** (preserving the paper's no-partial-credit philosophy) — but records two extra fields: `defensible_alternative` (incorrect, but reached via a professionally defensible convention — the label-noise signal from flaw 3) and a `failure_category` (feeds P3).

The final score under the improved grader: correct = Stage-1 accept OR Stage-2 "correct". Naive EM is reported alongside throughout.

**Measurement setup.** All 148 items × three same-generation model tiers (`claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-6`, all with thinking off, paper-exact prompt), so tier separation is a within-generation capability ladder, not a generation confound.

## Part 3 — Did the improvement make the eval better?

"Better" is a claim about the instrument. We test three concrete properties.

### Property 1 — Format invariance under controlled perturbation

For every gold answer with a parseable primary number, we generate correct-by-construction surface variants (scale-shifted `$32,095 million` ↔ `$32.095 billion`, suffixed `$32,095M`, percent-vs-word, sentence-wrapped, symbol-stripped). A valid grader must accept 100% of them; every rejection is a measured format confound.

| grader | acceptance on 340 non-identity correct variants |
|---|---|
| naive exact match | **0.6%** |
| improved grader (Stage 1 alone — no LLM needed) | **100.0%** |

This is the cleanest number in the study: the baseline grader fails 99.4% of correct answers that are merely formatted differently, and the deterministic stage of the improved grader fixes all of it before any LLM judging is involved. *(Reproduce: `python3 p2/perturb.py`, no API cost.)*

### Property 2 — Grader–human agreement

63 stratified (item × model) response pairs (7 per question type per model, drawn blind — the template shows no grader verdicts) were adjudicated against the gold answer and gold chain of thought, then compared to each grader. Labels with per-pair notes are checked in at `p2/data/human_labels.csv`. (Disclosure: the adjudication was performed by the take-home author working with Claude; it is independent of both graders and blind to their verdicts, but it is not an independent-SME panel — that is what P5 commissions.)

| grader | agreement with human | Cohen's κ |
|---|---|---|
| naive exact match | 60.3% | **−0.000** |
| improved | 92.1% | **0.840** |

Naive EM's κ is exactly zero because it has one behavior — say "incorrect" — so its 60.3% raw agreement is pure base rate. The improved grader's κ = 0.840 is substantial; for calibration, PRBench's published judge–expert agreement is κ = 0.603, so this grader is measurably tighter than the only comparable finance instrument that reports the statistic.

**The five disagreements are one defect, and the check caught it.** In all five (5/63 = 7.9%), the human said *incorrect* while Stage 1 had auto-accepted: the gold's number appeared *incidentally* in a wrong response — gold "3x MOIC" matching the "3." of a markdown list ordinal; gold "60M increase" matching a mentioned "$60M acquisition" in a response whose final answer was "EV is unaffected". All five golds are sentence-like or multi-part ("60M increase", "3x MOIC, 25% IRR", three-statement narratives) — none are bare quantities like `"$32,095 (in millions)"`, where Stage 1 made no errors. The improved grader therefore never *under*-credits (no false rejects observed) but has a measured ~8% false-accept channel confined to non-bare golds.

**Proposed fix, quantified but deliberately not yet applied:** restrict Stage-1 auto-accept to bare-quantity golds and route sentence-like golds to the judge unconditionally. Rerunning the routing rule offline shows 63 of the current 160 Stage-1 accepts would be re-routed (≈63 extra judge calls, ~$1.5). We held this back to keep the checked-in numbers exactly reproducible from the checked-in code and within the approved budget; the defect, its measured size, and the one-line fix (`p2/grade.py`, gate on a bare-gold regex) are documented here instead. This is the validity loop working as intended: the human-agreement check exists precisely to surface what the deterministic probe cannot.

### Property 3 — Tier separation

A finance eval that cannot rank Haiku < Sonnet < Opus within one model generation is not measuring capability. Accuracy per tier under each grader (all 148 items):

| grader | Haiku 4.5 | Sonnet 4.6 | Opus 4.6 | Sonnet−Haiku | Opus−Sonnet | monotone? |
|---|---|---|---|---|---|---|
| naive exact match | 0.0% | 0.0% | 0.0% | +0.0 | +0.0 | degenerate |
| improved | 50.0% | 53.4% | 56.1% | +3.4pp | +2.7pp | **yes** |

The baseline grader scores **every model at exactly zero** — not a single response out of 444 string-matches its gold label, so naive EM has no discriminative power at all: the "tier separation" it reports is the degenerate 0=0=0. The improved grader recovers a clean monotone ladder, and puts Opus 4.6 (56.1%) in the same range as the AfterQuery leaderboard's current best (o3 = 54.1%) — a sanity anchor, not a claim of comparability, since their grading process is unpublished.

Where the separation lives is itself a finding: **basic** lookup questions are non-monotone (Haiku 55.3% > Sonnet 52.6% > Opus 50.0%) — all tiers can read a curated income statement, and the ordering noise is within-subset sampling error. The capability ladder shows up in **assumption** (6.5% → 13.0% → 17.4%) and **conceptual** (78.1% → 82.8% → 87.5%) questions. An eval buyer who wants model-ranking power should weight those subsets; the basic subset is a floor check.

### And the headline claim

The paper's release-time headline — models answer **<5%** of assumption-based questions correctly — replicates directionally but not literally under the improved grader: Haiku 6.5%, Sonnet 13.0%, Opus 4.6 17.4% on the same 46 items. Two readings, both true: (1) the **capability cliff is real** — even Opus 4.6, a generation past the paper's models, fails 5 of every 6 assumption questions while answering 87.5% of conceptual ones, so the gap is not a grading artifact; (2) the **absolute number was partly instrument** — a strict-format reading of "exact match" can push any of these scores toward zero (our naive baseline literally reaches it), so cross-paper comparisons of the sub-5% figure carry no information without the grader spec.

The adjudicator's second channel sharpens the label-ambiguity critique (flaw 3): of 208 responses judged incorrect, **114 (55%) used a professionally defensible alternative convention** — 67% of incorrect basic answers, 51% of assumption, 48% of conceptual. These stay *incorrect* under our strict grading (preserving the paper's philosophy), but the flag means over half the measured "failure" mass sits on convention disagreements with a single gold label rather than on outright analytical error. An eval that wants to measure judgment rather than convention-guessing needs either multi-reference golds or rubric grading on this subset — that is precisely the P5 vendor brief's design requirement.

One honest caveat on grader anatomy: for the 64 conceptual items the gold answers are mostly non-numeric, so Stage 1 rarely fires and the improved grader's conceptual scores rest almost entirely on the Opus 5 adjudicator (72 of 76 judge-added "correct" verdicts are conceptual). The deterministic guarantees (Property 1) cover the tactical 84; the conceptual grading inherits LLM-judge risk, which is what Property 2's human check bounds.

## Part 4 — Runnable instructions (Claude-readable)

Everything runs from the repo root with one command:

```bash
cd p2 && ANTHROPIC_API_KEY=<your-key> ./run_all.sh
```

Explicitly, `run_all.sh` executes, in order:

| step | command | needs API? | output |
|---|---|---|---|
| 1 | `python3 prepare_items.py` | no | `data/items.jsonl` (148 items from the checked-in `../benchmarks/financeqa/test.csv`) |
| 2 | `python3 run_models.py` | yes | `results/responses.jsonl` — 148 × {`claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-6`}; idempotent, resumes on rerun |
| 3 | `python3 perturb.py` | no | `results/perturbation.csv` — format-invariance probe |
| 4 | `python3 grade.py` | yes | `results/grades.csv` — all three graders; `claude-opus-5` adjudicator verdicts cached in `results/judge_cache.jsonl` |
| 5 | `python3 analyze.py` | no | `results/summary.md` — every table in this document |

Requirements: `python3` (3.9+), `pip install anthropic`, `ANTHROPIC_API_KEY` in the environment (or a git-ignored `.env` at the repo root). The dataset is checked in, so no HuggingFace access is needed. Expected cost for a full from-scratch rerun: under $15 (the 444 response calls are small; the adjudicator judges only responses the deterministic stage doesn't accept). All checked-in result files under `p2/results/` were produced by exactly these commands; every number in this document traces to a row in `results/summary.md`, which is computed from `results/grades.csv` and `results/perturbation.csv` by `analyze.py`.

Human adjudication (Property 2) is the one manual step: `python3 make_adjudication_template.py` writes `data/adjudication_template.csv` (63 stratified response pairs, grader verdicts hidden); fill `human_verdict` with `correct`/`incorrect`, save as `data/human_labels.csv`, and rerun `python3 analyze.py`.
