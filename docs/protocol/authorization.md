# Authorization Relay Protocol

This document provides reusable templates for human authorization relay and privileged-operation escalation.

The binding rules live in `AGENTS.md`; this file keeps packet formats and examples in one generic protocol location.

## Approval IDs

Use scoped approval IDs:

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

Use distinct packets for implementation-stage approval, privileged-command approval, merge approval, and product or architecture approval.

## Human Authorization Relay Template

````md
## Human Authorization Relay

Approval-ID: HA-YYYYMMDD-ISSUE<N>-<SCOPE>-NN
Decision-Owner: human
Recorded-By: chatgpt:<role>
ChatGPT-Session: <session-id-or-not-recorded>
Issue-or-PR: #<number>
Branch: <branch-or-null>
Authorized-Executor: codex:<role>

Approved scope:
- ...

Not authorized:
- ...

Conditions:
- ...

Expiry / invalidation:
- ...

Status: approved
````

## Privileged Operation Request Template

````md
## Privileged Operation Request

Request-ID: SUDO-YYYYMMDD-ISSUE<N>-NN
Actor: codex:<role>
Session: <codex-session-id>
Issue-or-PR: #<number>
Branch: <branch>

Exact commands:
```bash
sudo apt-get update
sudo apt-get install -y <package>
```

Reason:
- ...

Expected system changes:
- ...

Network access:
- ...

Rollback:
```bash
...
```

Alternatives considered:
- ...

Why alternatives are not being used:
- ...

Next actor: chatgpt
````

## Privileged Operation Approval Template

````md
## Human Authorization Relay - Privileged Operation

Approval-ID: HA-YYYYMMDD-ISSUE<N>-SUDO-NN
Request-ID: SUDO-YYYYMMDD-ISSUE<N>-NN
Decision-Owner: human
Recorded-By: chatgpt:<role>
Authorized-Executor: codex:<role>
Issue-or-PR: #<number>
Branch: <branch>

Approved exact commands:
```bash
...
```

Not authorized:
- any command not listed above
- password piping or `sudo -S`
- sudoers changes
- group membership changes
- persistent privilege escalation
- user-level fallback substitutions unless separately approved

Conditions:
- human may need to enter the sudo password directly on the DGX Spark
- Codex must record exact command output, package versions, and resulting verification evidence

Status: approved
Single-use: true
````
