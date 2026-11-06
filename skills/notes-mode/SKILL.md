---
name: notes-mode
description: Durable external ledger for long agent sessions. Use when a session spans many steps or approaches a context reset/compaction, when inheriting or auditing a prior session's notes, or when spawning subagents that must hand back findings. Replaces lossy transcript summarization with a rationale-preserving ledger. Invoke as $notes-mode.
disable-model-invocation: true
---

# Notes Mode

**Ledger discipline.** Context is a finite budget. Rationale is the only thing you cannot re-derive by reading the code, so rationale goes in a ledger outside the window and gets re-read on demand. Never act on a fact you did not read from that ledger — say you do not have it.

## Ledger

Root: `.agent_notes/ledger/`

| Need | Command |
|---|---|
| Which shard governs this module | `grep -in "<module-or-filename>" .agent_notes/ledger/INDEX.md` |
| Full detail for a scope | `grep -rl "<scope>" .agent_notes/ledger/` then read that one file |
| History of a specific claim | `grep -n "N0<id>" .agent_notes/ledger/` |

Never `cat` the whole ledger. `INDEX.md` is the only shard you may read in full; everything else is reached by grep.

## Rules

1. Before non-trivial work in an unfamiliar area, grep the ledger for that scope. Do it even when the task looks small.
2. Cite the note ID when a note changes your approach. An uncited note changed nothing.
3. Write the note at the moment of the event, not afterwards. Reconstructed notes capture only what already survived.
4. Record a failed approach with its reason. A failure without a reason gets retried.
5. Correct by superseding. Never delete a prior claim or edit it silently.

## Dispatch — load only what this turn needs

| Need | Read |
|---|---|
| Write or format a note | `references/schema.md`, `references/write.md` |
| Hand off to, or receive from, a subagent | `references/handoff.md` |
| Context reset or compaction checkpoint | `references/reset.md` |
| Inherited or drifted ledger | `references/audit.md` |
| Codex context-management features | `references/codex.md` |
| Why the protocol is shaped this way | `references/rationale.md` |

## Standing constraints

- One ledger per repository, at `.agent_notes/ledger/`. Never a second copy.
- This file is a cached prompt prefix: keep it byte-stable and never edit it mid-session. Changes take effect next session.
- Tool outputs over ~2k tokens: write the payload to `.agent_notes/scratch/<name>.md`, keep the path in context, not the payload.
- Ledger edits are commits. Provenance comes from `git log`, so notes carry no DATE field.
- Rationale beats results. Results are re-derivable from the repo; rationale is not.

Again: read the ledger before acting, and never act on a fact you have not read from it.
