# Subagent Handoff Contract

Prose is a lossy summary by construction. A handoff of notes is not.

## The subagent MUST return, in this order

1. `NOTES_WRITTEN` — IDs it created or updated.
2. `FILES_TOUCHED` — paths modified, created, deleted.
3. `VERDICT` — COMPLETE | PARTIAL | BLOCKED | FAILED.
4. `BLOCKERS` — for PARTIAL or BLOCKED: the specific unresolved item plus the evidence for it. "Needs follow-up" is not an answer.
5. `OPEN_QUESTIONS` — assumptions it made that it never verified.

Every abandoned approach must already exist as a `REFUTED` note carrying its reason. If it is not in the ledger, it did not happen. There is deliberately no separate DO_NOT_RETRY field — that job belongs to the ledger.

## Subagent rules

- Its findings ARE the notes. It must not also summarize them into prose for the parent.
- It must never claim context it does not have. If it did not read a file, it does not know what is in it.
- Namespace note IDs when concurrency is possible: `N014/explore`.
- A return missing any of the five fields has failed the contract, even if the code changes are correct.

## Parent rules

- Reconcile the returned IDs against the ledger and confirm they exist.
- On PARTIAL or BLOCKED, re-spawn with the narrower blocker from field 4 — never with a broader prompt.
- On FAILED, read the relevant REFUTED notes before re-spawning anything.

Put this contract in the subagent's task prompt text. A subagent cannot inherit it from your context.
