---
name: astra-review
description: Run an independent GPT-6-Astra code review through headless Codex (codex exec) and return it verbatim. Use only when the user explicitly invokes /astra-review.
disable-model-invocation: true
---

# Astra Review

Always use **GPT-6-Astra** through headless Codex (`codex exec`). Default to **medium reasoning on the normal (standard) speed tier**, never Fast. Use another effort only when the user explicitly asks. Never use another model or harness.

## Run

1. Pick the repo root and the scope (uncommitted diff by default, or the base revision / paths the user names). Codex runs in the same checkout, so it sees uncommitted work.
2. Make a run folder outside the repo: `RUN=$(mktemp -d /tmp/astra-review.XXXXXX)`. Write the review brief (below) to `$RUN/brief.md`.
3. Launch in the background (Bash `run_in_background`), stdin from the brief so it never hangs on open stdin:

```bash
codex exec -m gpt-6-astra -c model_reasoning_effort='"medium"' \
  -s read-only --ephemeral -C "$REPO" \
  -o "$RUN/review.md" - < "$RUN/brief.md" > "$RUN/stdout.txt" 2> "$RUN/stderr.txt"
```

- `-s read-only`: the reviewer may read files and run read-only commands but cannot change anything.
- Do not pass any service-tier / fast option.


## Checks

- Before launching: `codex --version` works. If `gpt-6-astra` is missing from `codex debug models`, stop and report it.
- After the run, check the header in `$RUN/stdout.txt`: it must show `model: gpt-6-astra`, `reasoning effort: medium`, `sandbox: read-only`, and no fast/priority service-tier line. If the user config forces a fast tier, stop and report it.
- If any check fails, stop and report the blocker. Never silently fall back to another model, effort, tier or harness.

## Review brief

Include the complete CRITICAL GIT RULES section below in the reviewer brief.

Give neutral context: scope, paths, intended behavior, and diff/base revision (tell the reviewer which `git diff` command shows the change). Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

## Result

Wait for the background job's completion notification; do not poll. The review counts as finished only when the exit code is 0 and `$RUN/review.md` exists and is not empty. A timeout, non-zero exit, or empty file is a blocker: report it with the tail of `$RUN/stderr.txt` and do not present partial output as a finished review.

### Output (owner 2026-11-13)

1. **Detail file for agents.** Copy the full review to `REVIEW-<date>.md` in the reviewed project's documentation folder, or keep it at `$RUN/review.md` when no destination is requested. The copy keeps the reviewer's full text verbatim. Add a short header giving the scope, model, effort, and run folder, and a "Fix list" that repeats each issue with its file:line, exact string, and suggested fix. Agents read this file for context.
2. **Chat reply for the owner.** Show a simple table ranked by priority (highest first):
   - Columns: `#`, an emoji for what the item is (🔒 security, 🕵️ privacy/leak, 🐛 bug, ⚙️ config, 🧪 test, 📄 docs, 🧹 cleanup), Item, Rating (how often/how bad), Fix.
   - Keep each description column narrow, about 40 characters per line. If a description runs longer, break it onto a second line inside the cell with `<br>` instead of letting it stretch the table.
   - Use plain words, with no file paths in the table.
   - After the table, give one line with the verdict, then the path of the detail file.
   - Never present partial output as a finished review.

## CRITICAL GIT RULES

- Never commit, amend, merge, rebase, cherry-pick, or switch branches.
- Never delete, discard, revert, overwrite, clean up, or otherwise remove any existing Git change.
- Never run `git reset`, `git restore`, `git checkout`, `git clean`, `git stash`, or an equivalent destructive/discarding command.
- Never stage new changes or unstage existing changes.
- Preserve all unrelated modified, staged, and untracked files exactly as found; do not alter another person's changes.
- Leave completed changes only in the working tree.
- If files or changes unexpectedly appear, disappear, or change during work, stop and report the concurrent-worktree conflict; do not reconstruct, revert, or clean anything.
