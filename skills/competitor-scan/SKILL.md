---
name: competitor-scan
description: Weekly competitor scan for a plan (default plan 68, the open-source Observatory app). Re-checks every known rival (agent monitors/controllers, sandbox and cloud-session tools, parallel-agent orchestrators, coding CLIs/IDEs and their free tiers), finds new ones, diffs against last week, updates the feature matrix and moat, then refreshes competitors.html with /page-update. Invoked as /competitor-scan [plan-folder].
---

# /competitor-scan

Weekly. First run 2026-11-04 (plan 68: 22 monitors, 35 sandbox/cloud tools, 30 coding tools' free tiers).

Plan folder: arg or `~/projects/plans/68-observatory-app`. Data files there (the source of truth; the page is built from them):
- `matrix.json`: features x tools ({features, tools, cells{tool:{feature:{v:y|p|n|?, note}}}}), plan itself as a tool.
- `sandboxes.json`: sandbox / cloud-session / orchestrator / hosted-agent tools.
- `free-tiers.html` data: coding tools, free model usage, ToS verdict ADD/MAYBE/NO.
- `scans/<YYYY-MM-DD>/`: this run's raw notes, `diff.md`, and copies of the json files before the run.

## Steps

1. **Snapshot**: copy matrix.json, sandboxes.json, competitors.html, free-tiers.html into `scans/<today>/before/`. Read INTAKE.md for what the plan now promises (plan's own matrix column must match it).
2. **Re-check known tools** (Sonnet subagents, ~8 tools each, parallel, max 4): for each URL, `gh api repos/O/N` (stars, pushed_at, archived, license) and the README; for closed tools, their site/pricing page via WebFetch. Update cells only with evidence; keep `?` when silent; never guess `y`. Note archived/renamed/dead tools.
3. **Discover new tools** (one subagent): GitHub search (stars>50, pushed in last 30 days) and web search for: claude code monitor/dashboard/remote/mobile, codex remote, agent session manager, coding agent sandbox, cloud agent sandbox, parallel coding agents, agent tmux, agent menu bar. Also check Hacker News / Product Hunt for the week. Add finds that fit; list rejects with one reason.
4. **Free tiers** (one subagent): re-verify ADD and MAYBE rows by opening the actual ToS/pricing pages and quoting the clause; flag changes. Never sign up or install.
5. **Diff** (`scans/<today>/diff.md`): new tools, dead/archived tools, star jumps >20%, matrix cells that changed, free-tier verdict changes, new features nobody had last week. Recompute: coverage scores, moat list (only we plan it), must-haves (most rivals y, we n), gap ideas (nobody has).
6. **Plan feedback**: if a must-have or threat is new, append a dated line to INTAKE.md "Owner additions" only as a *suggestion* and send one watcher chat message (`_run/chat_inbox/<ms>.json`, {at, from:"control", text}) listing them. Never change sub-item priorities without the owner.
7. **Page**: update `_page/new.json` (done/open items) and the json data, then `python3 build-competitors.py`, scroll-perf.mjs --home ../index.html and theme.py fix-chars; follow /page-update rules for competitors.html (read `~/.agents/skills/page-update/SKILL.md`): "New since you read it" = the diff; matrix, sandbox section and moat panel rebuilt from the json. Keep relay-tower theme, radar tab icon, collapsibles, scroll-perf, fix-chars. Update free-tiers.html the same way if step 4 changed anything.
8. **Verify**: Playwright 1440 + 390 (gridwright's playwright, executablePath newest ms-playwright chrome), no errors, no horizontal scroll, look at the screenshot.
9. **Reply**: 3-5 lines (new threats, new must-haves, free-tier changes), then the html paths as `~/projects/plans/...` and `http://localhost:8000/projects/plans/...`.

## Rules
- Evidence over memory: every changed cell gets a note with source; mark memory-based facts "unverified".
- GitHub search rate limit ~30/min: pace calls, prefer `gh api repos/...` (higher limit).
- Subagents: Sonnet, read-only except their own notes file in `scans/<today>/`; only the main session edits json and html.
- No Haiku. Respect the usage gate (`~/.claude/scripts/usage_gate.sh`) before launching subagents.

## Make it more robust later (backlog)
- Script the GitHub refresh (`scan.mjs`: stars/pushed/archived for all urls in the json) so step 2 only reads READMEs that changed (compare README sha).
- Store weekly star history and chart growth on the page.
- Add a watchlist of ToS URLs with content hashes to detect ToS changes cheaply.
