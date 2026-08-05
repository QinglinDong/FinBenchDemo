---
pretty_name: BlueFin Public Set
tags:
- spreadsheet
- agent-benchmark
- finance
configs:
- config_name: interrogation
  data_files:
  - split: test
    path: data/interrogation/test-*.parquet
- config_name: manipulation
  data_files:
  - split: test
    path: data/manipulation/test-*.parquet
- config_name: synthesis
  data_files:
  - split: test
    path: data/synthesis/test-*.parquet
license: cc-by-nc-4.0
language:
- en
size_categories:
- n<1K
---

# Bluefin Release

A spreadsheet-agent benchmark of financial-modeling tasks. Each task provides an
Excel input workbook (and, where applicable, a reference output workbook plus a
grading rubric). This dataset is published in Arrow-compatible Parquet so it can
be loaded directly with 🤗 `datasets` — no custom loading script required.

The original per-task files remain in the `tasks/` tree; the Parquet subsets
under `data/` are a row-assembled, Arrow-native view of those same files.

## Links

- 📄 Paper: [BlueFin: Benchmarking LLM Agents on Financial Spreadsheets](https://arxiv.org/abs/2605.30907) (arXiv:2605.30907)
- 💻 Code: [github.com/Longitude-Labs/bluefin](https://github.com/Longitude-Labs/bluefin)

## Subsets

Each task type is an independently loadable subset (`split="test"`):

```python
from datasets import load_dataset

interrogation = load_dataset("Longitude-Labs/bluefin-release", "interrogation", split="test")
manipulation  = load_dataset("Longitude-Labs/bluefin-release", "manipulation",  split="test")
synthesis     = load_dataset("Longitude-Labs/bluefin-release", "synthesis",     split="test")
```

| Subset | Rows | Grain | Reference output |
|---|---|---|---|
| `interrogation` | 3 | one row **per question** | — (Q&A over the workbook) |
| `manipulation` | 7 | one row **per task** | `golden_output` |
| `synthesis` | 1 | one row **per task** | `sample_output` |

## Schema

Workbooks are stored as **raw `.xlsx` bytes** (a `binary` column) — re-open them
downstream with `openpyxl`. Structured JSON (`questions`/`metadata`/`rubric`) is
stored as **raw JSON strings** (`json.loads()` to parse); `instruction` is raw
Markdown text. A few stable scalars are promoted to typed columns for filtering.

**`workbook_id`** is a lightweight content id — `sha256(input_workbook)[:12]` —
that identifies unique input workbooks without inspecting the bytes.

### `interrogation`
`task_id` (str), `question_id` (str), `question` (str), `expected_answer` (str),
`public` (bool), `workbook_id` (str), `input_workbook` (bytes).
*(The same workbook bytes repeat across a task's question rows; `workbook_id` is
shared across them.)*

### `manipulation`
`task_id` (str), `task_type` (str), `public` (bool), `n_criteria` (int32),
`workbook_id` (str), `instruction` (str), `metadata` (str, raw JSON),
`rubric` (str, raw JSON), `input_workbook` (bytes), `golden_output` (bytes).

### `synthesis`
Same as `manipulation`, with `sample_output` (bytes) in place of `golden_output`.

> **Notes**
> - The top-level `task_id` is always the **task folder/path key**. It may differ from the
>   `task_id` recorded *inside* the `metadata` JSON (e.g. the synthesis task's folder is
>   `TTWO_Operating_Model_DCF` while `metadata.task_id` is `gf2_0bfe9c36`). Use the column for
>   addressing; use the JSON for provenance.
> - Workbook columns hold the **exact original `.xlsx` bytes**. To preserve fidelity (formulas,
>   formatting), keep these bytes — a load-then-resave round-trip through `openpyxl` may drop
>   features openpyxl doesn't model.

## Working with the workbooks

```python
import io, openpyxl

row = manipulation[0]
wb = openpyxl.load_workbook(io.BytesIO(row["input_workbook"]))
print(row["task_id"], row["workbook_id"], wb.sheetnames)
```

## Citation

```
@misc{kundurthy2026bluefinbenchmarkingllmagents,
      title={BlueFin: Benchmarking LLM Agents on Financial Spreadsheets}, 
      author={Srivatsa Kundurthy and Clara Na and Colton Moraine and Anoushka Mohta and Case Winter and George Fang and John Ling and Emma Strubell and Zach Kirshner},
      year={2026},
      eprint={2605.30907},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2605.30907}, 
}
```