# Codex Notes

Optional. The protocol works with nothing but a text file and a grep.

## Enabling

In `~/.codex/config.toml`, either as a dotted key placed above every `[section]` header:

```toml
features.context_management.experimental_mode = true
```

or as its own section:

```toml
[features.context_management]
experimental_mode = true
```

Use one form, not both. Restart Codex and start a new task.

## What it enables (Codex CLI ~0.153)

- **Token-budget context** — a machine-readable remaining-capacity figure is passed alongside each model call, so the model can pace its output and compact early instead of guessing.
- **History notes** — structured continuity annotations injected into context. The schema is internal and undocumented. Do not build tooling that parses or edits them.
- **`new_context` tool** — a no-summary checkpoint. It discards history rather than compressing it, and the session continues from the initial context only: system prompt, AGENTS.md, active files. Aggressive and intentional.

## Eligibility — the flag is silently ignored when any of these fail

- ChatGPT Plus, Pro, or Pro Lite account
- Codex backend, not a custom provider
- Standard session, not a temporary structured thread
- Not an API-key session

There is no warning when eligibility is unmet. Verify with a short test session before documenting the feature as active.

## Interaction with this protocol

Codex auto-compacts at roughly 95% of the window; `experimental_mode` replaces that with budget-aware pacing plus an explicit wipe. Prefer it to a manual percentage trigger, and prefer `new_context` to step 3 of `reset.md` — the `new_context` discard is strictly more aggressive, so run the checkpoint and cold-verify in steps 1 and 2 first.

Keep `ledger/` as the contract either way. The flag only helps sessions running on the Codex backend, and it changes nothing about what survives a reset.

## Related Codex knobs

`project_doc_max_bytes` caps combined project documentation at 32 KiB by default, dropping the overflow without warning. If the repo's instruction files exceed that, the tail never reaches the model. `project_doc_fallback_filenames` names additional files treated as project docs.
