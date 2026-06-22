# AGENTS.md

Project harness for reliable agent-assisted development. The repository is the shared memory bus for the human owner, ChatGPT, and Codex.

## Startup Workflow

Before writing code:

1. **Confirm working directory** with `pwd`
2. **Sync repo state** with `git pull --ff-only` when a remote is configured
3. **Read this file** completely
4. **Read current state**: `feature_list.json`, `progress.md`, `session-handoff.md`, `docs/state/current.md`, and `docs/state/decisions.md`
5. **Read specification authority**: `spec/README.md`, `spec/product.md`, `spec/quality.md`, and every spec referenced by the active feature
6. **Review recent commits** with `git log --oneline -20`
7. **Review the active issue and PR**, including unresolved comments and verification requests
8. **Run `./init.sh`** to verify the environment and specification traceability
9. **Reconcile contradictions** between tracked state files before implementation

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
- **ChatGPT**: planning, specification drafting, acceptance criteria, review, architecture discussion, requirements clarification, consistency checks, and GitHub-facing stewardship
- **Codex**: local implementation, executable tests, commands, DGX Spark verification, refactors, commits, and pushes

Neither AI agent owns product direction. If agents disagree, check this file, approved specifications, feature definitions, decision docs, and existing code, then present tradeoffs for the human owner to decide.

### Durable State Files

- `AGENTS.md` - stable operating protocol and invariants
- `spec/README.md` - specification authority, lifecycle, IDs, and derivation rules
- `spec/product.md` - product scope and non-goals
- `spec/quality.md` - cross-cutting quality requirements
- `spec/features/*.md` - feature behavior and acceptance criteria
- `feature_list.json` - derived feature state, dependencies, traceability, blockers, and evidence
- `progress.md` - rolling session log
- `session-handoff.md` - restart packet for the next session
- `docs/state/current.md` - concise snapshot of current project status
- `docs/state/decisions.md` - durable product, process, and architecture decisions
- Issues / PRs - discussion, review, evidence, and work requests
- Commit messages - status messages for changed repo state

Issues and PRs can propose decisions, but final decisions become binding only after being copied into the appropriate tracked authority file.

### Freshness Rule

At session start, pull the latest changes and compare the active specification, `feature_list.json`, `progress.md`, `session-handoff.md`, and `docs/state/current.md`. If they contradict each other, stop implementation and reconcile state first.

### Evidence Rule

Do not claim `done`, `works`, `fixed`, `tested`, or `verified` without evidence. Evidence must include the exact command or manual check, result, environment, known failures, and relevant commit when available. Write evidence to `feature_list.json`, `progress.md`, `session-handoff.md`, or a PR before claiming completion.

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
```

Avoid vague messages like `update`, `fix stuff`, or `wip`.

## Working Rules

- **One feature at a time**: Work on exactly one active feature from `feature_list.json`
- **Eligibility required**: Do not implement product behavior unless its referenced spec is approved
- **Verification required**: Do not claim done without running the required commands and acceptance checks
- **Update artifacts**: Before ending a session, update the affected spec or decision file, `feature_list.json`, `progress.md`, `session-handoff.md`, and relevant `docs/state/*` files
- **Stay in scope**: Do not modify files unrelated to the active feature or issue
- **Leave clean state**: The next session must be able to run `./init.sh` immediately

## Required Artifacts

- `AGENTS.md` — operating protocol
- `spec/README.md` — specification operating rules
- `spec/product.md` — product scope authority
- `spec/quality.md` — quality authority
- `spec/features/*.md` — feature behavior authority
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
- [ ] Evidence is recorded in `feature_list.json`, `progress.md`, `session-handoff.md`, or the PR
- [ ] Relevant state and decision docs are updated
- [ ] Repository remains restartable from the standard startup path

## End of Session

Before ending a session:

1. Update the affected spec only when product truth changed and approval rules were followed
2. Update `feature_list.json` with planning or execution state owned by the actor
3. Update `progress.md` with current state
4. Update `session-handoff.md`
5. Update `docs/state/current.md` and `docs/state/decisions.md` when facts or decisions changed
6. Record unresolved risks, blockers, and specification questions
7. Commit with a descriptive status message once work is in a safe state
8. Leave the repo clean enough for the next session to run `git pull --ff-only` and `./init.sh` immediately

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

Application verification commands must be added to `init.sh` after the application stack is approved and scaffolded.

## Escalation

If you encounter:
- **Product decisions**: Read draft specs and open questions, then ask the human owner
- **Architecture decisions**: Consult architecture and decision docs, otherwise ask the human owner
- **Unclear requirements**: Comment on the relevant spec issue or PR; do not guess and implement
- **Repeated test failures**: Update evidence and progress, then flag for human review
- **Scope ambiguity**: Re-read the referenced spec and `feature_list.json`
- **Contradictory state**: Stop implementation and reconcile tracked authority files first
