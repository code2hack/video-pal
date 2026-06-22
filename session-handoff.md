# Session Handoff

## Current Objective

- Goal: establish the specification-driven feature and verification workflow from issue #3.
- Current status: draft PR #4 contains the proposed governance change; human approval and DGX Spark verification are pending.
- Branch: `chatgpt/3-specification-workflow`.
- Primary writer: ChatGPT.

## Completed This Session

- [x] Defined specification authority, lifecycle, stable IDs, and change control.
- [x] Added draft product, quality, MVP, and feature-template documents.
- [x] Added feature-list schema version 2 with planning/execution ownership.
- [x] Added specification and traceability validators.
- [x] Updated `init.sh` to run the new checks and the existing structural harness validator.
- [x] Updated durable state and decision artifacts.
- [x] Removed the accidental temporary test file.

## Verification Evidence

| Check | Command | Result | Environment | Notes |
|---|---|---|---|---|
| Specification structure | `python3 scripts/validate_specs.py` | Pass | ChatGPT container | Draft specs and stable IDs validated |
| Feature traceability | `python3 scripts/check_traceability.py` | Pass | ChatGPT container | Six feature entries and draft MVP reference validated |
| Python syntax | `python3 -m py_compile scripts/spec_utils.py scripts/validate_specs.py scripts/check_traceability.py` | Pass | ChatGPT container | No syntax errors |
| Shell syntax | `bash -n init.sh` | Pass | ChatGPT container | No shell syntax errors |
| Full startup | `./init.sh` | Pending | DGX Spark | Codex must run with bundled harness skill available |

## Decisions Recorded

- Product behavior lives in approved specs; work status lives in `feature_list.json`.
- Draft specs do not authorize implementation.
- Human approval is required for product behavior and material spec changes.
- ChatGPT curates planning and traceability; Codex owns executable implementation and local evidence.
- Feature-list generation must preserve execution fields and evidence.

## Blockers / Risks

- Product scope and quality targets are unresolved by design.
- Draft PR #2 also edits `AGENTS.md`; merge order requires explicit reconciliation.
- No DGX Spark evidence exists for this branch yet.
- No application stack or application verification command exists yet.

## Next Session Startup

1. Read `AGENTS.md`, `spec/README.md`, all state files, issue #3, and PR #4.
2. Confirm whether PR #2 or PR #4 has changed or merged.
3. Pull or check out `chatgpt/3-specification-workflow`.
4. Run `./init.sh` on the DGX Spark.
5. Record exact output and environment in PR #4.
6. Do not modify product scope unless the human owner is actively resolving the draft questions.

## Exact Next Action

**Codex:** validate PR #4 on DGX Spark and post evidence.  
**ChatGPT afterward:** review the evidence and reconcile any changes.  
**Human owner:** approve/revise governance and authorize merge.
