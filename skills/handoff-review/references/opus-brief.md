# Opus final reviewer brief (/handoff-review)

You write the weekly review of round stops and handoff notes in the plans harness, from the Haiku batch notes. READ-ONLY outside <WORK>; another session may be editing harness files, never touch them.

Inputs in <WORK>: rounds.json (every round launched in the window), stops.json (the Observatory detector: stopStats {pre, post, late, byCause, daily}, stops, tip), batch-NN.md (Haiku; it miscounts and can be wrong: verify every claim you keep), and <PREV> (last week's final-review.json or "none"). Also read: ~/projects/plans/_run/driver.mjs (handoff, reap, startStep, schedule), _run/bin/checkpoint.sh, _run/bin/agent.sh (hit_limit, LIMIT_RE), _run/start-driver.sh, _run/bin/driver-watchdog.sh, _run/prompts/orchestrator.md, _observatory/blockers.mjs optimizeTips, and HARNESS.md section 13 entries since the window start (fixes already made: do not recommend them again; list them as done).

Spot-check with driver.log and round folders. Count each round once (its worst stop). A "late" stop (rc != 0 after outputs were complete) is its own bucket, not lost work.

Write <WORK>/final-review.md (Verdict; Numbers; Confirmed optimizations ranked; Detector fixes; Rejected Haiku claims; Owner questions) and <WORK>/final-review.json with exactly these keys:
```json
{
 "window": "2026-10-27..2026-11-03",
 "verdict": "one plain sentence, the outcome first",
 "summary": ["2-3 short plain paragraphs"],
 "numbers": {"rounds": 0, "launches": 0, "stops": 0, "noted": 0, "unnoted": 0, "late": 0, "lost_work": 0},
 "outcomes": [{"label": "Clean on the first try", "n": 0, "kind": "ok"}, {"label": "Stopped, resumed from a note", "n": 0, "kind": "note"}, {"label": "Stopped with no note", "n": 0, "kind": "warn"}],
 "note_quality": {"good": 0, "thin": 0, "wrong": 0},
 "retry_found": {"prompt": 0, "chance": 0, "never": 0},
 "fixes": [{"status": "done|open|none", "name": "short", "text": "what it means for the owner; for open ones what it would take", "impact": 1, "effort": "S|M|L"}],
 "rejected": [{"claim": "...", "result": "Rejected|Downgraded|Corrected", "why": "..."}],
 "decisions": [{"id": "snake_case", "title": "question", "why": "one line", "options": ["A", "B"], "recommended": "A"}]
}
```
impact is 1-10 (rounds, minutes or tokens affected). Only genuine owner calls go in decisions; anything an agent can just do is an open fix. Plain words, no em dashes, numbers over adjectives. Reply "done" plus a 3-line verdict.
