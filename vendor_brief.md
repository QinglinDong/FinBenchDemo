# P5 — Vendor Brief: FinanceQA-A200 (Analyst Assumption Benchmark, 200 items)

## What you are building

200 analyst "hand-spreading" questions over recent SEC filings, extending an existing 148-item benchmark whose items all come from one company. Each item asks for a specific financial quantity computed from a filing excerpt. The defining feature: most items must require the analyst move of **constructing a number the filing does not state**, using standard conventions (capitalizing leases, defining excess cash, building adjusted EBITDA). Composition: **120 assumption items** (construction required), **50 basic items** (derivable directly from the excerpt), **30 trap items** (construction is *not* defensible from the given data; the correct behavior is a qualified refusal). Coverage: **≥20 issuers, ≥5 GICS sectors, all filings dated within the last 12 months** (contamination control), no more than 15 items per issuer.

## Item specification (JSONL, one object per item)

| field | requirement |
|---|---|
| `issuer`, `filing_url`, `excerpt` | Real filing; excerpt must contain everything needed (plus the stated conventions) to derive the gold. Verifier must not need the full filing. |
| `question` | One quantity, one period. For assumption items the quantity must NOT be readable off the excerpt — if a single line item answers it, it is basic, not assumption. |
| `question_type` | `basic` / `assumption` / `trap` |
| `gold_primary` | **A bare quantity, machine-parsable**: `"$1,502 (in millions)"`, `"24.30%"`, `"3.67x"`. Never a sentence. (The predecessor benchmark's sentence-style golds measurably broke automated grading; this is a hard requirement.) For trap items: `"NOT_CONSTRUCTIBLE"` plus a one-sentence reason. |
| `accepted_alternatives` | Every professionally defensible convention that yields a different number, each as `{convention: <name>, value: <bare quantity>}`. Empty list allowed but must be affirmed, not omitted. (In our pilot, 51% of model answers judged "wrong" used a defensible alternative convention — this field is the fix.) |
| `gold_cot` | Step-by-step derivation naming each convention fork and the branch taken. |
| `assumption_named` | For assumption items: the specific convention the item is testing, in ≤10 words (e.g., "operating cash = min(2% revenue, cash)"). |

## Grading rubric (what your annotators apply, and what the automated grader mirrors)

1. **Correct** iff the candidate's final answer matches `gold_primary` within **0.5% relative tolerance**, under any formatting/scale/sign presentation ($32,095M = $32.1B = 32,095 million).
2. A final answer matching an `accepted_alternatives` value is scored **correct-alternative** (reported separately from correct-primary).
3. No partial credit. A response giving multiple candidate numbers is graded on the one it commits to as final; if it commits to none, incorrect.
4. Trap items: **correct** = declines to produce a point estimate AND states why the data is insufficient; any confident point estimate is incorrect.

## Worked gold examples

**1. Basic.** Excerpt: Costco FY2024 income statement. Q: *"Calculate operating profit for 2024."* → `gold_primary: "$9,285 (in millions)"`, `accepted_alternatives: []` (affirmed empty — the line item is stated). CoT: operating income appears directly; no fork.

**2. Assumption.** Excerpt: income statement + Note 5 (leases: operating lease cost $291M, variable lease cost $163M). Q: *"Compute adjusted EBITDA for 2024, treating leases as debt-equivalents."* → `gold_primary: "$11,969 (in millions)"` (EBITDA $11,522 + $291 + $163 − $7 short-term lease cost); `accepted_alternatives: [{convention: "SBC add-back variant", value: "$12,787 (in millions)"}]`; `assumption_named: "add back operating & variable lease cost"`. The unadjusted $11,522 is **not** an accepted alternative — write it into the item as a known-wrong distractor.

**3. Boundary case (deliberately hard — this is the calibration item).** Excerpt: balance sheet + lease note *where variable lease assets are not recognized*. Q: *"Estimate variable lease assets for 2024."* GAAP-literal reading says this quantity does not exist on the balance sheet (ASC 842 excludes variable payments) — and our pilot showed every model tier answers **$0** on exactly this reasoning. The item is nonetheless an **assumption item**, not a trap: the analyst convention is to capitalize variable lease cost like the ROU assets (multiply by the fixed-lease ratio → `gold_primary: "$1,502 (in millions)"`). The writer must include `accepted_alternatives` for the defensible capitalization-multiple variants, and the item docs must state *why this is not a trap* (the data fully supports the construction). Any writer who cannot articulate the trap-vs-assumption distinction on this example fails qualification.

## QA on delivered batches (batch = 50 items)

- **Independent recompute:** a second SME re-derives every gold from the excerpt alone, blind to `gold_primary`. Batch acceptance requires **≥90% within-0.5% reproduction**; every miss is adjudicated, and systematic misses (same convention fork) reject the batch.
- **Gold seeding:** we supply 5 pre-validated items disguised in each batch; a verifier who flags <4/5 correctly is replaced.
- **Automated checks (we run, vendor sees results):** `gold_primary` parses as a bare quantity; excerpt self-containment (a model given only the excerpt + gold CoT reproduces the gold); assumption items fail a lookup probe (a model told to *only quote disclosed figures* must NOT be able to produce the gold).
- **Specific rejection criteria:** sentence-style golds; assumption items answerable by lookup; excerpts requiring outside data; `accepted_alternatives` omitted rather than affirmed empty; two items testing the same (issuer, metric) pair; any item whose gold the writer produced with LLM assistance (see below).
- **Inter-annotator agreement threshold:** on the type tag (basic/assumption/trap), writer–verifier Cohen's κ ≥ 0.75 per batch.

## Who may write items

- ≥3 years in a role that hand-spreads filings (buy-side/sell-side analyst, IB, corporate development, FP&A manager) — *tax or audit background alone does not qualify*; CFA Level II+ or demonstrably equivalent.
- Passes our 5-item screener: derive golds for 3 items (within tolerance), correctly classify 2 boundary cases as assumption vs. trap (example 3 above is the model).
- **No LLM assistance for gold derivation** (contamination and independence: these items will evaluate the same model families that would be assisting). LLM use is permitted only for prose polish of questions, never for numbers.
- Verifiers must be different individuals from writers, same qualification bar.

**Deliverables & cadence:** 4 batches × 50 items, JSONL per the schema above, first batch in 3 weeks (calibration batch — expect heavy feedback), full delivery in 8. Invoice against accepted items only.
