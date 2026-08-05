# P1 — The Finance Benchmark Landscape, and Two Evals Sampled for Deep Study

*The landscape map below was compiled across two survey passes (one in a parallel Claude session, one here); every load-bearing fact was re-verified on 2026-08-04 against primary sources — papers, HuggingFace dataset APIs, downloaded parquet files, and live leaderboards. Where a verified fact contradicts a source's own claim, we say so.*

**How to read this file.** The bulk of it is a map: what public finance evals exist, organized by the practitioner work they simulate. At the end we pick **two** — FinanceQA and PRBench-Finance — to take forward into P2–P4. That choice is a *sampling* decision (which instruments are most productive to study and improve inside a 24-hour budget), not a ranking; most evals here are good measurements of *something*, and the per-eval notes try to say what.

## Benchmark selection criteria

An eval is a measurement instrument, and instrument quality is relative to a question. Ours is the practitioner question: *does this benchmark measure work a finance professional actually does, in a way we can trust and reproduce?* We screened every candidate against six criteria:

| # | Criterion | The question it asks | Failure looks like | Example from this survey |
|---|---|---|---|---|
| C1 | Task validity | Do items resemble work a practitioner actually does? | Exam recall, crowdsourced lookup | CFA mocks (saturated credential recall); TAT-QA (crowdsourced) |
| C2 | Gold-label quality | Are golds unambiguous, noise-checked, and convention-complete? | Single gold where professionals legitimately disagree | FinQA (Aiera could re-verify only 91 items); FinanceQA (our P2: 55% of "wrong" answers used a defensible alternative convention) |
| C3 | Grader quality | Is the grading mechanism published, and how close is it to human judgment? | Unpublished manual process; unvalidated LLM judge | FinanceQA (no grader code ever shipped); PRBench (judge κ = 0.603) |
| C4 | Headroom & discrimination | Does it still separate frontier tiers? | Ceiling effects; flat tier ladders | CFA at 97.6%; our naive-EM baseline scoring every tier 0 = 0 = 0 |
| C5 | Public | Are the items, golds, and harness public enough to rerun and re-grade? | Private items; harness-only releases | FinanceBench (150 of 10,231); Rivet TaxBench (nothing) |
| C6 | Freshness | How exposed is the answer key, and does the item set get refreshed? | Answers on HF for years; eval set = public set; dead repo | FinQA (answers public since 2021); FinanceQA (answers + CoT public since 2025-01); positive case: TaxCalcBench's annual tax-year refresh |

No public finance eval passes all six; the landscape table carries these criteria as columns C1–C6 so the trade-offs are visible per row. For *selection* (which eval rewards deep study), a candidate needed high marks on C1 and C5 and *fixable* failures in between — a flaw you can measure and repair is an asset for P2, not a defect.

### Beyond criteria

Five more properties are legitimate quality criteria for finance evals. **None of them were used to screen candidates in this demo** — the first two were deliberately excluded (agentic scaffolds are part of the capability being measured, and coverage is a scale property that the P5 extension buys rather than a quality gate), the other three are certification-grade concerns out of scope for a selection rubric; screening on 9–10 would have emptied today's candidate pool entirely. (An earlier "maintenance cadence" candidate is now folded into C6 freshness.)

| # | Criterion (not used here) | The question it asks | Failure looks like | Example from this survey |
|---|---|---|---|---|
| 7 | Construct isolation | Does the score measure the model — or the scaffold around it? | Results that don't transfer across harnesses | FinanceBench's 81% is tied to one RAG configuration; Vals FA scores are harness-specific |
| 8 | Coverage / representativeness | How much of the scenario space does the item sample span? | One issuer generalized to "finance" | FinanceQA: all 84 tactical items from a single Costco 10-K |
| 9 | Statistical power | Is n large enough for the score to mean anything? | ±10pp confidence intervals read as model differences | FinanceQA's assumption subset is n=46 → roughly ±10pp binomial noise at 95% |
| 10 | Run-to-run consistency | Is the score stable across repeated runs? | pass@1 ≫ pass^k collapse | Rivet TaxBench drops 40–50pp from pass@1 to pass^5; only the τ-bench family reports pass^k publicly |
| 11 | Cost-to-run | What does one full evaluation cost? | Too expensive to iterate on | Vals FA v1 at ≈$3.79/query |

## Axes of comparison

- **Domain / Task (`D×` / `T×`)** — a coded two-level hierarchy of finance work, defined in the Finance Task Hierarchy table below; landscape rows and coverage gaps use the same codes.
- **Input format** — what the model receives: `table+text excerpt` / `full filing` / `xlsx workbook` / `structured JSON` / `PDF forms` / `conversational prompts` / `tool harness` / `KB + tools` / `MCQ + essay` / `text problems`.
- **Item authorship** — `experts` / `crowdsourced` / `derived` / `forum-scraped` / `researchers` / `synthetic` / `vendor-internal` / `exam-vendor`.
- **Grader type** (a property, not a quality judgment) — `deterministic` / `rubric+judge` / `judge-vs-gold` / `human` / `mixed`.
- **Criteria ratings** — C1 `high/med/low`; C2 `clean/validated/noisy/inherited/ambiguous/crowd/private`; C3 `high/med/low/unknown` (deterministic ⇒ high; judge rated by published agreement; unpublished ⇒ low/unknown); C4 remaining headroom `none/low/med/high/unknown` with best score; C5 `yes/partial/no`; C6 `high/med/low` freshness with the exposure evidence.

### Finance Task Hierarchy

`†` = no public benchmark coverage (detailed in the gap table below).

| Code | Domain | Tasks |
|---|---|---|
| D1 | Research & analysis | T1 disclosure QA · T2 filing QA · T3 agentic research & search · T4 data retrieval · T5 hand-spreading |
| D2 | Modeling (Excel) | T1 formula edits · T2 workflow modeling · T3 build/modify agent |
| D3 | Advisory | T1 financial advice · T2 legal advice |
| D4 | Tax & compliance | T1 return preparation · T2 professional tax workflows · T3 rule-following · T4 regulatory-filing workflows † |
| D5 | Deals (IB) | T1 deal-document drafting † |
| D6 | Buy-side investment management | T1 investment memo † · T2 PE / LBO review † |
| D7 | Corporate finance | T1 FP&A † |
| D8 | Audit & controls | T1 SOX walkthroughs & tie-outs † |
| D9 | Insurance | T1 underwriting & actuarial † |
| D10 | Credit & fixed income | T1 covenant & bond analytics † |
| D11 | Banking ops | T1 retail customer support |
| D12 | Academic & exams | T1 exam prep · T2 numeric reasoning |

## Benchmark Landscape

One row per surveyed eval, sorted by year. Columns are grouped: **eval properties** (Eval → Grader type), then the **six selection criteria C1–C6** numbered to match the criteria table, then the verdict. All values use the controlled vocabularies defined in the axes above. Full per-eval facts and raw data: [`benchmarks/`](benchmarks/README.md); the final column carries the one-line reason each eval was or wasn't taken forward.

| # | Eval | Year | Domain | Task | Input format | Size | Authorship | Grader type | C1 Task validity | C2 Gold quality | C3 Grader quality | C4 Headroom | C5 Public | C6 Freshness | Taken forward | Why to skip&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FinQA | 2021 | D1 Research & analysis | T1 disclosure QA | table+text excerpt | 8,281 | experts | deterministic | med | noisy (91/8,281 re-verified) | high (deterministic) | low (saturating) | yes | low (answers public since 2021) | no | C6: answers public since 2021; C2: noisy labels (91/8,281 re-verified); C1: tests arithmetic, not judgment |
| 2 | TAT-QA | 2021 | D1 Research & analysis | T1 disclosure QA | table+text excerpt | 16,552 q | crowdsourced | deterministic | low | crowd | high (deterministic) | unknown | yes | low (public since 2021) | no | C1: crowdsourced lookup, not practitioner work |
| 3 | ConvFinQA | 2022 | D1 Research & analysis | T1 disclosure QA (multi-turn) | table+text excerpt | 14,115 q | derived | deterministic | med | inherited (FinQA) | high (deterministic) | unknown | yes | low (public since 2022) | no | C2 + C6: inherits FinQA's labels and its contamination |
| 4 | CFA mock suites | 2023–25 | D12 Academic & exams | T1 exam prep | MCQ + essay | 980 q | exam-vendor | deterministic | low | clean (answer key) | high (deterministic) | none (97.6%) | partial (mixed) | low (prep-bank items) | no | C4: saturated at 97.6%; C1: credential recall, not a work product |
| 5 | FinanceBench | 2023 | D1 Research & analysis | T2 filing QA (open-book, 40 issuers) | full filing | 10,231 (150 public) | experts | human | med | clean (evidence-linked) | low (manual, unpublished) | high (81% wrong, one RAG config) | partial (150/10,231) | med (2023; bulk private) | no | C5: only 150/10,231 public; C3: manual grading, not reproducible as shipped |
| 6 | DocFinQA | 2024 | D1 Research & analysis | T2 filing QA (long-context) | full filing (~123k words) | 7,437 | derived | deterministic | med | inherited (FinQA) | high (deterministic) | unknown | yes | low (inherits FinQA) | no | C2: inherits FinQA labels; adds a needle-finding confound on top |
| 7 | SpreadsheetBench v1 | 2024 | D2 Modeling | T1 formula edits | xlsx workbook | 912 q | forum-scraped | deterministic | med | clean (execution-checkable) | high (deterministic) | unknown | yes | med (2024 forum items) | no | C1: atomic cell edits — the unit of work is a formula, not a model |
| 8 | **FinanceQA** | **2025** | D1 Research & analysis | T5 hand-spreading (1 issuer: Costco) | table+text excerpt (or none) | 148 | experts | human | **high** | ambiguous (P2: 55% defensible-alt) | low (**no grader code**) | med (o3 54.1%) | yes (Apache-2.0, answers incl.) | low (answers+CoT public 2025-01; eval set = public set) | **yes** | **P2 target** — C1 high (the judgment layer) with *fixable* C2/C3 flaws, and cheap to run |
| 9 | FinanceReasoning / FinChain / Fino1 | 2025 | D12 Academic & exams | T2 numeric reasoning | text problems | 2,238 / synthetic | researchers, synthetic | deterministic | low | clean (credibility-checked) | high (deterministic) | low (89.1%) | yes | med (2025) | no | C1: academic reasoning chains; low task validity for practitioner work |
| 10 | FinSearchComp | 2025 | D1 Research & analysis | T3 agentic search (global + Greater China) | tool harness | 635 q | experts | mixed | med | clean (expert-checked) | unknown (mixed) | unknown | yes | high (time-sensitive by design) | no | C1: measures search execution more than financial reasoning |
| 11 | **PRBench-Finance** | **2025** | D3 Advisory | T1 financial advice (13 topics) | conversational prompts (1–10 turns) | 600 (+300 hard) | experts | rubric+judge | **high** | validated (93.9% expert-justified) | med (judge κ=0.603) | high (≈0.55) | yes (CC-BY-4.0 + MIT harness) | med (2025-11 release) | **yes** | C1 high + C5 fully open — the only public advice eval whose judge (C3) can be studied and improved from outside |
| 12 | PRBench-Legal | 2025 | D3 Advisory | T2 legal advice | conversational prompts | 500 | experts | rubric+judge | high | validated | med (judge κ) | high (0.37 hard) | yes | med (2025-11) | no | C1 high, but wrong profession for this survey |
| 13 | RuleArena | 2025 | D4 Tax & compliance | T3 rule-following (tax is 1 of 3) | rules + scenario text | 816 problems | researchers | deterministic | low | clean (rule-derived) | high (deterministic) | unknown | yes | med (2025) | no | C1: generic rule-following; tax is incidental to the design |
| 14 | TaxCalcBench v1/v2 | 2025/26 | D4 Tax & compliance | T1 return preparation (federal + state) | structured JSON / PDF forms | 51 + 50 returns | vendor-internal | deterministic | high | clean (engine-derived XML) | high (deterministic, line-by-line) | high (<⅓ strict) | yes (MIT) | high (annual tax-year refresh) | no | Closest call — C3 (deterministic grader) is already its best feature, nothing for P2 to fix; C1 sits off our analyst focus |
| 15 | Vals Finance Agent v1/v2 | 2025/26 | D1 Research & analysis | T3 agentic filing research (9 categories) | tool harness (EDGAR + web) | 537 (v1) / 927 (v2) | experts | judge-vs-gold | high | private (unverifiable) | unknown (v2 jury, no public κ) | med (58.6%, v2 board 2026-08) | partial (harness MIT; items private) | high (held-out split, refreshed) | no | C5: v2's 927 items are private on a commercial leaderboard — nothing to re-grade |
| 16 | BigFinanceBench | 2026 | D1 Research & analysis | T3 open-ended research | tool harness | 928 (50 public) | experts | rubric+judge | high | clean (expert rubrics, 36,241 pts) | unknown (no public κ) | med (58.8%) | partial (50/928) | high (2026 + canary) | no | C5: only 50/928 public, so its C3 judge can't be studied from outside |
| 17 | BlueFin | 2026 | D2 Modeling | T3 spreadsheet build/modify agent | xlsx workbook | 131 tasks | researchers | rubric+judge | high | clean (expert rubrics) | med (judge α=0.826) | high (<50%) | yes | high (2026) | no | Young and small (n=131 → beyond-criterion 9); agent-scaffold-dependent |
| 18 | FinRetrieval | 2026 | D1 Research & analysis | T4 data retrieval (global issuers) | tool harness (MCP) | 500 q | vendor-internal | deterministic | med | clean (structured fields) | high (deterministic) | low (90.8% w/ vendor MCP) | yes (MIT) | high (2026) | no | C1: narrow single-number lookup; C4: near-saturated with vendor MCP (90.8%) |
| 19 | Rivet TaxBench | 2026 | D4 Tax & compliance | T2 professional tax workflows | conversational prompts | 500+ prompts | vendor-internal | deterministic | high | private (CPA-validated) | unknown (vendor-run) | high (<50% pass^5) | **no** | high (private, refreshed) | no | C5: not public at all — every number is vendor-reported |
| 20 | SpreadsheetBench 2 | 2026 | D2 Modeling | T2 workflow modeling (avg 11.8 sheets) | xlsx workbook (multi-sheet) | 321 tasks | experts | deterministic | high | clean (expert workbooks) | high (deterministic, via scaffold) | unknown | yes | high (2026) | no | Beyond-criterion 11 (cost-to-run): needs an Excel agent environment, outside the 24h budget |
| 21 | τ³-Banking (τ-Knowledge) | 2026 | D11 Banking ops | T1 retail customer support (698-doc KB) | KB + tools (698 docs), dialogue | 97 tasks | researchers | deterministic | high | clean (DB-state targets) | high (deterministic, pass^k) | high (25.5% pass¹, paper) | yes (CC-BY-4.0) | high (2026) | no | C1: banking customer support, not analyst work — but its C3 design (DB-state + pass^k) feeds our P5 brief |

### Cross-cutting instruments that don't fit a cluster

- **[FailSafeQA](https://arxiv.org/abs/2502.06329)** (2025) — perturbation-robustness probe (misspelled/incomplete/OCR-degraded finance queries): measures *reliability under messy input*, a dimension every cluster above ignores.
- **Consistency measurement** — pass^k is reported by Rivet's private TaxBench (pass^5) and, publicly, by the τ-bench family including τ³-Banking (pass^k, k≤4). No *analyst-workflow* eval measures whether a model gives the same answer five times, despite TaxCalcBench's documented run-to-run inconsistency — still a hole for the clusters this survey centers on.

## Use cases with no public benchmark coverage

The same hierarchy (`D× T×` codes above), continued into the branches no public benchmark reaches. The pattern behind the gaps: the work products are long-form and internal, the data is confidential, expert grading is expensive — and firms that hold the data increasingly monetize evals as product marketing (Rivet, Daloopa, Vals) rather than release them.

| Code | Domain › task | Work product | Closest public coverage |
|---|---|---|---|
| D5 T1 | Deals (IB) › deal-document drafting | CIMs, S-1/prospectus sections, fairness opinions, credit-agreement drafting | none — Vals CorpFin (commercial) *reads* credit agreements; nothing grades drafting |
| D6 T1 | Buy-side IM › data-room investment memo | Thesis + valuation + risks + recommendation, end-to-end | BigFinanceBench (#16) — question-shaped, not memo-shaped |
| D6 T2 | Buy-side IM › PE / LBO review | Model review, downside cases, QoE-style checks | SpreadsheetBench 2 (#20) — template modeling only |
| D7 T1 | Corporate finance › FP&A | Variance analysis, rolling forecasts, driver-based plans | none — inputs inherently internal; a synthetic-company build (the TaxCalcBench recipe) is the plausible route |
| D8 T1 | Audit & controls › SOX walkthroughs, tie-outs | Control tests, tie-out schedules, workpaper review | none — despite being among the most rule-bound (gradeable) work in the domain |
| D9 T1 | Insurance › underwriting & actuarial | Reserving, pricing, experience studies | none |
| D10 T1 | Credit & fixed income › covenant & bond analytics | Compliance calcs, downside cases, bond math beyond exams | thin — Vals CorpFin (commercial leaderboard only) |
| D4 T4 | Tax & compliance › regulatory-filing workflows | Filing prep, marketing-material compliance review, monitoring | RuleArena (#13), tangentially |

Cross-cutting measurement dimensions (not tasks) also remain unbenchmarked for analyst work: answer consistency (pass^k), calibrated refusal under missing data (FailSafeQA aside), multi-turn correction handling, and cost-normalized scoring.

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

## Sources

Primary sources linked inline. Key verification artifacts: HF dataset-viewer API row/statistics dumps for `AfterQuery/FinanceQA` (schema, per-category counts, example rows); downloaded `ScaleAI/PRBench` parquet files (split sizes, rubric counts and weights measured directly); live leaderboard reads (AfterQuery, Scale Labs, Vals AI) on 2026-08-04.
