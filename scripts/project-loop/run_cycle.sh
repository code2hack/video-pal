#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

stage="stage0"
args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage)
      stage="${2:-}"
      shift 2
      ;;
    --stage=*)
      stage="${1#--stage=}"
      shift
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

if [[ "$stage" != "stage0" ]]; then
  echo "Only Stage 0 dry-run selection is implemented. Stage 1/2 require separate human authorization." >&2
  exit 2
fi

exec python3 scripts/project-loop/select_work.py "${args[@]}"
