# Reset Protocol

Trigger on an event, not a percentage — an agent cannot reliably measure its own fill.

Run this when the harness signals context pressure or auto-compact, before any deliberate history drop, and before handing a session to someone else.

1. **Checkpoint.** Write notes for every T1–T5 trigger that has fired since the last checkpoint.
2. **Verify cold.** Read only `ledger/INDEX.md` plus the shards covering the current scope. Can you name the next concrete step? Every ambiguity is a missing note — write it now.
3. **Reset.** Drop the transcript. Continue from the ledger.
4. **Announce.** State plainly that context was reset and that you are now working from notes. Do not imply continuity you no longer have.

## Offload before resetting

- Tool outputs over ~2k tokens → `.agent_notes/scratch/<name>.md`; keep the path, not the payload.
- Files you have already read or edited → the path is sufficient, it can be re-read.

Step 2 is the step that gets skipped, and it is the entire point. A ledger that has never been read cold has not been tested.
