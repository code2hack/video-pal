#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=== Harness Initialization ==="

echo "=== Specification Validation ==="
python3 scripts/validate_specs.py

echo "=== Feature Traceability Validation ==="
python3 scripts/check_traceability.py

echo "=== Structural Harness Validation ==="
if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: node is required to run the structural harness validator." >&2
  exit 1
fi
node skills/harness-creator/scripts/validate-harness.mjs --target .

echo "=== Project Loop Validation ==="
python3 -m py_compile scripts/project-loop/select_work.py scripts/project-loop/validate_receipt.py
python3 -m pytest tests/project-loop
bash -n scripts/project-loop/run_cycle.sh
python3 scripts/project-loop/validate_receipt.py tests/project-loop/fixtures/verifier_failure_receipt.json

echo "=== Application Verification ==="
if [[ -f pyproject.toml || -f package.json || -f Cargo.toml || -f go.mod ]]; then
  echo "ERROR: an application manifest exists but init.sh has no application verification command yet." >&2
  exit 1
else
  echo "No application manifest detected; product implementation is not yet approved."
fi

echo "=== Verification Complete ==="
echo
echo "Next steps:"
echo "1. Read AGENTS.md and spec/README.md"
echo "2. Read feature_list.json and the active feature specification"
echo "3. Work on exactly one eligible feature"
echo "4. Re-run ./init.sh before claiming completion"
