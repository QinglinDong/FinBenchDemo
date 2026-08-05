# benchmarks/ — the deep-dived evals (and one demotion exhibit), verbatim

Raw, unmodified official data for the four evals deep-dived in `../selected_evals.md`, downloaded 2026-08-04/05 so every P1 claim can be checked against the primary artifact. Item counts were verified by loading each file.

| dir | eval (deep dive) | contents | items | license | source |
|---|---|---|---|---|---|
| `financeqa/` | FinanceQA (DD1) | `test.csv` — the full public set (same file `../p2/` runs on) | 148 (38 basic / 46 assumption / 64 conceptual) | Apache-2.0 | [HF: AfterQuery/FinanceQA](https://huggingface.co/datasets/AfterQuery/FinanceQA) |
| `prbench/` | PRBench-Finance (DD2) | `finance.parquet`, `finance_hard.parquet` — full expert rubrics, 48 cols (the legal split is not mirrored: out of survey scope) | 600 / 300 | CC-BY-4.0 | [HF: ScaleAI/PRBench](https://huggingface.co/datasets/ScaleAI/PRBench) |
| `taxcalcbench/` | TaxCalcBench v1+v2 (DD3) | `repo/` — full source incl. all test cases and the deterministic line-by-line grader. Upstream's own model-run `results/` dirs (~240 MB of their eval outputs, not benchmark data) and `.git` removed. | 51 (ty24) + 50 (ty25) returns | MIT | [GitHub: column-tax/tax-calc-bench](https://github.com/column-tax/tax-calc-bench) |
| `spreadsheetbench2/` | SpreadsheetBench 2 (DD4) | `repo/` — evaluation code + agent scaffold; `data_example_05_11.zip` — official example tasks. The full task set (`spreadsheetbench-v2.zip`, 128 MB) exceeds GitHub's 100 MB file limit — restore with `curl -L https://huggingface.co/datasets/KAKA22/SpreadsheetBench-v2/resolve/main/spreadsheetbench-v2.zip -o spreadsheetbench2/spreadsheetbench-v2.zip` | 321 tasks (full set) | MIT | [GitHub: RUCKBReasoning/SpreadsheetBench-2](https://github.com/RUCKBReasoning/SpreadsheetBench-2) · [HF: KAKA22/SpreadsheetBench-v2](https://huggingface.co/datasets/KAKA22/SpreadsheetBench-v2) |
| `bluefin/` | BlueFin (demoted candidate — this download is the evidence) | `interrogation.parquet`, `manipulation.parquet`, `synthesis.parquet` + upstream README. **The release is explicitly a "Public Set": 11 of the paper's 131 tasks** (3 interrogation questions / 7 manipulation / 1 synthesis) — the finding that demoted BlueFin's C5 to *partial* in P1. | 11 public of 131 | CC-BY-NC-4.0 | [HF: Longitude-Labs/bluefin-release](https://huggingface.co/datasets/Longitude-Labs/bluefin-release) · [GitHub: Longitude-Labs/bluefin](https://github.com/Longitude-Labs/bluefin) |

**License note:** BlueFin's public set is CC-BY-**NC**-4.0 (non-commercial) — inspection and research use only; do not fold it into commercial pipelines or training data.

## Previously mirrored, removed when the survey down-scoped to the deep-dive set

Each is one `curl`/`git clone` away if needed again: FinQA ([GitHub: czyssrs/FinQA](https://github.com/czyssrs/FinQA), MIT), Aiera finqa-verified ([HF](https://huggingface.co/datasets/Aiera/finqa-verified)), FinanceBench open sample ([GitHub: patronus-ai/financebench](https://github.com/patronus-ai/financebench), CC-BY-NC-4.0), FinRetrieval ([HF: daloopa/finretrieval](https://huggingface.co/datasets/daloopa/finretrieval), MIT), BigFinanceBench public subset ([HF: RogoAI/big-finance-benchmark](https://huggingface.co/datasets/RogoAI/big-finance-benchmark), CC-BY-4.0, carries `do_not_train` + canary flags).

Never mirrored: Vals Finance Agent v2 (items private), Rivet TaxBench (not public), CFA banks (licensing), τ³-Banking (in the tau2-bench `dev/tau3` branch, one clone away).
