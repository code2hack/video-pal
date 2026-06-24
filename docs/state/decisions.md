# Decisions

Last updated: 2026-06-22 SGT

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
- ChatGPT plans, drafts specifications and acceptance criteria, reviews, and stewards GitHub state.
- Codex implements locally, writes executable tests, verifies on DGX Spark, commits, and pushes.

### Evidence over claims

Agents must record exact verification evidence before claiming work is done. Evidence belongs in tracked state files, commits, PRs, or issues.

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

## Pending

### Video Pal product scope

The first user journey, supported interface, video inputs, outputs, privacy boundary, latency, accuracy, and recovery behavior remain unresolved in draft specifications.

### Quality targets

No numeric performance, reliability, privacy, security, accessibility, or portability requirements have been approved.

### Governance PR merge order

PR #2 merged first. PR #4 now carries the `AGENTS.md` reconciliation that preserves PR #2 branch/identity governance and PR #4 specification workflow governance. PR #4 still requires ChatGPT review and explicit human merge authorization.

### Application verification commands

`init.sh` validates specifications, traceability, and harness structure. Application-specific commands remain pending until a product stack is approved and scaffolded.
