---
name: claude-review
description: Run an independent Claude Fable 5.1 code review through headless Claude Code (claude -p) and return it verbatim. Use only when the user explicitly invokes /claude-review.
disable-model-invocation: true
---

# Claude Review

Always use **Claude Fable 5.1** (`claude-fable-5-1`) through headless Claude Code (`claude -p`). Default to **medium effort on normal speed**, never fast mode. Use another effort only when the user explicitly asks. Never use another model or harness.

## Run

1. Pick the repo root and the scope (uncommitted diff by default, or the base revision / paths the user names). The reviewer runs in the same checkout, so it sees uncommitted work.
2. Make a run folder outside the repo: `RUN=$(mktemp -d /tmp/claude-review.XXXXXX)`. Write the review brief (below) to `$RUN/brief.md`.
3. Launch in the background (Bash `run_in_background`), prompt piped via stdin (a positional prompt gets swallowed with `--allowedTools`):

```bash
cd "$REPO" && claude -p --model claude-fable-5-1 --effort medium \
  --permission-mode default \
  --allowedTools "Read" "Grep" "Glob" "Bash(git diff:*)" "Bash(git log:*)" "Bash(git show:*)" "Bash(git status:*)" \
  --disallowedTools "Edit" "Write" "NotebookEdit" \
  --output-format json < "$RUN/brief.md" > "$RUN/out.json" 2> "$RUN/stderr.txt"
jq -r '.result // empty' "$RUN/out.json" > "$RUN/review.md"
```

- The allow/deny lists make the reviewer read-only: it may read files and run read-only git commands but cannot change anything.
- Do not pass any fast-mode option.

## Checks

- Before launching: `claude --version` works.
- After the run, check `$RUN/out.json`: `is_error` is false and `modelUsage` lists `claude-fable-5-1` (other small helper models may appear too). If Fable is missing or another main model ran, stop and report it.
- If any check fails, stop and report the blocker. Never silently fall back to another model, effort, speed or harness.

## Review brief

Give neutral context: scope, paths, intended behavior, and diff/base revision (tell the reviewer which `git diff` command shows the change). Ask for a thorough senior-developer review, including related code and tests, without steering toward suspected bugs, solutions, or verdicts. Review only; do not change files. Request a concise plain-English report of serious or critical issues, fixes, and production merge readiness. Distinguish verified findings from uncertainty and identify validation gaps.

Include this sentence in the brief, word for word: "During your final answer, Rate each issue you find from 1 to 10 on how often it would happen, and 1-10 on how bad it would be"

## Result

Wait for the background job's completion notification; do not poll. The review counts as finished only when the exit code is 0 and `$RUN/review.md` exists and is not empty. A timeout, non-zero exit, or empty file is a blocker: report it with the tail of `$RUN/stderr.txt` and do not present partial output as a finished review.

Return the reviewer's full final response (`$RUN/review.md`) verbatim, followed by one line giving the run folder path.
