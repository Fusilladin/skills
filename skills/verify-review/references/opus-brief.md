# Opus final reviewer brief (/verify-review)

You write the overall review of every verify job in one window, from the Haiku per-run notes. READ-ONLY outside `<WORK>`.

Inputs in `<WORK>`:
- `verify-data.json`: one row per run (wall minutes, attempts, model, cost, cost_state, waits, queue waits, lost, rc 124 count, driver_log).
- `runs/*.md`: one note per run (Haiku). `batch-NN-summary.md`: per-batch patterns.
- `<PREV>` (may be "none"): last week's `final-review.json`, so you can say what changed.
- `_run/HARNESS.md` §13 entries since the window start: fixes already made, so do not recommend them again.

Check the Haiku notes against the files for anything surprising (verdict counts, regressions, lost runs). Haiku miscounts; the VERIFY.md is the truth. Say "unknown" instead of guessing.

Write `<WORK>/final-review.md` (sections: Bottom line; Volume and cost; Outcomes; Harness issues ranked by impact; What verify catches and misses; Recommendations; Changes since last week) and `<WORK>/final-review.json` with exactly these keys:

```json
{
 "window": "2026-10-27..2026-11-03",
 "summary": ["3 short plain paragraphs: what verify found; what went wrong around it; what changed / what to decide"],
 "outcomes": {"built": 0, "partial": 0, "failed": 0},
 "per_run": [{"project": "10-agent-sandbox", "step": "v8-verify", "outcome": "built|partial|failed", "pass": 2, "total": 6, "regression": true, "note": "<= 12 words"}],
 "plans_trend": [{"project": "...", "trend": "up|flat|down", "versions": "v3..v8"}],
 "down_why": {"<project>": ["short tag: New scope | Autonomous loop | Too many reopens | Cross-plan break | Harness | other", "2-3 plain sentences: what you think happened, with evidence"]},
 "time_lost": [{"label": "Waiting for Opus or Codex", "minutes": 0}, {"label": "Watcher queue", "minutes": 0}, {"label": "Lost at reboots/restarts", "minutes": 0}, {"label": "Killed at the time cap", "minutes": 0}],
 "issues": [{"name": "plain label", "count": 0, "fixed": false}],
 "fixes": [{"group": "Driver and queue | Prompts | Observatory | ...", "items": [{"status": "done|open|none", "name": "short", "text": "what it means for the owner, 1-2 plain sentences; for open ones what it would take"}]}],
 "decisions": [{"id": "snake_case", "title": "question", "why": "one line", "options": ["A", "B"], "recommended": "A"}]
}
```

Rules: plain words, no em dashes, numbers over adjectives. Things the harness already fixed go in `fixes` as done (cite the HARNESS entry). Only owner calls go in `decisions`; everything an agent can just do is an open fix. Reopens by the watcher are marked `(autonomous: ...)` in REOPEN-VN.md; owner ones are not; use that when explaining drops. Reply "done" when both files are written.
