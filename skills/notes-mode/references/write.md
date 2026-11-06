# When to Write

## Mandatory — write at the moment of the event

- **T1** A decision was made that constrains future work.
- **T2** An approach was tried and failed. Record the reason, not just the error.
- **T3** A non-obvious fact surfaced: naming convention, implicit ordering requirement, undocumented side effect.
- **T4** The user stated a constraint they will not restate.
- **T5** A file, module, or approach was explicitly ruled out.
- **T6** A context reset or compaction is imminent → `reset.md`.
- **T7** A subagent is about to be spawned, or has returned → `handoff.md`.

## Never write

- Routine reads and greps, or anything re-derivable in one command.
- Restatements of code that exists on disk, or of anything git already records.
- Transient tool output that will be stale immediately.
- Anything that will not change a future decision. If you cannot name the decision it changes, it does not belong in the ledger.

## Budget

Target 60 or fewer ACTIVE notes repository-wide. Past that it has stopped being a ledger: archive the REFUTED and SUPERSEDED shards rather than continuing to append.
