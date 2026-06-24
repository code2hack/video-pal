# Video Pal Specification System

The `spec/` directory is the durable product-behavior contract shared by the human owner, ChatGPT, and Codex. Specifications define **what must be true**. They do not record transient work status, implementation details, or unapproved chat ideas.

## Authority by artifact

| Artifact | Authority |
|---|---|
| `AGENTS.md` | Collaboration process, roles, Git workflow, and harness rules |
| `spec/product.md` | Product vision, users, release scope, and non-goals |
| `spec/features/*.md` | Feature behavior, requirements, acceptance criteria, and edge cases |
| `spec/quality.md` | Cross-cutting privacy, performance, reliability, portability, security, and usability expectations |
| `docs/architecture*` and `docs/state/decisions.md` | Architecture and accepted-decision rationale |
| `feature_list.json` | Derived work decomposition, dependencies, execution state, blockers, and evidence |
| Tests and recorded commands | Executable verification evidence |

When artifacts disagree, use the authority for the affected domain:

- an approved feature spec outranks `feature_list.json` for required behavior;
- `feature_list.json` outranks progress prose for current execution state;
- tests are evidence but do not silently redefine an approved specification;
- chat-only statements are provisional until recorded through Git.

## Required files

The minimum specification set is:

```text
spec/
├── README.md
├── product.md
├── quality.md
├── features/
│   └── VP-001-mvp.md
└── templates/
    └── feature-spec.md
```

Create machine-readable contracts such as OpenAPI or JSON Schema only when a real interface needs them. Do not add speculative contract files.

## Lifecycle

Every normative specification uses one status:

- `draft` — under discussion; implementation must not start from it.
- `approved` — explicitly approved by the human owner and eligible for feature decomposition and implementation.
- `implemented` — every acceptance criterion has recorded verification evidence.
- `superseded` — replaced by another identified specification or revision.

Rules:

1. Only the human owner can authorize `draft → approved`.
2. ChatGPT may draft and refine specifications but cannot silently approve product behavior.
3. Codex may challenge ambiguity or testability through an issue or PR but cannot silently change approved behavior.
4. `approved` and `implemented` documents require a non-null `approval_ref`.
5. `superseded` documents require `superseded_by`.
6. Material changes to approved behavior require a focused PR, impact analysis, and renewed human approval.

## Stable identifiers

Identifiers are permanent traceability keys:

- feature specification: `VP-NNN`, for example `VP-001`;
- functional requirement: `VP-NNN-REQ-NNN`;
- acceptance criterion: `VP-NNN-AC-NNN`;
- cross-cutting quality requirement: `QUAL-NNN`.

Do not reuse or renumber an identifier after it appears in merged history, an issue, PR, feature entry, test, or evidence record. Retire obsolete identifiers with an explanation instead.

## Front matter

Feature specifications use constrained YAML-style front matter that the repository validator can parse without third-party dependencies:

```yaml
---
id: VP-001
title: Example feature
status: draft
revision: 1
decision_owner: human
approval_ref: null
depends_on: []
supersedes: []
superseded_by: null
---
```

Use JSON-compatible inline lists, quoted strings when needed, integers, booleans, or `null`. Do not place nested mappings in front matter.

## Required feature sections

Every `spec/features/*.md` document contains:

1. Problem
2. Goals
3. Non-goals
4. Functional requirements
5. Acceptance criteria
6. Edge cases
7. Verification matrix
8. Open questions

Draft specs may leave normative requirement and acceptance IDs undefined. An approved spec must define at least one requirement and one acceptance criterion and must not contain unresolved `TBD` markers.

## Deriving `feature_list.json`

`feature_list.json` is maintained from approved specifications and governance issues. It is not a replacement for product specifications.

Planning fields are normally curated by ChatGPT:

- `kind`
- `name`
- `description`
- `spec_ref`
- `spec_revision`
- `requirements`
- `acceptance_criteria`
- `dependencies`

Execution fields are updated by the actor doing the work, normally Codex for implementation:

- `status`
- `branch`
- `pull_request`
- `blockers`
- `evidence`

Any future generator must **merge** planning fields and preserve execution fields. It must never regenerate the whole file in a way that erases status, blockers, branches, PR references, or evidence.

Governance, documentation, handoff, and product-definition work may have `spec_ref: null` or may point to a draft spec. Entries with `kind: "implementation"` must reference an `approved` or `implemented` feature spec.

## Verification traceability

Tests and manual checks should identify the acceptance criterion they verify, for example `VP-001-AC-001`.

For a completed implementation feature:

- every listed acceptance criterion must exist in the referenced spec;
- every listed acceptance criterion must have passing evidence;
- evidence records must include the exact command or manual check, result, environment, relevant commit when available, and known limitations;
- generated test skeletons must be reviewed by Codex and must not be treated as evidence until executed.

## Change control

A PR that changes an approved specification must state:

```text
Affected requirements:
Affected acceptance criteria:
Affected feature-list entries:
Affected tests:
Migration required:
Backward compatibility:
Human decision required:
```

Do not mix unrelated application implementation into a specification-governance PR.

## Standard workflow

1. Human product intent is recorded as a draft.
2. ChatGPT drafts or refines requirements, acceptance criteria, edge cases, and unresolved choices.
3. Human approves product behavior and material constraints.
4. ChatGPT derives planning fields in `feature_list.json`.
5. Codex implements one eligible feature on a `codex/...` branch.
6. Codex maps tests to acceptance IDs and records exact DGX Spark evidence.
7. ChatGPT reviews requirement → feature → test → evidence traceability.
8. Human authorizes merge.
