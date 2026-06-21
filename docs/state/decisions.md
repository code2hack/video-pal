# Decisions

Last updated: 2026-06-21 16:02 CST

## Accepted

### Repository is the shared memory bus

Future collaboration between the human owner, ChatGPT, and Codex must persist through tracked files, git history, issues, and PRs. Chat history alone is not durable project memory.

### Source-of-truth order

1. Repository files
2. Git history
3. Issues and PRs
4. Current session chat
5. Agent assumptions

### Role boundaries

- Human owner owns product direction and final decisions.
- ChatGPT plans, reviews, clarifies requirements, and stewards GitHub discussion.
- Codex implements locally, edits files, runs commands, verifies, commits, and pushes.

### Evidence over claims

Agents must record verification evidence before claiming work is done. Evidence belongs in tracked state files, commits, PRs, or issues.

## Pending

### Video Pal product architecture

No app stack or product architecture has been selected yet.

### Verification commands

`init.sh` still contains a generic placeholder because no package manifest or app scaffold exists.
