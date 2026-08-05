# benchmarks/ — verbatim copies of the surveyed public finance evals

Raw, unmodified official data for the evals discussed in `../selected_evals.md`, downloaded 2026-08-04 so every claim in P1 can be checked against the primary artifact. Item counts below were verified by loading each file (they reconcile with the P1 write-up).

| dir | eval | contents | items | license | source |
|---|---|---|---|---|---|
| `financeqa/` | FinanceQA (AfterQuery, 2025) | `test.csv` — the full public set (same file used by `../p2/`) | 148 (38 basic / 46 assumption / 64 conceptual) | Apache-2.0 | [HF: AfterQuery/FinanceQA](https://huggingface.co/datasets/AfterQuery/FinanceQA) |
| `prbench/` | PRBench (Scale AI, 2025) | `finance.parquet`, `finance_hard.parquet`, `legal.parquet` — full rubrics, 48 cols | 600 / 300 / 500 | CC-BY-4.0 | [HF: ScaleAI/PRBench](https://huggingface.co/datasets/ScaleAI/PRBench) |
| `finqa/` | FinQA (2021) | `dev/test.json` with gold reasoning programs (`train.json` is 78 MB and not committed — restore with `curl -sL https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/train.json -o finqa/train.json`) | 6,251 / 883 / 1,147 (= 8,281) | MIT | [GitHub: czyssrs/FinQA](https://github.com/czyssrs/FinQA) |
| `finqa-verified/` | Aiera finqa-verified (2024) | `finqa_verified.parquet` — the hand-reverified subset | 91 | see upstream card | [HF: Aiera/finqa-verified](https://huggingface.co/datasets/Aiera/finqa-verified) |
| `financebench/` | FinanceBench (Patronus, 2023) | `financebench_open_source.jsonl` — the public sample (source PDFs not mirrored) | 150 of 10,231 | CC-BY-NC-4.0 (see upstream) | [GitHub: patronus-ai/financebench](https://github.com/patronus-ai/financebench) |
| `taxcalcbench/` | TaxCalcBench v1+v2 (Column Tax) | `repo/` — full source incl. test cases and the deterministic line-by-line grader. Their historical model-run `results/` dirs (~240 MB of their own eval outputs, not benchmark data) and `.git` were removed. | 51 (ty24) + 50 (ty25) returns | MIT | [GitHub: column-tax/tax-calc-bench](https://github.com/column-tax/tax-calc-bench) |
| `finretrieval/` | FinRetrieval (Daloopa, 2026) | `questions.parquet` (structured gold: value/unit/period/ticker), `scores.parquet` | 500 questions | MIT (code); data via HF | [HF: daloopa/finretrieval](https://huggingface.co/datasets/daloopa/finretrieval) |
| `bigfinancebench/` | BigFinanceBench public subset (Rogo, 2026) | `big_finance_subset.jsonl` (query + reference answer + full point-weighted rubric), upstream README | 50 of 928 | CC-BY-4.0, carries `do_not_train` + canary flags | [HF: RogoAI/big-finance-benchmark](https://huggingface.co/datasets/RogoAI/big-finance-benchmark) |

Not mirrored, with reasons: **SpreadsheetBench 2** (hundreds of MB of xlsx workbooks + an agent scaffold; inspect at [RUCKBReasoning/SpreadsheetBench-2](https://github.com/RUCKBReasoning/SpreadsheetBench-2)), **Vals Finance Agent** (questions require their tool harness; [vals-ai/finance-agent](https://github.com/vals-ai/finance-agent)), **Rivet TaxBench** (not public), **FinanceBench full set** (private beyond the 150).

Handling note: `bigfinancebench` is tagged `evaluation_only` / `do_not_train` with a benchmark canary — do not use it as training data anywhere downstream.
