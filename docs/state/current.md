# Current Project State

Last updated: 2026-06-23

## Snapshot

The project remains in harness, specification, and automation-governance setup. Application implementation has not started.

Current active feature: `feat-008` — Implement Project Loop v1, Stage 0 only.

## Repository State

- Repository: `code2hack/video-pal`
- Default branch: `main`
- Merged harness communication protocol: `main`
- Related governance PR: draft PR #2 for branch, file-ownership, and actor-identity rules
- Specification issue / branch / PR: #3 / `chatgpt/3-specification-workflow` / draft PR #4
- Project-loop issue / branch / PR: #5 / `chatgpt/5-project-loop-protocol` / stacked draft PR #6
- Codex implementation issue / branch / PR: #7 / `codex/7-project-loop-v1` / draft PR #8
- No application manifest or source stack exists.

## Specification State

- `spec/README.md`, `spec/product.md`, `spec/quality.md`, and `spec/features/VP-001-mvp.md` are proposed in draft PR #4.
- Product and quality specifications remain `draft`.
- No product implementation feature is eligible.

## Project Loop State

- `docs/project-loop.md` defines the proposed reusable controller above the harness.
- Reusable paths use generic `project-*` naming.
- Loop v1 begins with one-item dry-run selection and read-only PR verification.
- Modifying runs require isolated worktrees.
- Maker and checker are separate; the checker is read-only.
- Repair is bounded and must default off until earlier stages are proven.
- Every non-no-op cycle publishes a durable receipt.
- Human approval remains required for product/architecture decisions, deployment, destructive actions, governance exceptions, and merge.
- Stage 0 project-loop dry-run selection code exists on `codex/7-project-loop-v1`.
- PR #8 review hardening is committed for Stage 0 output safety, receipt immutability, issue/PR identity handling, malformed candidate containers, and unresolved Git HEAD.
- Stage 0 uses fixture or manually supplied JSON by default.
- GitHub writes and receipt comments remain disabled by default.
- Stage 1 read-only PR verification is not implemented.
- Stage 2 repair remains disabled and unimplemented beyond receipt/config safety checks.

## Collaboration State

- ChatGPT is the primary writer for issue #5 and PR #6.
- Codex owns issue #7 and has human approval for Stage 0 implementation only.
- PR #6 is stacked on PR #4 and is not merged project truth.
- Governance PRs #2, #4, and #6 require explicit merge-order reconciliation.

## Verification State

- Protocol and naming have been manually reviewed through the GitHub connector.
- No DGX Spark verification has been claimed for PR #6.
- Stage 0 focused checks passed on DGX Spark: Python compile, 33 project-loop pytest tests, shell syntax, receipt validation, skill validation, full startup, and diff check.

## Next Step

Codex posts updated PR #8 review-fix evidence to PR #8 and issue #7, then stops for ChatGPT/human review. Stage 1 and repair require separate human approval.
