# Session Handoff

## Current Objective

- Goal: implement project-loop v1 Stage 0 dry-run selector from issue #7.
- Current status: Stage 0 implementation is in draft PR #8; PR review hardening is pushed and updated evidence is posted.
- Branch: `codex/7-project-loop-v1`.
- Primary writer: Codex.
- Codex implementation issue: #7.

## Completed This Session

- [x] Opened issue #5 for the reusable project-loop protocol.
- [x] Added `docs/project-loop.md`.
- [x] Updated `AGENTS.md` with project-loop invariants.
- [x] Standardized reusable names on `project-*`.
- [x] Defined one-item cycles, worktree isolation, maker/checker separation, bounded repair, durable receipts, and human gates.
- [x] Opened stacked draft PR #6.
- [x] Opened Codex-owned implementation issue #7 with required paths, stages, tests, evidence, and branch name.
- [x] Received human approval for Stage 0 only.
- [x] Added Stage 0 project-loop configuration, selector, receipt validator, run wrapper, skill, checker contract, fixtures, and tests.
- [x] Kept repair disabled and GitHub writes disabled by default.
- [x] Opened draft PR #8 stacked on `chatgpt/5-project-loop-protocol`.
- [x] Addressed PR #8 review findings for Stage 0 output safety, receipt immutability, issue/PR identity collisions, malformed candidate containers, and unresolved Git HEAD.
- [x] Added requested negative tests for tracked/protected output paths, traversal, symlink escape, Stage 0 invariant mutations, issue/PR same-number selection, malformed candidate containers, and Git HEAD failure.

## Verification Evidence

| Check | Method | Result | Environment | Notes |
|---|---|---|---|---|
| Protocol coverage | Manual review of `docs/project-loop.md` against issue #5 | Pass | ChatGPT GitHub connector | All requested design areas represented |
| Harness consistency | Manual comparison of `AGENTS.md` and `docs/project-loop.md` | Pass | ChatGPT GitHub connector | Detailed design remains in the doc; invariants are in AGENTS |
| Portable naming | Review all proposed reusable paths | Pass | ChatGPT GitHub connector | Uses `project-*`; no product-specific reusable path |
| Full startup | `./init.sh` | Pass | DGX Spark | Specification validation, traceability, harness validation 100/100, and project-loop checks pass |
| Python compile | `python3 -m py_compile scripts/project-loop/select_work.py scripts/project-loop/validate_receipt.py` | Pass | DGX Spark | Stage 0 scripts compile |
| Loop tests | `python3 -m pytest tests/project-loop` | Pass | DGX Spark | 33 tests |
| Shell syntax | `bash -n scripts/project-loop/run_cycle.sh` | Pass | DGX Spark | Stage 0 wrapper only |
| Receipt fixture | `python3 scripts/project-loop/validate_receipt.py tests/project-loop/fixtures/verifier_failure_receipt.json` | Pass | DGX Spark | Deterministic schema validation |
| Skill validation | `python /home/code2hack/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/project-loop` | Pass | DGX Spark | Project-loop skill is valid |
| Diff check | `git diff --check` | Pass | DGX Spark | No whitespace errors |

## Decisions Recorded

- Reusable harness/loop artifacts use generic `project-*` naming.
- The loop is a bounded controller above the harness, not an unbounded self-prompt.
- Loop v1 begins with dry-run selection and read-only PR verification.
- Maker and checker are separate; the checker is read-only.
- Repair defaults off and, when enabled later, is bounded to three attempts unless approved otherwise.
- Essential run state is published as a durable issue/PR receipt.
- Human product, architecture, deployment, destructive-action, and merge gates remain intact.
- Stage 0 is authorized; Stage 1 and Stage 2 are not authorized.

## Blockers / Risks

- Draft PR #6 is stacked on draft PR #4.
- Draft PR #2 also changes `AGENTS.md`; all governance changes require ordered reconciliation.
- No DGX Spark execution evidence exists for PR #6.
- Stage 1 read-only PR verification requires separate human approval.
- Stage 2 repair mode requires separate human approval.
- Product specifications remain draft; product feature implementation is not eligible.

## Next Session Startup

1. Read `AGENTS.md`, `docs/project-loop.md`, all state files, issue #7, and the draft PR for this branch.
2. Run `./init.sh`.
3. Review `project-loop.toml` before changing any loop behavior.
4. Do not enable Stage 1, Stage 2, GitHub writes, repair, merge, or deployment without separate human approval.

## Exact Next Action

**ChatGPT:** re-review Stage 0 fixes in PR #8 for conformity with issue #5 and PR #6.
**Human owner:** decide whether to authorize Stage 1 later.
