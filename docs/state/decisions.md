# Decisions

Last updated: 2026-06-24

## Accepted

### Repository is the shared memory bus

Future collaboration between the human owner, ChatGPT, and Codex must persist through tracked files, Git history, issues, and PRs. Chat history alone is not durable project memory.

### Source-of-truth order

1. Repository authority files, using the domain boundaries in `spec/README.md`
2. Git history
3. Human-approved decisions recorded in tracked files
4. Issues and PRs
5. Current session chat
6. Agent assumptions

### Role boundaries

- Human owner owns product direction, acceptance, architecture approval, secrets, deployment, and merge authorization.
- ChatGPT plans, drafts specifications and acceptance criteria, reviews, stewards GitHub state, and curates harness/loop protocol.
- Codex implements locally, writes executable tests, verifies on DGX Spark, implements local automation, commits, and pushes.

### Evidence over claims

Agents must record exact verification evidence before claiming work is done. Evidence belongs in tracked state files, commits, PRs, issues, or schema-valid project-loop receipts.

### Adopt a layered specification system

Human direction on 2026-06-22 approved adding multiple small specification files under root `spec/` rather than a single monolithic document.

Authority is separated across product scope, feature behavior, quality constraints, architecture decisions, execution state, and test evidence.

### Human approval gates product behavior

A `draft` specification is discussion material only. Only the human owner may authorize `draft → approved`, and application implementation must not start from a draft product spec.

### Stable traceability identifiers

Use permanent IDs:

- `VP-NNN` for feature specs
- `VP-NNN-REQ-NNN` for functional requirements
- `VP-NNN-AC-NNN` for acceptance criteria
- `QUAL-NNN` for cross-cutting quality requirements

Identifiers must not be silently reused or repurposed.

### Preserve execution state during generation

ChatGPT normally curates planning fields in `feature_list.json`. The working actor, normally Codex for implementation, owns execution status, branch, PR, blockers, and evidence. Any generator must merge planning changes and preserve execution data.

### Tests are evidence, not product authority

Tests and generated test skeletons map to acceptance criteria. They do not change approved behavior. Generated tests become evidence only after review and execution in the stated environment.

### Use portable project-loop naming

Reusable harness and automation artifacts must use generic `project-*` names rather than a product or repository name.

Canonical examples include:

```text
project-loop.toml
.project-loop/
.agents/skills/project-loop/
.codex/agents/project-verifier.toml
scripts/project-loop/
docs/project-loop.md
```

Repository-specific values belong in configuration, specifications, issues, PRs, and state files. Product files may retain product-specific names when they represent product truth rather than reusable framework machinery.

### Separate the harness from the loop

The harness defines the rules, context, verification, and durable state for one agent run. The project loop sits above it and repeatedly discovers one eligible work item, invokes agents inside isolated worktrees, checks results, records evidence, and chooses the next allowed transition.

The loop must consume the harness rather than duplicate or bypass it.

### Use a bounded project-loop state machine

One cycle processes at most one item and follows:

```text
DISCOVER → CLAIM → ISOLATE → RECONCILE → BASELINE
→ VERIFY → REPAIR (bounded) → INDEPENDENT REVIEW
→ RECEIPT → HANDOFF / STOP
```

A later schedule may start another bounded cycle. A cycle must not retry indefinitely.

### Isolate modifying automation

Every modifying loop run uses a dedicated Git worktree and an actor-prefixed non-protected branch. Isolation prevents checkout collisions but does not replace branch ownership, conflict detection, or review.

### Separate maker and checker

The maker may edit within the approved scope. A different read-only checker validates governance, specifications, acceptance coverage, changed-file scope, evidence, unsupported claims, and remaining risks.

The maker does not finally accept its own work, and the checker does not edit or merge.

### Bound repair and fail closed

The default cycle limit is one work item, one edited branch, and at most three repair attempts. Repair must default off until dry-run selection and read-only verification are proven.

The loop stops on human decisions, unchanged or growing validation delta, conflicts, unexpected files, exhausted budgets, insufficient permissions, ambiguous authority, or any need to change approved behavior merely to pass a test.

### Use durable project-loop receipts

Every non-no-op cycle publishes a structured issue/PR receipt containing identity, work item, claim, commits, attempts, exact command results, changed files, validation delta, checker result, stop reason, next actor, and known risks.

Raw local logs may remain under ignored `.project-loop/`, but essential cross-session state must not exist only there.

### Preserve human gates

The project loop must stop before product acceptance, material specification changes, architecture approval, secret handling, deployment, destructive operations, governance exceptions, or final merge unless the human owner explicitly authorizes the exact action.

### Relay human authorization through ChatGPT to durable GitHub comments

Human approvals may be made in ChatGPT conversation, but they become actionable for Codex only after ChatGPT posts a durable GitHub authorization comment to the relevant issue or pull request.

Each approval comment must include a scoped approval ID, exact approved scope, explicit not-authorized scope, conditions, expiry or invalidation, decision owner, recorder, authorized executor, issue or PR, branch, and status.

ChatGPT records and transmits the human owner's decision; ChatGPT does not independently grant authority. Codex must keep waiting if the durable GitHub authorization comment is absent, ambiguous, or unscoped.

### Require privileged-command escalation and forbid silent user-level fallback

When approved work requires `sudo`, package installation, system-wide dependency changes, service configuration, privileged device access, group membership changes, or similar elevated operations, Codex must stop and post a privileged-operation request to the relevant issue or pull request.

Codex must not silently substitute user-local packages, home-directory prefixes, portable binaries, local Conda or virtualenv packages, home-directory compiled tools, or architecture changes merely to avoid privileged approval. Project-local environments, caches, containers, fixtures, and non-privileged installs remain allowed only when they are already part of the approved architecture or task scope.

Codex must never ask the human to paste a sudo password into chat, GitHub, scripts, environment variables, or logs; must not use `sudo -S`; and must not persist elevated access without separate explicit approval. If a password prompt is required, the human enters it directly in the local DGX terminal.

### Roll out automation in stages

1. dry-run selector
2. read-only pull-request verification
3. bounded deterministic repair
4. approved feature implementation only after earlier stages are stable and the human explicitly expands scope

## Pending

### Video Pal product scope

The first user journey, supported interface, video inputs, outputs, privacy boundary, latency, accuracy, and recovery behavior remain unresolved in draft specifications.

### Quality targets

No numeric performance, reliability, privacy, security, accessibility, or portability requirements have been approved.

### Governance PR merge order

PR #2, PR #4, PR #6, and PR #8 have merged into `main`. PR #11 has been rebased onto updated `main` after PR #8 merge commit `b0fc66efb9bd7f0ccdc26c4a31368d205046e2cc`; post-rebase DGX verification has passed and ChatGPT re-review is pending. PR #11 still requires explicit human merge authorization before merge.

### Project-loop protocol approval

Issue #5 and PR #6 are merged project truth as of merge commit `4cc68bf4f16a7b30930c6b813d6a53185d41c2ce`.

### Project-loop local implementation

Issue #7 is assigned to Codex. On 2026-06-22, the human owner authorized Stage 0 implementation only on `codex/7-project-loop-v1`, using `chatgpt/5-project-loop-protocol` as the explicit stacked base unless prerequisites merge first. After PR #6 merged, PR #8 was rebased onto updated `main`.

Stage 0 dry-run selection, configuration, receipt validation, fixtures, deterministic tests, and a draft PR merged through PR #8. GitHub writes remain disabled by default.

Stage 1 read-only PR verification and Stage 2 repair require separate human approval.

### Repair-mode authorization

Even after Stage 0 and Stage 1 exist, repair mode remains disabled by default until the human owner reviews read-only evidence and separately approves expansion.

### Application verification commands

`init.sh` validates specifications, traceability, and harness structure. Application-specific and project-loop executable commands remain pending until their implementations are proven locally.
