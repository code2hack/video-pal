# Project Run Receipt

Every project-loop cycle emits one receipt. Raw logs can stay under ignored `.project-loop/`, but this receipt is the durable summary that can be posted to an issue or PR.

Required JSON fields:

- `schema_version`: integer, currently `1`
- `run_id`: unique string for the cycle
- `actor`: maker identity, for example `codex`
- `runtime`: execution environment, for example `DGX Spark`
- `work_item`: selected item object or `null` for a no-op
- `claim`: object with branch, starting commit, and claim timestamp
- `timestamp`: receipt timestamp
- `starting_commit`: repository commit before the cycle
- `ending_commit`: repository commit after the cycle, or `null`
- `attempts`: integer attempt count
- `commands`: list of exact commands and exit results
- `changed_files`: list of paths changed by the cycle
- `validation_delta`: normalized rejection reasons, failures, or remaining findings
- `checker_result`: `not-run`, `pass`, `fail`, `error`, or `unavailable`
- `stop_reason`: exact terminal reason
- `next_actor`: who should act next
- `known_risks`: list of remaining risks

Stage 0 receipts use `attempts: 0`, `changed_files: []`, and either `stop_reason: "stage0-selected"` or `stop_reason: "no-eligible-work"`.

Repair receipts must state the stop reason explicitly, such as `repair-disabled`, `unchanged-validation-delta`, `attempt-limit-reached`, or `unexpected-changed-file`.
