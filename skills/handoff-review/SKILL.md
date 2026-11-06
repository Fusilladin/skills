---
name: handoff-review
description: Weekly review of round stops and handoff notes in the plans harness (PAUSE.md, HANDOFF.md, checkpoints, limit pauses, late stops, driver restarts). Haiku agents review every round launched in the window, one Opus agent verifies and ranks fixes, then an orbit-ledger HTML page with charts, a fix board and decision cards; then apply the owner's decisions. Run once a week, next to /verify-review. Invoked as /handoff-review [from YYYY-MM-DD] [to YYYY-MM-DD].
---

# /handoff-review

Weekly check that rounds which stop abnormally leave a usable note, that retries read it, and what is still wasteful around stops.
First run: 2026-11-02/03 (126 rounds since the 10-29 fix; page `_observatory/handoff-fix-review.html`). It led to the 11-03 harness fixes: late-stop notes, checkpoint STOP + facts block + luna/pi coverage, hex-safe 429, retry prompt names HANDOFF.md, audit-only resumes, driver watchdog, honest blockers.mjs detector.

Defaults: window = the 7 days before today, or from the last report's end date so weeks never overlap.
Work folder: `~/projects/plans/_reports/handoff-review/<YYYY-MM-DD>/` (not /tmp).

## 0. Gate

- Usage room: `~/.claude/scripts/usage_gate.sh check`. PAUSE means stop and tell the owner when it will be OK. The job uses up to 8 Haiku agents and one Opus agent.
- Intake in one batch unless the owner said "just run it": window, and whether to apply recommended decisions without asking. Then say "No more questions; working now."
- Never EnterPlanMode while Haiku agents are writing; it blocks their writes.

## 1. Collect

```bash
W=~/projects/plans/_reports/handoff-review/$(date +%F)
python3 ~/.agents/skills/handoff-review/scripts/collect.py --from <from> --to <to> --out $W
```
Writes `rounds.json` (one row per plan+step launched in the window, with its driver.log events), `stops.json` (the Observatory's own detector, `blockers.mjs` optimizeTips: stopStats pre/post/late/byCause/daily, stops, the handoff tip) and `batches/batchNN.json` (whole plans, at most 8 batches).

## 2. Per-batch notes: Haiku, in parallel

Touch a marker first (`touch $W/.marker`). One Agent per batch, all in a single message, `model: haiku`, `run_in_background: true`:
"Read ~/.agents/skills/handoff-review/references/haiku-brief.md and follow it. Batch: $W/batches/batchNN.json. OUT=$W. NN=<nn>."
Wait for the notifications; don't poll. Then check ownership: `find ~/projects/plans -newer $W/.marker -name 'PAUSE.md' -o -newer $W/.marker -name 'HANDOFF.md'` and any other file they could have touched; other sessions edit the harness too, so look at what changed before blaming an agent.

## 3. Final review: one Opus agent

"Read ~/.agents/skills/handoff-review/references/opus-brief.md and follow it. WORK=$W. PREV=<last week's final-review.json or none>."
It writes `final-review.md` and `final-review.json`. Spot-check its two or three biggest claims yourself (driver.log lines, the file:line it cites) before the page.

## 4. Page

```bash
python3 ~/.agents/skills/handoff-review/scripts/build_page.py --work $W --out ~/projects/plans/_reports/handoff-review-$(date +%F).html
```
Orbit-ledger (the Observatory look): verdict + fix donut, fix board (open first, impact bar, effort), open decision cards with Copy choices, stops-per-day chart, rounds waffle, closed panels for answered decisions and rejected Haiku claims. It also writes `_reports/handoff-review-latest.html`, which the Observatory header "Handoff review" button should open.
Run the summary and verdict text through the humanizer rules first (plain words, no em dashes). Playwright at 1440 and 390 px: no console errors, no horizontal scroll; look at the screenshot yourself (Playwright from gridwright/node_modules, executablePath to ~/.cache/ms-playwright/chromium-*).

## 5. Owner decisions and fixes

- When the owner pastes Copy choices: set `decisions[].answer` in final-review.json and rebuild (answered cards fold away).
- When the owner says "update all" / "implement": apply open fixes. Back up each file as `*.bak-<date>-handoff`, `node --check` / `bash -n`, test the detector by running optimizeTips on driver.log, restart the driver (`kill $(cat _run/driver.pid); DRIVER_START_REASON=handoff-review bash _run/start-driver.sh`; jobs are detached and adopted). Leave the Observatory server to the owner or the session that owns it. Mark fixes `done` with one plain sentence, rebuild, and for a page the owner already read use /page-update.
- Log the change as a HARNESS.md §13 entry; brief the watcher like /verify-review step 6.

## Rules learned in the first run (keep)

- Count each round once, by its worst stop. "Late" stops (rc != 0 after AUDIT.md existed) are a separate bucket: nothing lost.
- Sub-step events (audit gate rc 75 that fell back to headless Sonnet, worker rc 124, launch waits) cost time, not state: not handoff gaps. p1 steps and sub-5-minute no-output exits are not gaps either.
- Haiku claims seen wrong before: "retry never read HANDOFF.md" (check the transcript's first tool calls), "serial workers" (tasks declare their order), long gaps that were HOLDs. Always check.
- Concurrent sessions edit driver.mjs, server.mjs, audit.sh and AUDIT.md (audit-bump writes `.pre-override` backups). Use Edit (stale-read safe), never overwrite whole harness files.
- Auto mode blocks crontab edits unless the owner explicitly asks; then it is allowed.
- End the reply with the .html path in two lines: `~/projects/plans/_reports/...` and `http://localhost:8000/projects/plans/_reports/...`.
