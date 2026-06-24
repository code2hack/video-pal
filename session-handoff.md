# Session Handoff

## Current Objective

- Goal: define a reusable, product-agnostic project-loop protocol and portable naming contract from issue #5.
- Current status: draft PR #6 is rebased onto updated `main` after PR #4 merged; DGX Spark verification passed.
- Branch: `chatgpt/5-project-loop-protocol`.
- Primary writer: ChatGPT.
- Codex implementation issue: #7.

## Completed This Session

- [x] Opened issue #5 for the reusable project-loop protocol.
- [x] Added `docs/project-loop.md`.
- [x] Updated `AGENTS.md` with project-loop invariants.
- [x] Standardized reusable names on `project-*`.
- [x] Defined one-item cycles, worktree isolation, maker/checker separation, bounded repair, durable receipts, and human gates.
- [x] Opened draft PR #6.
- [x] Opened Codex-owned implementation issue #7 with required paths, stages, tests, evidence, and branch name.
- [x] Rebasing prerequisite complete: PR #2 and PR #4 are merged into `main`.
- [x] Rebased `chatgpt/5-project-loop-protocol` onto updated `main`.
- [x] Reconciled `AGENTS.md` by preserving branch/identity governance, specification workflow governance, and project-loop governance.
- [x] Ran DGX Spark verification on the rebased PR #6 branch.

## Verification Evidence

| Check | Method | Result | Environment | Notes |
|---|---|---|---|---|
| Protocol coverage | Manual review of `docs/project-loop.md` against issue #5 | Pass | ChatGPT GitHub connector | All requested design areas represented |
| Harness consistency | Manual comparison of `AGENTS.md` and `docs/project-loop.md` | Pass | ChatGPT GitHub connector | Detailed design remains in the doc; invariants are in AGENTS |
| Portable naming | Review all proposed reusable paths | Pass | ChatGPT GitHub connector | Uses `project-*`; no product-specific reusable path |
| Full startup | `./init.sh` | Pass | DGX Spark | Specification validation passed; traceability passed for 8 features; structural harness validation 100/100 |
| Diff check | `git diff --check origin/main...HEAD && git diff --check` | Pass | DGX Spark | No whitespace errors |
| Feature JSON | `python3 -m json.tool feature_list.json >/tmp/video-pal-pr6-feature-list.json` | Pass | DGX Spark | Feature state parses as JSON |
| Python syntax | `python3 -m py_compile scripts/spec_utils.py scripts/validate_specs.py scripts/check_traceability.py` | Pass | DGX Spark | No syntax errors |
| Loop implementation tests | Commands in issue #7 | Not started | DGX Spark | Separate Codex-owned scope |

## Decisions Recorded

- Reusable harness/loop artifacts use generic `project-*` naming.
- The loop is a bounded controller above the harness, not an unbounded self-prompt.
- Loop v1 begins with dry-run selection and read-only PR verification.
- Maker and checker are separate; the checker is read-only.
- Repair defaults off and, when enabled later, is bounded to three attempts unless approved otherwise.
- Essential run state is published as a durable issue/PR receipt.
- Human product, architecture, deployment, destructive-action, and merge gates remain intact.

## Blockers / Risks

- PR #6 is still draft and requires ChatGPT review after Codex verification.
- Human merge authorization is still required.
- PR #8 and PR #11 are downstream and require retargeting or rebasing after PR #6.
- Stage 1 read-only PR verification is not authorized.
- Stage 2 repair mode is not authorized.
- Product specifications remain draft; product feature implementation is not eligible.

## Next Session Startup

1. Read `AGENTS.md`, `docs/project-loop.md`, all state files, issue #5, issue #7, and PR #6.
2. Confirm the current state of PRs #6, #8, and #11.
3. Do not assume the project-loop protocol is merged project truth until PR #6 merges.
4. Do not enable Stage 1, Stage 2, repair, merge, deployment, product implementation, or privileged commands without separate authorization.

## Exact Next Action

**Codex:** push the rebased branch, retarget PR #6 to `main`, and post evidence.
**ChatGPT afterward:** review the rebased PR #6 for conformity with issue #5.
**Human owner:** approve/revise the protocol and explicitly authorize merge.
