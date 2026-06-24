# AGENTS.md

Project harness for reliable agent-assisted development. The repository is the shared memory bus for the human owner, ChatGPT, and Codex.

## Startup Workflow

Before writing code:

1. **Confirm working directory** with `pwd`
2. **Sync repo state** with `git pull --ff-only` when a remote is configured
3. **Read this file** completely
4. **Read current state**: `feature_list.json`, `progress.md`, `session-handoff.md`, `docs/state/current.md`, and `docs/state/decisions.md`
5. **Review recent commits** with `git log --oneline -20`
6. **Run `./init.sh`** to verify environment is healthy
7. **Reconcile contradictions** between tracked state files before implementation

If baseline verification is failing, repair that first before adding new scope.

## Agent Communication Protocol

### Source of Truth

Do not rely on chat history as durable memory. Truth priority is:

1. Repository files
2. Git history
3. Issues and PRs
4. Current session chat
5. Agent assumptions

If a decision exists only in chat, it is provisional. Record binding decisions in tracked files.

### Role Boundaries

- **Human owner**: product direction, final authority, scope approval, secrets, deployment decisions, and merge approval
- **ChatGPT**: planning, review, architecture discussion, requirements clarification, consistency checks, harness maintenance, and GitHub-facing stewardship
- **Codex**: local implementation on DGX Spark, file edits, commands/tests, refactors, commits, and pushes

Neither AI agent owns product direction. If agents disagree, check this file, feature definitions, decision docs, existing code, then present tradeoffs for the human owner to decide.

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

### Durable State Files

- `AGENTS.md` - stable operating protocol and invariants
- `feature_list.json` - feature status, dependencies, acceptance criteria, and completion evidence
- `progress.md` - rolling session log
- `session-handoff.md` - restart packet for the next session
- `docs/state/current.md` - concise snapshot of current project status
- `docs/state/decisions.md` - durable product and architecture decisions
- Issues / PRs - discussion, review, and work requests
- Commit messages - status messages for changed repo state

Issues and PRs can propose decisions, but final decisions become binding only after being copied into tracked repo files.

### Freshness Rule

At session start, pull latest changes and compare `feature_list.json`, `progress.md`, `session-handoff.md`, and `docs/state/current.md`. If they contradict each other, stop implementation and reconcile state first.

### Evidence Rule

Do not claim `done`, `works`, or `fixed` without evidence. Evidence must include the command or manual check, result, and any known failures or environmental assumptions. Write evidence to `progress.md`, `feature_list.json`, `session-handoff.md`, or a PR before claiming completion.

### No Hidden Memory

Avoid relying on "as discussed" unless the discussion is linked in an issue/PR or recorded in tracked state. Acknowledgements should create or reference durable state changes.

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

- **One feature at a time**: Pick exactly one unfinished feature from `feature_list.json`
- **Verification required**: Don't claim done without running verification commands
- **Update artifacts**: Before ending session, update `progress.md`, `feature_list.json`, `session-handoff.md`, and relevant `docs/state/*` files
- **Stay in scope**: Don't modify files unrelated to the current feature
- **Leave clean state**: Next session must be able to run `./init.sh` immediately

## Required Artifacts

- `feature_list.json` — Feature state tracker (source of truth)
- `progress.md` — Session continuity log
- `init.sh` — Standard startup and verification path
- `session-handoff.md` — Restart packet for the next session
- `docs/state/current.md` — Current project snapshot
- `docs/state/decisions.md` — Durable decisions log

## Definition of Done

A feature is done only when ALL of the following are true:

- [ ] Target behavior is implemented
- [ ] Required verification actually ran (tests / lint / type-check)
- [ ] Evidence recorded in `feature_list.json`, `progress.md`, `session-handoff.md`, or PR
- [ ] Relevant state and decision docs are updated
- [ ] Repository remains restartable from standard startup path

## End of Session

Before ending a session:

1. Update `progress.md` with current state
2. Update `feature_list.json` with new feature status
3. Update `session-handoff.md`
4. Update `docs/state/current.md` and `docs/state/decisions.md` when facts or decisions changed
5. Record any unresolved risks or blockers
6. Commit with a descriptive status message once work is in safe state
7. Leave repo clean enough for next session to run `git pull --ff-only` and `./init.sh` immediately

## Verification Commands

```bash
# Full verification (recommended)
./init.sh
```

Required checks:
- `echo "No package manifest detected; replace this line with your project verification command."`

## Escalation

If you encounter:
- **Architecture decisions**: Consult project architecture docs if present, otherwise ask user
- **Unclear requirements**: Check product/requirements docs if present, otherwise ask user
- **Repeated test failures**: Update progress, flag for human review
- **Scope ambiguity**: Re-read `feature_list.json` for definition of done
