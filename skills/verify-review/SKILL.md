---
name: verify-review
description: Weekly review of every plans-harness verify job (Haiku per-run notes, one Opus overall review, neon-ops HTML page with charts and decision cards), then apply the owner's decisions and brief the watcher. Run once a week near the Claude weekly usage reset. Invoked as /verify-review [from YYYY-MM-DD] [to YYYY-MM-DD].
---

# /verify-review

Weekly audit of the verify step in `~/projects/plans` (the final check of each plan build).
First run: 2026-11-02/03 (126 runs, Oct 20 to Nov 1; page `_reports/verify-review-2026-11-02.html`).

Defaults: window = the 7 days before today (or from the last report's end date, so weeks never overlap).
Work folder: `~/projects/plans/_reports/verify-review/<YYYY-MM-DD>/` (not /tmp: the run spans hours and /tmp is RAM).

## 0. Gate (when to run)

- Run it when the Claude weekly window resets within about a day and usage has room: `~/.claude/scripts/usage_gate.sh check`.
  PAUSE means stop and tell the owner when it will be OK. The job uses about 11 Haiku agents and one Opus agent.
- Observatory must be up: `curl -s localhost:18990/ -o /dev/null -w %{http_code}` returns 200. If not, run `systemctl --user start observatory` and wait for the scan to finish.
- Intake in one batch, unless the owner already said "just run it". Ask about the window, and whether to apply the recommended decisions without asking. Then say "No more questions; working now."
- Never EnterPlanMode while the Haiku agents are writing; it blocks their writes.

## 1. Collect

```bash
W=~/projects/plans/_reports/verify-review/$(date +%F)
python3 ~/.agents/skills/verify-review/scripts/collect.py --from <from> --to <to> --out $W
```
This writes `verify-data.json`, with one row per run: wall time, attempts, model, cost, `cost_state`, provider waits, queue waits, lost runs and rc 124. It also writes `batches/batchNN.json` with 12 runs each. The Observatory is read in 3 h windows because its API caps agents at 300 rows.

## 2. Per-run notes: Haiku, in parallel

Run one Agent per batch, all in a single message, with `model: haiku` and `run_in_background: true`. The prompt is:
"Read ~/.agents/skills/verify-review/references/haiku-brief.md and follow it. Batch: $W/batches/batchNN.json. OUT=$W. NN=<nn>."
The agents write `$W/runs/<project>__<step>.md` and `$W/batch-NN-summary.md`. Wait for the completion notifications; don't poll.
Haiku miscounts, so Opus checks its numbers in the next step.

## 3. Overall review: one Opus agent

Run one Agent with `model: opus`. The prompt is:
"Read ~/.agents/skills/verify-review/references/opus-brief.md and follow it. WORK=$W. PREV=<last week's final-review.json or none>."
It writes `final-review.md` and `final-review.json` (summary, outcomes, per_run, plans_trend, down_why, time_lost, issues, fixes, decisions).
Before using its two or three biggest claims, check them against the files yourself, for example the VERIFY.md verdicts and the driver.log lines.

## 4. Page

```bash
python3 ~/.agents/skills/verify-review/scripts/build_page.py --work $W --out ~/projects/plans/_reports/verify-review-$(date +%F).html
```
This produces a neon-ops page:
- inline SVG charts (outcome donut, run length, hours lost, issues, cost, a pass-rate sparkline for each plan that dropped, fix-status donut);
- decision cards for open owner calls, with Copy choices;
- answered decisions folded away under "Decisions already made".

It also runs collapsible.html, scroll-perf (home link `../index.html`) and theme fix-chars.
Before building, run the summary text in `final-review.json` through the humanizer rules: plain words, no em dashes.
Check the page with Playwright at 1440 and 390 px. There should be no console errors and no horizontal scroll. Playwright is in gridwright's node_modules. Look at the screenshots yourself.
Add a link in `~/projects/plans/index.html` under "How it works", next to the earlier verify-review links.

## 5. Decisions: when the owner pastes Copy choices back

- Record each answer in `final-review.json` as `decisions[].answer`, then rebuild. Answered cards fold away, so "hide if done" is automatic.
- Apply each decision in the harness:
  - Back up every changed file as `*.bak-<date>-verifyreview`.
  - Use `node --check` / `bash -n`, and `node _run/bin/budget.mjs test` when the router changes.
  - Restart the driver: `kill $(cat _run/driver.pid); bash _run/start-driver.sh`. Jobs are detached and get adopted.
  - Restart the Observatory with `systemctl --user restart observatory` when server.mjs changes.
  - Log the change as a HARNESS.md §13 entry.
- Mark each fix in `fixes[]` as `done` with one plain sentence on what changed, then rebuild.

## 6. Brief the watcher

The watcher is the session that runs `_run/bin/auditq-wait.sh`. To find it: get `ps` of auditq-wait, then its parent `claude --resume`, then the tty, then `tmux list-panes -a`, then match the pane against ListAgents. Send it, with SendMessage:
- the HARNESS §13 entries to read;
- anything it must do differently: queue order, re-arming auditq-wait, reopen rules, status fields;
- a long spec saved as `_run/handoff/<topic>-<date>.md`, with the path in the message.

Don't send it work its permissions would block.

## Rules learned in the first run (keep)

- A paid job with no usage record shows "not captured", never $0 (Observatory `costState`). Runs before 2026-10-22 06:38 are ignored.
- The Observatory dollar figure is the API-list-price equivalent of subscription usage, not a bill.
- `VERIFY.md` counts only if it is newer than the job start, has no placeholders, and the run exited 0 (driver.mjs stepOk/reap).
- Autonomous reopens use `--auto`, write BASELINE-V{n}.md "must still pass", and need READ.md (reopen guards, 2026-11-03). When a plan drops, check whether the reopen was autonomous first.
- Drops caused by owner-requested new scope are fine; say so rather than flagging them.
- End the reply with the .html path in two lines: `~/projects/plans/_reports/...` and `http://localhost:8000/projects/plans/_reports/...`.
