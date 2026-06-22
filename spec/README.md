# Video Pal Specification System

`spec/` is the product-behavior authority shared by the human owner, ChatGPT, and Codex.

## Authority

- `AGENTS.md`: collaboration process.
- `spec/product.md`: product scope and non-goals.
- `spec/features/*.md`: behavior and acceptance criteria.
- `spec/quality.md`: cross-cutting quality requirements.
- `docs/**`: architecture and decision rationale.
- `feature_list.json`: derived execution state and evidence.

Approved specs control behavior. Tests prove behavior but do not redefine it.

## Lifecycle

- `draft`: discussion only; do not implement.
- `approved`: human-approved and eligible for implementation.
- `implemented`: every acceptance criterion has evidence.
- `superseded`: replaced by another named spec or revision.

Only the human owner approves product behavior. Material changes require a focused PR and renewed approval.

## IDs

Use stable `VP-NNN`, `VP-NNN-REQ-NNN`, `VP-NNN-AC-NNN`, and `QUAL-NNN` identifiers. Never reuse an ID.

## Derivation and verification

ChatGPT curates planning fields in `feature_list.json`. The working actor updates status, branch, PR, blockers, and evidence. Generators must preserve execution fields. Implementation requires an approved spec. Codex reviews and runs generated tests, records exact DGX Spark evidence, and ChatGPT reviews traceability.

## Change control

A change to approved behavior must identify affected requirements, criteria, features, tests, migration, compatibility, and the human decision required.
