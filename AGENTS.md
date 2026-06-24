# AGENTS.md

Project harness for reliable agent-assisted development. The repository is the shared memory bus for the human owner, ChatGPT, and Codex.

## Startup Workflow

Before writing code:

1. **Confirm working directory** with `pwd`
2. **Sync repo state** with `git pull --ff-only` when a remote is configured
3. **Read this file** completely
4. **Read current state**: `feature_list.json`, `progress.md`, `session-handoff.md`, `docs/state/current.md`, and `docs/state/decisions.md`
5. **Read specification authority**: `spec/README.md`, `spec/product.md`, `spec/quality.md`, and every spec referenced by the active feature
6. **Read loop authority when automation is involved**: `docs/project-loop.md` and the active loop issue or PR
7. **Review recent commits** with `git log --oneline -20`
8. **Review the active issue and PR**, including unresolved comments and verification requests
9. **Run `./init.sh`** to verify the environment and specification traceability
10. **Reconcile contradictions** between tracked state files before implementation

If baseline verification is failing, repair that first before adding new scope.

## Agent Communication Protocol

### Source of Truth

Do not rely on chat history as durable memory. Truth priority is:

1. Repository files, using the authority boundaries in `spec/README.md`
2. Git history
3. Human-approved decisions recorded in tracked files
4. Issues and PRs
5. Current session chat
6. Agent assumptions

If a decision exists only in chat, it is provisional. Record binding decisions in tracked files.

### Role Boundaries

- **Human owner**: product direction, final authority, scope approval, architecture approval, secrets, deployment decisions, and merge authorization
- **ChatGPT**: planning, specification drafting, acceptance criteria, review, architecture discussion, requirements clarification, consistency checks, harness and loop protocol maintenance, and GitHub-facing stewardship
- **Codex**: local implementation, executable tests, commands, DGX Spark verification, project-loop implementation, refactors, commits, and pushes

Neither AI agent owns product direction. If agents disagree, check this file, approved specifications, feature definitions, decision docs, existing code, and the active loop receipt, then present tradeoffs for the human owner to decide.

### File Edit Ownership

These are primary responsibility lanes, not access-control boundaries. The human owner may edit any file and may explicitly delegate exceptions.

- **Human-owned decisions**: product vision, priorities, acceptance decisions, secrets, deployment targets, and final approval. The human does not need to edit files directly; ChatGPT or Codex may record an approved decision in tracked files and mark the human as the decision owner.
- **ChatGPT-primary files**: `AGENTS.md`, `.github/**`, architecture and decision documents under `docs/**`, issue/PR specifications, and feature decomposition or acceptance criteria in `feature_list.json`.
- **Codex-primary files**: application source, tests, package manifests and lockfiles, build/runtime configuration, implementation scripts, and executable verification logic in `init.sh`.
- **Shared state files**: `feature_list.json`, `progress.md`, `session-handoff.md`, and `docs/state/current.md`. The actor who changes project truth must update the relevant state and evidence. ChatGPT normally edits planning and acceptance fields; Codex normally edits implementation status and verification evidence.
- **Decision log**: ChatGPT normally curates `docs/state/decisions.md`; Codex may add implementation constraints discovered locally. Product or architecture decisions become binding only after human approval.

Do not rewrite another actor's recorded evidence without explanation. Correct it by adding an attributed correction with the reason and supporting evidence.

### Branch and Pull Request Workflow

1. **No direct agent pushes to `main` by default.** ChatGPT and Codex work on dedicated branches and submit PRs. An agent may update or merge `main` only after explicit human instruction.
2. **One issue, one branch, one primary writer.** Check open issues, branches, and PRs before starting. Do not make concurrent uncoordinated edits on another actor's active branch.
3. **Branch names identify the actor:**
   - `chatgpt/<issue>-<slug>` for planning, review, documentation, and harness changes
   - `codex/<issue>-<slug>` for implementation and local verification
   - `human/<issue>-<slug>` for direct human-authored changes
4. **Open a draft PR early for non-trivial work.** The PR is the durable discussion, review, evidence, and handoff boundary.
5. **PR descriptions must record:** actor, linked issue, objective, scope, changed files, verification evidence, known risks, and requested next action.
6. **Review path:** ChatGPT reviews implementation and consistency; Codex may locally validate ChatGPT-authored harness or documentation changes; the human owner approves the decision to merge. An agent may execute the merge only when the human explicitly asks.
7. **Handoff through Git.** To transfer work, push the branch and update its PR or tracked state files. Do not require the human to copy text between ChatGPT and Codex.
8. **Keep branches focused.** Unrelated changes use a separate issue and branch. Resolve or document conflicts before requesting merge.

### Actor Identity and Attribution

All three collaborators may use the same GitHub account, so the GitHub login is the transport identity, not reliable proof of which actor performed the work. Use all of the following conventions:

- branch prefix: `chatgpt/`, `codex/`, or `human/`
- PR title prefix: `[ChatGPT]`, `[Codex]`, or `[Human]`
- PR body fields: `Actor`, `Runtime`, `Linked issue`, `Verification`, and `Human decision required`
- commit trailers:

```text
Actor: <chatgpt|codex|human>
Role: <meta|implementation|owner>
Issue: #<number>
Runtime: <chatgpt-github-connector|dgx-spark|human-local>
```

This attribution is declarative rather than cryptographic. If stronger identity separation becomes necessary, use separate GitHub accounts or GitHub Apps for the agents and signed commits with distinct keys.

### Human Authorization Relay

Human approvals may be given in ChatGPT conversation, but they become actionable for Codex only after ChatGPT posts a durable GitHub authorization comment to the relevant issue or pull request.

The normal authorization path is:

```text
human owner <-> ChatGPT sessions <-> GitHub <-> Codex agent sessions
```

Rules:

- ChatGPT is a relay and recorder of the human owner's decision; ChatGPT does not independently grant authority.
- Codex must request approval in the relevant issue or pull request when work needs a human-owned decision.
- ChatGPT reads the request and repository state, drafts an exact approval packet, obtains the human owner's approval in ChatGPT conversation, then posts the durable GitHub authorization comment.
- Codex may proceed only after reading that durable GitHub authorization comment.
- Codex must keep waiting if ChatGPT cannot publish the authorization comment.
- Chat-only summaries, informal acknowledgements, ambiguous wording, or unscoped approval are not sufficient.

Every approval comment must include a scoped approval ID and exact approved scope. Use:

```text
HA-YYYYMMDD-ISSUE<N>-<SCOPE>-NN
HA-YYYYMMDD-PR<N>-<SCOPE>-NN
```

Examples:

```text
HA-20260624-ISSUE7-STAGE1-01
HA-20260624-PR8-MERGE-01
HA-20260624-ISSUE12-SUDO-01
```

Use separate authorization packets for implementation-stage approval, privileged-command approval, merge approval, and product or architecture approval. Each packet must state approved scope, not-authorized scope, conditions, expiry or invalidation, decision owner, recorder, authorized executor, issue or PR, branch, and status.

Reusable templates live in `docs/protocol/authorization.md`.

### Privileged Operations

When Codex determines approved work requires `sudo`, package installation, system-wide dependency changes, service configuration, privileged device access, group membership changes, or similar elevated operations, Codex must stop and post a privileged-operation request to the relevant issue or pull request.

Codex must not silently bypass a privileged requirement by installing or compiling a user-level substitute unless that substitute is already the approved architecture or task scope.

Silent fallbacks are disallowed, including:

- `pip install --user` or user-local Python packages as a substitute for a requested system dependency
- user-local prefixes under home directories
- portable replacement binaries
- local Conda or virtualenv packages when used only to avoid privileged approval
- compiling a substitute into the home directory
- changing the implementation to avoid approval without recording the tradeoff

Allowed without a privileged request only when already approved by architecture or task scope:

- project-local virtual environments
- project-local dependency caches
- containers
- test fixtures
- non-privileged package installs that are part of the approved project setup

Codex must never ask the human to paste a sudo password into chat, GitHub, a script, an environment variable, or a log. Codex must never use `sudo -S`, echo passwords, edit sudoers, or persist elevated access unless separately and explicitly approved. If a password prompt is required, the human enters it directly in the local DGX terminal.

### Durable State Files

- `AGENTS.md` - stable operating protocol and invariants
- `spec/README.md` - specification authority, lifecycle, IDs, and derivation rules
- `spec/product.md` - product scope and non-goals
- `spec/quality.md` - cross-cutting quality requirements
- `spec/features/*.md` - feature behavior and acceptance criteria
- `docs/project-loop.md` - reusable project-loop architecture and safety contract
- `docs/protocol/authorization.md` - human authorization relay and privileged-operation templates
- `feature_list.json` - derived feature state, dependencies, traceability, blockers, and evidence
- `progress.md` - rolling session log
- `session-handoff.md` - restart packet for the next session
- `docs/state/current.md` - concise snapshot of current project status
- `docs/state/decisions.md` - durable product, process, architecture, and automation decisions
- Issues / PRs - discussion, review, evidence, work requests, and project-loop receipts
- Commit messages - status messages for changed repo state

Issues and PRs can propose decisions, but final decisions become binding only after being copied into the appropriate tracked authority file.

### Freshness Rule

At session start, pull the latest changes and compare the active specification, `feature_list.json`, `progress.md`, `session-handoff.md`, `docs/state/current.md`, and any active project-loop claim or receipt. If they contradict each other, stop implementation and reconcile state first.

### Evidence Rule

Do not claim `done`, `works`, `fixed`, `tested`, or `verified` without evidence. Evidence must include the exact command or manual check, result, environment, known failures, and relevant commit when available. Write evidence to `feature_list.json`, `progress.md`, `session-handoff.md`, a PR, or a schema-valid project-loop receipt before claiming completion.

### No Hidden Memory

Avoid relying on "as discussed" unless the discussion is linked in an issue/PR or recorded in tracked state. Acknowledgements should create or reference durable state changes.

## Specification-Driven Workflow

### Authority and Approval

1. `spec/` defines product behavior; `feature_list.json` tracks work derived from specs and governance issues.
2. A `draft` spec is discussion material only. Do not start application implementation from it.
3. Only the human owner may approve product behavior or a material change to approved behavior.
4. ChatGPT drafts and curates product specifications, stable requirement IDs, acceptance criteria, and planning fields.
5. Codex may challenge ambiguity or testability in the issue or PR, but must not silently alter approved behavior.
6. Tests provide evidence against a specification; they do not redefine it.

### Feature Derivation

- Preserve existing feature IDs; never silently repurpose them.
- Implementation entries must reference an `approved` or `implemented` file under `spec/features/`.
- Planning fields are `kind`, `name`, `description`, `spec_ref`, `spec_revision`, `requirements`, `acceptance_criteria`, and `dependencies`.
- Execution fields are `status`, `branch`, `pull_request`, `blockers`, and `evidence`.
- Generators and agents must merge planning changes while preserving execution fields and another actor's evidence.
- Governance and product-definition work may have no spec or may point to a draft spec.

### Verification Generation

1. Acceptance criteria are written before implementation and use stable IDs such as `VP-001-AC-001`.
2. ChatGPT may propose verification matrices and test skeletons.
3. Codex reviews generated tests, implements executable verification, and maps tests to acceptance IDs.
4. Generated tests are not evidence until they run in the stated environment.
5. Completed implementation work requires passing evidence for every listed acceptance criterion.
6. Run `python3 scripts/validate_specs.py` and `python3 scripts/check_traceability.py` through `./init.sh` before claiming the harness is healthy.

### Specification Change Control

A change to approved behavior requires a focused PR that lists affected requirements, acceptance criteria, feature entries, tests, migration needs, backward compatibility, and the human decision required.

## Reusable Project Loop Protocol

The harness defines how one agent run works. The project loop is the controller above it: it discovers one eligible item, runs agents inside the harness, verifies the result, publishes durable state, and chooses the next allowed transition. Detailed design lives in `docs/project-loop.md`.

Reusable loop artifacts use generic `project-*` names, including `project-loop.toml`, `.project-loop/`, `.agents/skills/project-loop/`, `.codex/agents/project-verifier.toml`, `scripts/project-loop/`, and `docs/project-loop.md`. Repository-specific values belong in configuration and state, not framework paths.

Loop v1 supports bounded pull-request verification and deterministic repair. Each cycle processes at most one work item in an isolated worktree and follows:

```text
DISCOVER → CLAIM → ISOLATE → RECONCILE → BASELINE
→ VERIFY → REPAIR (bounded) → INDEPENDENT REVIEW
→ RECEIPT → HANDOFF / STOP
```

The maker and checker must be separate; the checker is read-only. Default limits are one work item, one edited branch, and at most three repair attempts. Stop when checks pass, a human decision is needed, the validation delta stops shrinking, scope grows, budgets expire, conflicts appear, permissions are insufficient, or approved behavior would need to change merely to pass a test.

Every non-no-op cycle posts a durable receipt to the issue or PR with run identity, actor/runtime, work item, starting and ending commits, attempts, exact command results, changed files, remaining validation delta, checker result, stop reason, next actor, and known risks. Raw logs may remain under ignored `.project-loop/`, but essential state must be published outside the conversation.

The loop never approves product behavior, merges, deploys, handles secrets, performs destructive operations, or bypasses human-owned decisions unless the human explicitly authorizes the exact action.

Roll out in stages: dry-run selection, read-only verification, bounded deterministic repair, then approved feature implementation only after earlier stages are stable and the human expands scope.

### Commit Message Standard

Use commit messages as concise status packets:

```text
<type>(<scope>): <change>

Why:
- ...

Verified:
- ...

Remaining:
- ...

Actor: <chatgpt|codex|human>
Role: <meta|implementation|owner>
Issue: #<number>
Runtime: <chatgpt-github-connector|dgx-spark|human-local>
```

Avoid vague messages like `update`, `fix stuff`, or `wip`.

## Working Rules

- **One feature at a time**: Work on exactly one active feature from `feature_list.json`
- **One loop item at a time**: A loop cycle may claim at most one issue or PR
- **Eligibility required**: Do not implement product behavior unless its referenced spec is approved
- **Verification required**: Do not claim done without running the required commands and acceptance checks
- **Independent checking required**: Unattended changes require a separate read-only checker
- **No autonomous merge**: Automation stops at the human merge gate
- **Update artifacts**: Before ending a session, update the affected spec or decision file, `feature_list.json`, `progress.md`, `session-handoff.md`, relevant `docs/state/*` files, and the active issue or PR receipt
- **Stay in scope**: Do not modify files unrelated to the active feature or issue
- **Leave clean state**: The next session or loop cycle must be able to run `./init.sh` immediately

## Required Artifacts

- `AGENTS.md` — operating protocol
- `spec/README.md` — specification operating rules
- `spec/product.md` — product scope authority
- `spec/quality.md` — quality authority
- `spec/features/*.md` — feature behavior authority
- `docs/project-loop.md` — reusable project-loop authority
- `docs/protocol/authorization.md` — authorization relay template authority
- `feature_list.json` — derived work and evidence tracker
- `progress.md` — session continuity log
- `init.sh` — standard startup and verification path
- `session-handoff.md` — restart packet for the next session
- `docs/state/current.md` — current project snapshot
- `docs/state/decisions.md` — durable decisions log

## Definition of Done

A feature is done only when ALL applicable conditions are true:

- [ ] Target behavior is implemented
- [ ] Referenced specifications and IDs are valid
- [ ] Required tests, lint, type checks, and manual checks actually ran
- [ ] Every required acceptance criterion has passing evidence
- [ ] Evidence is recorded in `feature_list.json`, `progress.md`, `session-handoff.md`, the PR, or a schema-valid project-loop receipt
- [ ] Relevant state and decision docs are updated
- [ ] Repository remains restartable from the standard startup path

A loop cycle is complete only when it produces a successful no-op or publishes a durable receipt with its result, remaining delta, stop reason, and next actor.

## End of Session

Before ending a session:

1. Update the affected spec only when product truth changed and approval rules were followed
2. Update `feature_list.json` with planning or execution state owned by the actor
3. Update `progress.md` with current state
4. Update `session-handoff.md`
5. Update `docs/state/current.md` and `docs/state/decisions.md` when facts or decisions changed
6. Update the active issue or PR with the loop receipt when automation ran
7. Record unresolved risks, blockers, and specification questions
8. Commit with a descriptive status message once work is in a safe state
9. Leave the repo clean enough for the next session or cycle to run `git pull --ff-only` and `./init.sh` immediately

## Verification Commands

```bash
# Full harness and traceability verification
./init.sh
```

Required specification checks:

```bash
python3 scripts/validate_specs.py
python3 scripts/check_traceability.py
```

Project-loop executable checks must be added only after the Codex-owned implementation issue defines and verifies them. Application verification commands must be added to `init.sh` after the application stack is approved and scaffolded.

## Escalation

If you encounter:
- **Product decisions**: Read draft specs and open questions, then ask the human owner
- **Architecture decisions**: Consult architecture and decision docs, otherwise ask the human owner
- **Unclear requirements**: Comment on the relevant spec issue or PR; do not guess and implement
- **Loop eligibility ambiguity**: Do not claim the item; publish a no-op or blocked receipt
- **Repeated test or repair failures**: Stop at the configured budget, record the validation delta, and flag for human review
- **Scope ambiguity**: Re-read the referenced spec, `feature_list.json`, and `docs/project-loop.md`
- **Contradictory state**: Stop implementation and reconcile tracked authority files first
