# Why Notes Mode Is Shaped This Way

Not needed at runtime. Read this when auditing a ledger, designing around the protocol, or deciding whether a rule still earns its place.

## The loss it prevents

Summarizing a session to fit a window preserves *what* was done and reliably destroys:

- why an approach failed, and therefore what not to retry
- how a component actually behaves — invariants, edge cases, side effects
- which files were ruled out, and on what grounds
- constraints the user stated once, early, and never repeated

The result is a model that has been compacted but still acts as though it holds the full transcript. It is confidently wrong, and on agentic coding work that means destructive edits made from false certainty.

Notes mode inverts the tradeoff. It does not compress the transcript into one lossy summary; it maintains a small external ledger of durable facts. Context may be dropped, the ledger persists. Rationale cannot be re-derived by reading the code, so the ledger stores rationale and lets the repo supply everything else.

## Principles

- **P1** Externalize before you need it. A note written during a context transition is worth far more than the same note written afterwards, because afterwards the detail is already gone.
- **P2** Never act on implicit memory. If a fact was not cited from the ledger, you do not have it — say so rather than guessing.
- **P3** Retrieval beats recollection. Before any non-trivial action, consult the ledger for the relevant area.
- **P4** A failed attempt is a first-class result. Record it with its reason, so the work is not silently repeated.
- **P5** Append-only in spirit. Correct by superseding, never by silently editing a prior claim out of existence.
- **P6** A ledger is not a transcript. If it does not change a future decision, it does not belong.

## Anti-patterns

| | |
|---|---|
| A1 | Ledger as transcript — will be dropped, defeats the purpose |
| A2 | Late writing — the loss has already happened |
| A3 | Silent correction — loses the reason, invites the retry |
| A4 | Uncited compliance — a note that changed nothing should be deleted |
| A5 | Duplicate ledgers — one per repository; two will disagree |
| A6 | Trusting implicit memory — the precise failure this prevents |
| A7 | Prose handoffs — reintroduces the original lossy-compression problem |

## Why the routing is split the way it is

A context file's instructions get followed, and following them shows up as more exploration, more steps, more cost. Gloaguen, Mündler, Müller, Raychev and Vechev (*Evaluating AGENTS.md*, ETH Zurich / LogicStar, ICLR 2026) measured context files across four agents and four models: no task-success improvement, and inference cost up more than 20%, for both human-written and LLM-written files. The mechanism is behavioral — agents obey the instructions, and obedience broadens exploration.

So this protocol is deliberately layered:

- **Pinned in `SKILL.md`:** the literal retrieval commands and five rules. Behavior that must never be missed.
- **On demand:** schema, write triggers, handoff contract, audit, Codex config. Behavior that is needed only in a specific situation.
- **Never pinned:** the argument for why. A runtime agent that already follows the rules does not need the case for making them, and that argument is the most expensive part of the original document.
