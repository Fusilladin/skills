# Audit Mode

Read-only. Use when inheriting a session, or when ledger drift is suspected. Report first, repair second.

## Verdict per ACTIVE note

| Verdict | Meaning |
|---|---|
| VERIFIED | evidence re-checked against current repo state; still true |
| STALE | was true; the underlying code or config has since changed |
| UNSUPPORTED | no reproducible evidence; may be a hallucinated fact |
| ORPHANED | governs a file or subsystem that no longer exists |

`SUPERSEDED` is a STATUS, not an audit verdict. A note that is superseded but still marked ACTIVE is a hygiene bug — report it as such rather than as a verdict.

## Rules

- Default to VERIFIED only on positive re-confirmation, never on absence of contradiction.
- UNSUPPORTED is the highest-severity finding. It means a prior agent wrote down something that was never true.
- Report as a table: NOTE ID | verdict | evidence checked | recommended action.
- If more than roughly 20% of ACTIVE notes come back STALE or UNSUPPORTED, the ledger is not a trustworthy handoff artifact. Rebuild it from current repo state rather than patching it.

## Repair pass (only after reporting)

For each STALE or ORPHANED note, write a replacement note with `SUPERSEDES` pointing at the old ID, then flip the old one to SUPERSEDED. For each UNSUPPORTED note, set it to REFUTED with the evidence that failed. Never delete.
