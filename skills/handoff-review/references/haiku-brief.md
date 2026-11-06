# Round handoff reviewer brief (/handoff-review)

You review build rounds run by the plans driver (~/projects/plans, same as ~/projects/plans). The question each week: when a round stops abnormally, does it leave a usable note (PAUSE.md from bin/checkpoint.sh, HANDOFF.md from driver.mjs handoff() or reap() late-stop notes), does the retry use it, and what is still wasteful.

READ-ONLY. The only files you may write are your outputs under <OUT>. Do not edit, run tests, kill or start anything, no state-changing git.

Your batch file (JSON list of rounds) is in your task. Each row has plan, step, launches, round_dir, notes present, advanced, and its driver.log events (launch, done rc= missing= minutes, advance, paused, checkpoint, takeover, late, waiting, lost).

Per round (cheap: heads, tails, grep; never cat a big file):
1. How each attempt ended (rc, minutes, missing outputs); did it advance.
2. Every abnormal stop (rc != 0, pause, checkpoint, takeover, lost, timeout, rc 0 with missing output): was PAUSE.md/HANDOFF.md written within ~20 min before to 3 h after? Quality: good (done list, in progress, next steps), thin, wrong (contradicts files on disk; checkpoint.sh appends a "facts" block you can compare), none.
3. Did the retry read the note? Check the retry's transcript: Claude jsonl under ~/projects/plans/_run/claude-home/projects/<encoded-project-root>-<plan>/ (match by time), Pi `<round>/orch/session/*.jsonl`, Codex `<round>/orch/events.jsonl`. Named in prompt (orch/prompt.md mentions it) / found by chance / never.
4. Waste: repeated limits or timeouts, wrong usage-limit flags, refilled checkpoint slots, long silent waits (driver.log gaps or "waiting" lines), work redone after a retry, driver restarts.

Write `<OUT>/batch-<NN>.md`, max ~150 lines:
```
# Batch NN: <plans>
## Rounds
plan | step | launches | attempt endings ("75 24m; 0 40m") | abnormal stops | note (PAUSE/HANDOFF/none) | quality | retry used note (prompt/chance/never/n.a.) | advanced
## Findings
numbered; each = one-sentence claim + evidence (path + exact log line or quote). Only what you checked.
## Suggested fixes
numbered, concrete (file/function, change), tied to findings.
## Counts
abnormal stops, with note, without note, detector-invisible.
```
Facts only; say "unknown" rather than guess. Reply only "done NN: <rounds covered>".
