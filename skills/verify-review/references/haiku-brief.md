# Verify-run summarizer brief

You summarize "verify" jobs from the plans build harness (~/projects/plans). A verify job is the final check of a plan's build: an Opus 5.5 (Claude, run headless) or Codex gpt-6.1-sol agent reads the plan's spec, runs its tests, and writes `_build/VERIFY.md` (pass/partial/fail per requirement) and `_build/DEFERRED.md`. The driver launches it (driver.mjs), agent.sh runs it with a timeout (was 3600 s = 1 h), and the Observatory records each attempt's model, tokens, cost and duration.

READ-ONLY. Do not edit, run tests, kill or start anything. Only write your output files.

Your batch file (a JSON list of runs) is given in your task. Each run has: project, step, job_dir, verify_md_candidates, deferred_md_candidates, observatory_attempts (provider, model, rc, cost USD, minutes), driver_log (launch/done lines: rc, missing outputs, minutes; several "done" lines = retries).

For each run, look at (keep it cheap; read heads/tails, use grep):
1. `driver_log` and `job_dir/meta` (attempt timeline: which provider, rc, timeouts rc=124, usage limits, retries).
2. `job_dir/headless.txt` (Opus final message) and/or the last agent_message in `job_dir/events.jsonl` (Codex; `grep '"agent_message"' events.jsonl | tail -2`).
3. The VERIFY.md that belongs to this run: for `vN-verify` it is usually `_build/v(N+1)-final/VERIFY.md` if that exists, else `_build/VERIFY.md`; for plain `verify` try `_build/v2-final/VERIFY.md` then `_build/VERIFY.md`. The candidates list shows what exists; confirm by the version/date inside the file. Read the top ~60 lines for the verdict and counts.
4. Only if something looks wrong (timeouts, rc!=0, missing outputs, very long runtime >60 min, $0 cost with Opus), skim more (stderr.log, headless.err, tail of the Claude transcript under `~/projects/plans/_run/claude-home/projects/<encoded-project-root>-<project>/` by matching time).

Write one file per run: `<OUT>/runs/<project>__<step>.md` with this shape (short, plain English, under 25 lines):

```
# <project> <step>
- When: <start> -> <end>, <total minutes> min, <N> attempt(s)
- Who: <model(s) per attempt, rc each>; cost $<sum>
- Outcome: <verdict line, e.g. "7/12 pass, 4 partial, 1 fail" or "all pass">
- Key findings: <1-3 bullets: what failed/partial, regressions>
- Harness issues: <timeouts, retries, limit hits, missing outputs, stuck tests; or "none">
- Evidence: <file paths you read>
```

Then write `<OUT>/batch-<NN>-summary.md`: a table (project, step, minutes, attempts, model, outcome, harness issue) plus 3-6 bullets of patterns you saw across the batch. Facts only; say "unknown" rather than guess. Reply with just "done <NN>: <runs written>" when finished.
