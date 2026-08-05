#!/bin/bash
# Reproduce both P2 benchmarks end to end (FinanceQA grader + PRBench probe).
set -euo pipefail
cd "$(dirname "$0")"
./financeqa/run_all.sh
./prbench/run_all.sh
