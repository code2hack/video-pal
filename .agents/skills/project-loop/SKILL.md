---
name: project-loop
description: Run one bounded local project-loop cycle for deterministic work selection, receipt validation, and safe handoff. Use when Codex must operate the repository's reusable project-loop controller, especially Stage 0 dry-run selection, schema-valid receipts, and fail-closed automation planning.
---

# Project Loop

Use this skill only for the repository-local project-loop controller. Keep product-specific facts in configuration, issues, PRs, specs, and state files.

## Stage 0

Run dry-run selection with:

```bash
python3 scripts/project-loop/select_work.py \
  --config project-loop.toml \
  --candidates <issues-or-prs.json>
```

The selector must process at most one work item, explain every rejection, emit a schema-valid receipt, and make no GitHub or repository mutations.

## Receipts

Validate receipts with:

```bash
python3 scripts/project-loop/validate_receipt.py <receipt.json>
```

Read `references/project-run-receipt.md` before changing receipt fields.

## Safety

- Keep `repair_enabled = false` unless the human owner separately approves repair mode.
- Treat absent GitHub credentials or checker command as a fail-closed condition.
- Do not merge, deploy, approve product behavior, expose secrets, or mutate protected branches.
- Publish durable summaries to issues/PRs only when explicitly enabled by configuration and credentials.
