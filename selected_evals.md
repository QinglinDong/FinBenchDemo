# P1 — The Finance Benchmark Landscape, and Two Evals Sampled for Deep Study

*The landscape map below was compiled across two survey passes (one in a parallel Claude session, one here); every load-bearing fact was re-verified on 2026-08-04 against primary sources — papers, HuggingFace dataset APIs, downloaded parquet files, and live leaderboards. Where a verified fact contradicts a source's own claim, we say so.*

**How to read this file.** The bulk of it is a map: what public finance evals exist, organized by the practitioner work they simulate. At the end we pick **two** — FinanceQA and PRBench-Finance — to take forward into P2–P4. That choice is a *sampling* decision (which instruments are most productive to study and improve inside a 24-hour budget), not a ranking; most evals here are good measurements of *something*, and the per-eval notes try to say what.

## What "a good eval" means here

An eval is a measurement instrument, and instrument quality is relative to a question. Ours is the practitioner question: *does this benchmark measure work a finance professional actually does, in a way we can trust and reproduce?* That decomposes into five properties: (1) **task validity** — items resemble practitioner work, not a proxy like exam recall; (2) **grader trustworthiness** — the score means what it claims, with known error against human judgment; (3) **headroom** — frontier models don't saturate it; (4) **reproducibility** — public data plus a runnable harness; (5) **contamination status** — we know how long the answer key has been public. No public finance eval has all five; the notes below flag which each one trades away.

## Axes of comparison

- **Practitioner task type** — the job simulated: disclosure QA, analyst hand-spreading, open-ended advice, procedural rule-following, spreadsheet modeling, agentic retrieval, exam knowledge.
- **Item authorship** — practitioner-authored, crowdsourced, forum-scraped, or synthetic. Predicts whether "correct" means what a professional means by it.
- **Grader type** — deterministic exact/program match, line-by-line structured comparison, human binary judgment, or rubric + LLM judge. Each has a characteristic failure mode: format confounds, label noise, irreproducibility, judge bias.
- **Difficulty headroom** — best current frontier score; below ~60% still separates models, above ~95% is a regression test.
- **Contamination exposure** — how long gold answers have been downloadable, and whether the eval set equals the public set.
- **Reproducibility cost** — cheap public harness vs. private data, manual grading, or an agentic tool stack that confounds model with scaffold.

## The landscape in one table

Rows are every eval surveyed; columns are the comparison axes. Two columns use controlled vocabularies so the table sorts cleanly — **Authorship**: `experts` (practitioner/SME-written), `crowdsourced`, `derived` (built from another dataset), `forum-scraped`, `researchers`, `synthetic` (template-generated), `vendor-internal`, `exam-vendor`; **Grader**: `deterministic` (exact/program/field/cell match), `rubric+judge` (expert rubric scored by an LLM), `human` (manual, unpublished process), `judge-vs-gold` (LLM judge against a gold answer), `mixed`. Full per-eval facts and the raw data are in [`benchmarks/`](benchmarks/README.md); reasons for each cut are in the rejected list below.

| # | Eval | Year | Task type | Scenario coverage | Size | Authorship | Grader | Best frontier score | Fully public? | Taken forward |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FinQA | 2021 | Disclosure numeric QA | S&P 500 earnings reports, FY1999–2019 | 8,281 | experts | deterministic | saturating; labels noisy | yes (+ answers since 2021) | no |
| 2 | TAT-QA | 2021 | Hybrid table+text QA | 2,757 report snippets, mixed issuers | 16,552 q | crowdsourced | deterministic | — | yes | no |
| 3 | ConvFinQA | 2022 | Disclosure QA, multi-turn | Same corpus, simulated dialogues | 14,115 q | derived | deterministic | — | yes | no |
| 4 | CFA mock suites | 2023–25 | Credential exams | CFA Levels I–III mock questions | 980 q (latest) | exam-vendor | deterministic (MCQ) | **97.6% — saturated** | mixed | no |
| 5 | FinanceBench | 2023 | Open-book filing QA | US public filings (10-K/10-Q/8-K), 40 companies | 10,231 (150 public) | experts | human | 81% wrong-or-refused (GPT-4T+RAG) | no | no |
| 6 | DocFinQA | 2024 | Long-context numeric QA | Full filings (~123k words/item) | 7,437 | derived | deterministic | — | yes | no |
| 7 | SpreadsheetBench v1 | 2024 | Excel formula edits | Atomic single-cell/formula tasks | 912 q | forum-scraped | deterministic | — | yes | no |
| 8 | **FinanceQA** | **2025** | Analyst hand-spreading | **1 issuer** (Costco FY2024 10-K) + context-free concept qs | 148 | experts | human (**no grader code**) | o3 54.1% | yes (answers incl.) | **yes — P2 target** |
| 9 | FinanceReasoning / FinChain / Fino1 | 2025 | Academic reasoning chains | Numeric finance problems / 58 synthetic topics | 2,238 / synthetic / suite | researchers, synthetic | deterministic | 89.1% | yes | no |
| 10 | FinSearchComp | 2025 | Agentic financial search | Time-sensitive + historical search, global + Greater China | 635 q | experts | mixed | — | yes | no |
| 11 | **PRBench-Finance** | **2025** | Open-ended professional advice | 13 practitioner topics: corp fin, cross-border tax, risk, markets, wealth | 600 (+300 hard) | experts | rubric+judge (κ=0.603) | ≈0.55 | yes | **yes** |
| 12 | PRBench-Legal | 2025 | Professional advice | Legal practice (contrast domain) | 500 | experts | rubric+judge | 0.37 (hard) | yes | no (wrong domain) |
| 13 | RuleArena | 2025 | Rule-following | Tax as 1 of 3 generic rule scenarios | 816 problems | researchers | deterministic | — | yes | no |
| 14 | TaxCalcBench v1/v2 | 2025/26 | Tax-return preparation | US individual returns, TY24 federal + TY25 states, PDF inputs | 51 + 50 returns | vendor-internal | deterministic (line-by-line) | <⅓ strict correct | yes | near-miss |
| 15 | Vals Finance Agent v1/v2 | 2025/26 | Agentic filing research | Recent SEC filings, 9 task categories, tool stack; v2 is a 927-q rebuild, dataset non-public | 537 (v1) / 927 (v2) | experts | judge-vs-gold (v2: jury) | 58.6% (Opus 5, v2 board 2026-08) | partially (harness MIT; v2 items private) | no |
| 16 | BigFinanceBench | 2026 | Open-ended research tasks | Financial-research questions across issuers | 928 (50 public) | experts | rubric+judge | 58.8% | no | no |
| 17 | BlueFin | 2026 | Financial spreadsheet agent | Build/modify/comprehend financial workbooks | 131 tasks | researchers | rubric+judge (α=0.826) | <50% | yes | no |
| 18 | FinRetrieval | 2026 | Agentic data retrieval | Single-number lookups, 6 statement categories, global issuers | 500 q | vendor-internal | deterministic | 90.8% w/ vendor MCP | yes | no |
| 19 | Rivet TaxBench | 2026 | Professional tax work | 250+ real client scenarios, CPA-validated | 500+ prompts | vendor-internal | deterministic (pass@1 & pass^5) | <50% pass^5 everywhere | **no** | no |
| 20 | SpreadsheetBench 2 | 2026 | Workflow-level modeling | Real filings → multi-sheet models (avg 11.8 sheets) | 321 tasks | experts | deterministic (via agent scaffold) | — | yes | near-miss |
| 21 | τ³-Banking (τ-Knowledge) | 2026 | Agentic banking customer service | Retail-banking support over a 698-doc knowledge base; tools discovered from prose (dispute → freeze card → provisional credit chains) | 97 tasks | researchers | deterministic (DB-state; pass^k) | 25.5% pass¹ (paper, Mar 2026) | yes (CC-BY-4.0, tau2-bench dev/tau3 branch) | no |

### Cross-cutting instruments that don't fit a cluster

- **[FailSafeQA](https://arxiv.org/abs/2502.06329)** (2025) — perturbation-robustness probe (misspelled/incomplete/OCR-degraded finance queries): measures *reliability under messy input*, a dimension every cluster above ignores.
- **Consistency measurement** — pass^k is reported by Rivet's private TaxBench (pass^5) and, publicly, by the τ-bench family including τ³-Banking (pass^k, k≤4). No *analyst-workflow* eval measures whether a model gives the same answer five times, despite TaxCalcBench's documented run-to-run inconsistency — still a hole for the clusters this survey centers on.

## Use cases with no public benchmark coverage

Reading the map against the actual range of finance work, the gaps are as informative as the coverage. The pattern behind them: **the work products are long-form and internal, the data is confidential, and expert grading is expensive — and the firms that hold the data increasingly monetize evals as product marketing (Rivet, Daloopa, Vals) rather than release them.** Concretely, no public benchmark today measures:

1. **Deal-document drafting** — CIMs, S-1/prospectus sections, fairness-opinion support, credit-agreement drafting. Vals CorpFin reads credit agreements (comprehension); nothing grades *producing* deal documents.
2. **The long-horizon investment memo** — synthesizing a full data room into a thesis with valuation, risks, and a recommendation. Everything public is question-shaped; nothing grades a memo end-to-end. (BigFinanceBench's research tasks are the closest approach and remain single-question.)
3. **Audit and controls** — SOX walkthroughs, controls testing, tie-outs, workpaper review. Zero public coverage despite being among the most rule-bound (and therefore most gradeable) work in the domain.
4. **Insurance underwriting and actuarial work** — reserving, pricing, experience studies. Zero public coverage.
5. **FP&A** — budget variance analysis, rolling forecasts, driver-based planning. Zero public coverage; the blocker is that the inputs are inherently internal, which points to a synthetic-company construction (the TaxCalcBench recipe, applied to management accounting).
6. **Credit and fixed-income analysis** — covenant-compliance computation, downside cases, bond math beyond exam questions. Thin: only Vals' commercial CorpFin leaderboard touches it.
7. **Regulatory-filing and compliance workflows** — preparing filings, reviewing marketing material against advertising rules, monitoring. RuleArena gestures at the shape; nothing does the workflow.
8. **Measurement dimensions, not tasks**: answer consistency (pass^k), calibrated refusal when data is missing (FailSafeQA aside), multi-turn correction acceptance, and cost-normalized scoring are all absent from the public clusters above.

## The two evals we take forward

We sample two for deep study in P2–P4. Criteria for the *sample* (not a quality ranking): fully public data, tractable to run within budget, unsaturated, practitioner-authored — and flawed in ways that are measurable and fixable, because P2 is about improving an instrument. The pair deliberately brackets the two grading regimes in the landscape: verifiable short answers (FinanceQA) vs. rubric-judged open responses (PRBench), so whatever we learn about one grader style has a contrast case.

### FinanceQA (AfterQuery, 2025)

**(a) What it is.** FinanceQA ([arXiv:2501.18062](https://arxiv.org/abs/2501.18062), Jan 2025) is a 148-item benchmark of the questions a junior analyst gets asked when hand-spreading a company: 84 *tactical* questions computed from a real 10-K — 38 *basic* (derivable from the provided excerpt) and 46 *assumption-based* (context deliberately incomplete; the model must make the standard analyst assumption, e.g. adding back operating-lease costs for adjusted EBITDA) — plus 64 *conceptual* questions with no context (accounting and valuation logic). Every tactical item comes from one document: Costco's FY2024 10-K. Items were written without LLM assistance by annotators with hedge fund / PE / IB experience. Paper grading is **human, binary, exact-match** ("no partial points"); no grader code was ever published — the GitHub repo holds a README and a PDF. Data: [`AfterQuery/FinanceQA`](https://huggingface.co/datasets/AfterQuery/FinanceQA) on HF, Apache-2.0, gold answers and chain-of-thought rationales fully public. Headline: o1 scored 48.7%; **every release-time model scored under 5% on assumption questions** (best: 2/46). Current leaderboard top: o3 at 54.1%.

**(b) Why this one gets the deep-dive slot.** It isolates the layer cluster 1 skips — what an analyst does when the filing *doesn't* hand you the number — and the 40-point spread between basic (~45%) and assumption (<5%) questions inside one dataset is the most diagnostic single number in the public landscape. Practically: it is small, self-contained, and cheap, and its measurement risks are tractable to engage in P2. We verified that the public 148 rows **are** the paper's eval set (reported percentages reconcile exactly: 0.022 = 1/46), that the answer key has been downloadable since Jan 2025, and that anyone running it today must improvise a grader against answer strings like `"$32,095 (in millions)"` under a "provide a concise answer" prompt. (These observations are our own, from primary data; we found no published critique of FinanceQA.)

**(c) What it actually measures, in one sentence.** FinanceQA is a good measurement of whether a model makes the standard analyst assumptions when the context is deliberately incomplete — but only for one company's 10-K, and only up to the noise of an unpublished exact-match grading process.

### PRBench-Finance (Scale AI, 2025)

**(a) What it is.** PRBench ([arXiv:2511.11562](https://arxiv.org/abs/2511.11562), Nov 2025; ACL 2026) evaluates open-ended professional reasoning against expert rubrics. The finance split: 600 conversations (plus a 300-item `finance_hard` strict subset) across 13 practitioner topics — Corporate Finance (93) and cross-border tax structuring (85) largest — authored by 182 professionals *across finance and legal combined* (per-domain counts unpublished; Scale's leaderboard phrasing suggests finance-only, which the paper doesn't support). Items are workplace-register prompts with real stakes recorded in an `economic_pathway` field (e.g. a CCAR credit-loss model underestimating tail losses by 15–20%, submission due in six weeks). Rubrics: we measured 7–30 criteria per item, mean 16.4, 9,865 finance criteria (paper and GitHub claim 19,356 across both domains; the released files contain 18,692), each weighted −10…+10 including *negative* criteria for actively harmful advice ("recommends cutting maintenance capex first": −7). Grading: an o4-mini judge scores each criterion independently; weighted, clipped to [0,1]. Validation: experts endorse criteria 93.9% of the time; judge–expert Cohen's κ = 0.603, macro-F1 = 0.802 (the often-quoted "80.2% agreement" is the F1, not raw agreement). Fully public: [`ScaleAI/PRBench`](https://huggingface.co/datasets/ScaleAI/PRBench) (CC-BY-4.0) + MIT harness ([scaleapi/PRBench](https://github.com/scaleapi/PRBench)). Paper-time finance best ≈0.51; live leaderboard ≈0.55.

**(b) Why this one gets the deep-dive slot.** It is the only public instrument for the *advice* half of finance work — where the deliverable is a recommendation with caveats, process, and regulatory hooks — and the only rubric-judged finance eval whose full data and harness are open enough to study the grader itself. Its documented weaknesses are productive ones: κ = 0.603 is moderate for an instrument whose entire score is judge-produced; the Hard subset is defined post hoc by which items the paper's 20 models failed, so its meaning drifts as models improve; and per-criterion independent judging of up to 30 criteria invites verbosity-reward gaming. BigFinanceBench shares the philosophy but exposes only 50 items.

**(c) What it actually measures, in one sentence.** PRBench-Finance is a good measurement of whether a model's open-ended professional answer *covers what a domain expert would insist it cover* — coverage of expert-salient points as scored by a mid-tier LLM judge, which is related to, but not identical with, giving correct advice.

### Why these two together, and the closest alternatives

FinanceQA's measurement risk is *format confounds and grading noise* on verifiable answers; PRBench's is *judge validity and rubric gaming* on open-ended ones. Both are practitioner-authored, unsaturated (≈54% / ≈55%), and fully downloadable. The closest alternatives for the slot were **TaxCalcBench** (the only fully deterministic grader with real headroom — passed over because its grader, the thing we'd want to improve elsewhere, is already its best feature, and tax prep sits farther from the analyst workflows we probe) and **SpreadsheetBench 2** (closest to IB modeling reality — passed over because it needs a multi-turn agent scaffold plus an Excel execution environment, out of scope for a 24-hour budget, and improvements would target the scaffold as much as the eval).

### Considered and rejected, one line each

Fuller context for every entry is in the cluster tables above; this is the explicit cut list. "Rejected" means *not taken forward for deep study* — a fit judgment against the five properties and the 24-hour budget, not a quality verdict.

| Eval | One-line reason not taken forward |
|---|---|
| FinQA / ConvFinQA | Answers public since 2021–22 (contaminated), label noise evidenced by Aiera's 91-item verified subset, and they measure table arithmetic, not analyst judgment. |
| TAT-QA | Crowdsourced questions, not practitioner work. |
| FinanceBench | Only 150/10,231 items public; the headline measures a retrieval system + model jointly; manual grading isn't reproducible. |
| DocFinQA | Long-context stressor that inherits FinQA's labels and adds a needle-finding confound. |
| FinRetrieval | Narrow (single-number retrieval) and partly a vendor demo for Daloopa's MCP. |
| TaxCalcBench | Closest call on the deterministic-grader axis — but its grader is already its best feature, and tax prep sits farther from the analyst workflows we probe. |
| RuleArena / Rivet TaxBench | Tax as a generic rule-following scenario / not public (vendor-reported numbers only). |
| SpreadsheetBench v1 | Forum-sourced atomic formula edits — the unit of work is a cell. |
| SpreadsheetBench 2 | Closest to IB modeling reality, but needs an agent scaffold + Excel execution environment — out of a 24-hour budget. |
| BlueFin | Young, small, agent-scaffold-dependent, no clear owning institution. |
| CFA mock suites | Saturated (97.6% on L1); exams measure credential recall, not work product. |
| FinanceReasoning / FinChain / Fino1 | Academic reasoning-chain benchmarks; FinChain is synthetic; low task validity. |
| Vals Finance Agent v1/v2 | Practitioner-authored but confounds model with a web-search/EDGAR tool stack; v2's 927 items are not publicly downloadable. |
| τ³-Banking (τ-Knowledge) | Excellent instrument design (deterministic DB-state grading, pass^k, open CC-BY-4.0) — but it measures banking *customer service* conversations, not analyst work; the design ideas feed our P5 brief, the task domain doesn't fit. |
| BigFinanceBench | Strongest rejected candidate — rubric-grades the derivation — but only 50 of 928 items are public, so its grader can't be studied from outside. |
| FinSearchComp | Measures search execution more than financial reasoning. |
| PRBench-Legal | Same instrument as our pick, wrong profession. |

## Sources

Primary sources linked inline. Key verification artifacts: HF dataset-viewer API row/statistics dumps for `AfterQuery/FinanceQA` (schema, per-category counts, example rows); downloaded `ScaleAI/PRBench` parquet files (split sizes, rubric counts and weights measured directly); live leaderboard reads (AfterQuery, Scale Labs, Vals AI) on 2026-08-04.
