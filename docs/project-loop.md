# Reusable Project Loop Protocol

This document defines a reusable automation layer that sits above a repository's agent harness. It is intentionally product-agnostic so it can be copied into future projects without renaming framework paths.

## 1. Harness versus loop

The **project harness** is the environment and rule set one agent works inside:

- `AGENTS.md`
- specifications and acceptance criteria
- repository conventions
- verification commands
- Git and pull-request workflow
- state, decisions, evidence, and handoff files

The **project loop** is the controller above the harness. It repeatedly:

1. discovers one eligible work item;
2. claims it without colliding with another actor;
3. creates an isolated worktree;
4. invokes the maker inside the harness;
5. invokes an independent checker;
6. records evidence and remaining work;
7. chooses the next allowed transition;
8. stops at a human gate or terminal condition.

The harness makes one run reliable. The loop makes reliable runs repeatable.

## 2. Portable naming contract

Reusable harness and loop artifacts must use `project-*` names rather than a product or repository name.

Recommended layout:

```text
project-loop.toml
.project-loop/
.agents/
└── skills/
    └── project-loop/
        ├── SKILL.md
        └── references/
            └── project-run-receipt.md
.codex/
└── agents/
    └── project-verifier.toml
scripts/
└── project-loop/
    ├── select_work.py
    ├── run_cycle.sh
    └── validate_receipt.py
docs/
└── project-loop.md
```

Rules:

- Do not embed a product name in a reusable harness or loop path.
- Repository-specific values belong in `project-loop.toml`, specifications, state files, issues, and pull requests.
- Raw run data belongs under ignored `.project-loop/`.
- Essential state must also be published to the relevant issue, pull request, or tracked project state.
- Product source files and product specifications may retain product-specific names when the name is genuinely part of product truth.

## 3. Initial supported workflow

Version 1 supports **bounded pull-request verification and deterministic repair**.

It does not autonomously invent product scope, approve specifications, merge pull requests, deploy software, handle secrets, or perform destructive operations.

A successful first implementation should be able to:

- identify one explicitly eligible pull request;
- verify it in an isolated worktree;
- ask a separate read-only verifier to inspect it;
- repair deterministic failures within a bounded attempt budget;
- publish a durable run receipt;
- stop at the human merge gate.

## 4. State machine

One cycle follows this state machine:

```text
DISCOVER
  ↓
CLAIM
  ↓
ISOLATE
  ↓
RECONCILE
  ↓
BASELINE
  ↓
VERIFY
  ├── pass ───────────────→ INDEPENDENT_REVIEW
  ├── repairable failure ─→ REPAIR ─→ VERIFY
  └── human decision ─────→ RECEIPT

INDEPENDENT_REVIEW
  ├── pass ───────────────→ RECEIPT
  ├── repairable finding ─→ REPAIR ─→ VERIFY
  └── human decision ─────→ RECEIPT

RECEIPT
  ↓
HANDOFF / STOP
```

A scheduled automation runs another bounded cycle later. A single cycle is not an unbounded process.

## 5. Work eligibility

The selector processes at most one work item per cycle.

A pull request is eligible only when all required conditions hold:

- it carries the configured ready label or explicit issue/PR marker;
- its linked issue or governance acceptance criteria are clear;
- product implementation, when applicable, references an approved specification;
- declared dependencies are complete;
- no unresolved human decision blocks execution;
- no other active loop run owns the same work item;
- no conflicting active branch or primary writer exists;
- the requested actions fit the configured permission and budget envelope.

If no item is eligible, the cycle returns a successful no-op receipt and stops.

The selector must be deterministic where possible. It may use an agent to summarize candidates, but final eligibility gates must be machine-checkable or explicitly human-approved.

## 6. Claiming and concurrency

Before editing, the controller records a claim containing:

- run ID;
- issue or pull-request number;
- branch and starting commit;
- actor and runtime;
- claim timestamp;
- expiration or heartbeat rule.

The claim may be represented by a GitHub label/comment, a repository lock record, or both. A stale claim must not be silently stolen; record the recovery reason.

Use one issue, one focused branch, and one primary writer. Multiple read-only checkers may inspect the same work, but only one maker edits it during a cycle.

## 7. Worktree isolation

Every modifying run uses a dedicated Git worktree and an actor-prefixed branch.

The controller must:

1. fetch the relevant remote refs;
2. confirm the expected starting commit;
3. create an isolated worktree;
4. verify that it is not `main` or another protected branch;
5. run startup and baseline checks before editing;
6. remove or archive the worktree according to the configured retention policy.

A worktree prevents file collisions but does not eliminate merge or review conflicts. The loop must still check for overlapping branches and active writers.

## 8. Reconciliation and baseline

Before repair or implementation, the maker reads:

- `AGENTS.md` completely;
- the active issue and pull request;
- relevant specifications and acceptance criteria;
- `feature_list.json`;
- current state, decisions, progress, and handoff files;
- recent commits and changed files.

The cycle stops if tracked authorities contradict one another and the contradiction cannot be resolved without a human decision.

Baseline verification runs before edits. This distinguishes pre-existing failures from failures introduced by the current cycle.

## 9. Maker and checker separation

The maker and checker have different responsibilities.

### Maker

The maker may:

- inspect the work item;
- make the smallest change that reduces the recorded validation delta;
- run approved commands;
- update owned execution state and evidence;
- commit and push to the work branch when allowed.

The maker may not grade its own work as finally accepted.

### Checker

The checker is a separate read-only agent with separate instructions. It verifies:

- conformance to `AGENTS.md`;
- conformance to approved specifications;
- acceptance-criterion coverage;
- changed-file scope;
- test and command evidence;
- unsupported claims;
- remaining risks and human decisions.

The checker must not edit files, approve product behavior, merge, deploy, or suppress a failure merely because the maker believes it is acceptable.

## 10. Bounded repair policy

Default repair budget:

```text
maximum attempts: 3
maximum work items per cycle: 1
maximum branches edited per cycle: 1
```

Each repair attempt must address the current recorded validation delta. Prefer the smallest change that can make a failing deterministic check pass.

Stop immediately when:

- all required checks and checker findings pass;
- a product, architecture, security, deployment, or merge decision requires the human owner;
- the same validation delta remains unchanged after an attempt;
- the delta grows unexpectedly or scope expands;
- the maximum attempt, time, token, or command budget is exhausted;
- the branch has conflicts or moved unexpectedly;
- unexpected files changed;
- the required permission exceeds the configured sandbox;
- secrets or destructive operations would be involved;
- approved behavior would need to change merely to make tests pass.

Do not disguise a stop as success. Publish the exact stop reason and next actor.

## 11. Verification delta

The loop tracks a normalized **validation delta** rather than vague progress.

It may contain:

- failing commands;
- failed acceptance criteria;
- checker findings;
- missing evidence;
- scope violations;
- state contradictions;
- merge conflicts;
- human decisions required.

A repair attempt is useful only when it removes, narrows, or provides decisive evidence about one or more delta items.

## 12. Human gates

The loop may prepare evidence and recommendations, but the human owner controls:

- product scope and acceptance;
- material specification changes;
- architecture approval;
- secrets and credentials;
- deployment;
- destructive operations;
- exceptions to governance rules;
- final merge authorization.

The loop must stop before these transitions unless the human explicitly authorizes the exact action.

## 13. Durable run receipt

Every non-no-op cycle posts a structured receipt to the relevant issue or pull request.

Minimum fields:

```json
{
  "schema_version": 1,
  "run_id": "2026-06-22T09:00:00Z-pr-123",
  "actor": "codex",
  "runtime": "project-local",
  "work_item": {
    "type": "pull_request",
    "number": 123
  },
  "claim": {
    "starting_commit": "abc1234",
    "branch": "codex/123-example"
  },
  "attempts": 2,
  "commands": [
    {
      "command": "./init.sh",
      "exit_code": 0,
      "summary": "passed"
    }
  ],
  "ending_commit": "def5678",
  "changed_files": [],
  "remaining_delta": [],
  "checker_result": "pass",
  "stop_reason": "human-merge-authorization-required",
  "next_actor": "human",
  "known_risks": []
}
```

The receipt must distinguish observed command results from agent inferences.

Raw transcripts and JSONL logs may remain under ignored `.project-loop/runs/`. The issue or pull request receipt is the durable cross-session summary.

## 14. Suggested GitHub states

Suggested labels or equivalent state markers:

```text
needs:spec
needs:human-approval
ready:project-loop
project-loop:running
needs:verification
needs:chatgpt-review
needs:human-merge
blocked
done
```

Label creation and transition policy should be configurable. Do not hard-code repository-specific labels into reusable scripts when configuration can express them.

## 15. Configuration contract

`project-loop.toml` should hold project-local settings such as:

- repository name and default branch;
- eligible labels and terminal labels;
- protected paths and branches;
- startup and verification commands;
- attempt, time, token, and command budgets;
- worktree root and retention;
- permitted issue/PR mutations;
- maker and checker definitions;
- receipt schema version;
- dry-run versus modifying mode.

Do not place secrets in this file. Refer to environment variables or an approved secret manager.

## 16. Implementation layout

Codex should implement the local controller using generic paths:

```text
.agents/skills/project-loop/SKILL.md
.codex/agents/project-verifier.toml
scripts/project-loop/select_work.py
scripts/project-loop/run_cycle.sh
scripts/project-loop/validate_receipt.py
project-loop.toml
```

Optional additions must also use generic `project-*` names.

The skill contains agent-facing workflow instructions. Scripts own deterministic selection, budgets, command execution, receipt validation, and exit codes. The verifier agent remains read-only.

## 17. Rollout stages

### Stage 0 — Dry-run selector

- inspect GitHub and repository state;
- select or reject one candidate;
- publish no changes;
- explain eligibility decisions.

### Stage 1 — Read-only verification

- create isolated worktree;
- run baseline and verification commands;
- invoke the checker;
- publish a receipt;
- make no file edits.

### Stage 2 — Deterministic repair

- permit workspace edits on an existing branch;
- limit repairs to three attempts;
- rerun verification and checker after every repair;
- never merge.

### Stage 3 — Approved feature implementation

- select only features derived from approved specifications;
- create an actor-prefixed branch and draft pull request;
- implement, verify, review, and hand off;
- stop at human merge authorization.

Do not begin Stage 3 until Stages 0–2 are stable and the human owner explicitly approves expansion.

## 18. Portability checklist

Before copying the loop into another project:

- retain generic `project-*` paths;
- replace only configuration values and product specifications;
- preserve bounded attempts and human gates;
- confirm the new repository's `AGENTS.md` and verification entrypoint;
- validate branch protection and connector permissions;
- begin in dry-run mode;
- verify that maker and checker are distinct;
- ensure essential memory is published outside agent conversations.

## 19. Definition of done for Loop v1

Loop v1 is complete only when evidence shows that it can:

1. select at most one explicitly eligible pull request;
2. run in an isolated worktree;
3. execute the repository startup/verification path;
4. invoke a separate read-only checker;
5. perform or decline bounded deterministic repairs according to policy;
6. publish a schema-valid durable receipt;
7. return a successful no-op when no work is eligible;
8. stop before merge or any human-owned decision;
9. resume a later cycle from repository and GitHub state without chat memory.
