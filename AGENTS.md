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

- **Human owner**: product direction, final authority, scope approval, secrets, deployment decisions
- **ChatGPT**: planning, review, architecture discussion, requirements clarification, consistency checks, GitHub-facing stewardship
- **Codex**: local implementation, file edits, commands/tests, refactors, commits, pushes

Neither AI agent owns product direction. If agents disagree, check this file, feature definitions, decision docs, existing code, then present tradeoffs for the human owner to decide.

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
