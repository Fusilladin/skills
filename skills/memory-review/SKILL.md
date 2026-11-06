---
name: memory-review
description: Weekly RAM and /tmp check of this Linux box and the plans harness. Snapshot the biggest processes, sort them into leak / held-not-freed / piling-up / normal with real evidence (heap snapshots of Node servers, X shared memory, /tmp files), then write a frame-budget HTML page with charts and decision cards, apply the owner's decisions and run /page-update. Run once a week, next to /verify-review and /handoff-review. Invoked as /memory-review.
---

# /memory-review

Weekly check of where RAM and RAM-backed /tmp go, and whether anything grows.
First run: 2026-11-02/03. It found the Observatory Codex-string leak, the opencode `.so` pile-up in /tmp, and the screenshot hotkey's leftover X shared memory. All were fixed. Page: `_reports/memory-review-2026-11-03.html` (detail page `_run/memory-fixes/index.html`).

Work folder: `~/projects/plans/_reports/memory-review/<YYYY-MM-DD>/`. Keep it out of /tmp, which is RAM.
Page: `~/projects/plans/_reports/memory-review-<YYYY-MM-DD>.html`, linked from `~/projects/plans/index.html` under "How it works".
No subagents: the whole review is a few dozen read-only commands. Do it in this session.

## 0. Intake

Unless the owner already said "just run it", ask once: apply recommended fixes without asking, or decide on the page? Then say "No more questions; working now."

## 1. Snapshot (read-only)

```bash
W=~/projects/plans/_reports/memory-review/$(date +%F)
PREV=$(ls -d ~/projects/plans/_reports/memory-review/*/snapshot.json 2>/dev/null | grep -v "$(date +%F)" | tail -1)
python3 -I ~/.agents/skills/memory-review/scripts/collect.py --out $W ${PREV:+--prev $PREV}
```
`snapshot.json` holds:
- meminfo, plus the top 25 processes with RSS, anon, shm and age;
- System V shared memory segments of 16 MB and up, with their creator;
- /tmp usage, its biggest entries, and opencode `.so` files counted per hour;
- the Observatory service, Zen probe ok/down per day, and any `~/tmp-archive*`.

`prev_rss` shows growth since last week.

## 2. Sort each big or growing process into one of four bins, with evidence

Check `prev_rss` and age first. A big process that is young and was big last week is usually normal. Then work through these by type:

- **Node server** (Observatory or any long-running node):
  1. Open the inspector with `kill -USR1 <pid>`.
  2. Run `node scripts/node-eval.mjs '<expr>'` with `process.memoryUsage()` and `v8.getHeapSpaceStatistics()`. Prefix it with `GC=1` to force a garbage collection first.
  3. If the heap stays big after GC, run `node scripts/heap-snapshot.mjs $W/x.heapsnapshot`, then `node --max-old-space-size=8000 scripts/heap-top.mjs $W/x.heapsnapshot 400`. It prints the largest objects and their retainer paths.
  4. Close the inspector with `node scripts/node-eval.mjs 'require("inspector").close()'` and delete the snapshot.
  - Known pattern: a regex match or `split` piece kept in a long-lived Map pins the whole file chunk it came from ("sliced string"). The fix is `flat()` (`Buffer.from(x).toString()`).
- **GTK/X app with big RssShmem**: look at `/proc/<pid>/smaps` for `SYSV` segments and match them in `ipcs -mp`. Xorg counts the same pages, so don't add the two together. That memory is held, not leaked, unless it keeps growing with each use.
- **/tmp**:
  - Look at the biggest entries and their age.
  - `.XXXXXXXXXXXXXXXX-00000000.so` files come from `opencode run`. The heartbeat cleanup (`clean_opencode_so` in `_run/bin/free_heartbeat.sh`) should keep them in single digits. If there are many, check that the cleanup still runs and whether some other opencode caller (worker, orchestrator) needs it too.
- **Expected big users**: Strata (`strata-host`, about 35 GB, with a RAM guard at 90%), rustc and cargo builds, browsers, claude, codex and opencode runs. Mention them in the `context` line; they aren't findings.

Check each claim against a second source before you write it down. The first run had to correct a guess that the hotkey kept screenshots: its own heap was only 20 MB.

## 3. Page

Write `$W/findings.json`; the schema is at the top of `scripts/build_page.py`.
- `verdict` is one of leak / held / pileup / normal. `worst_mb` is the largest amount measured; `after_mb` is set only when a fix is live.
- Each decision has a plain, non-technical `why` and a recommended option first.
- Copy last week's decisions and fixes over, with their answers, so they fold into Done.
- Add `trend` points from every earlier `snapshot.json` (`meminfo.MemAvailable`).
- Follow humanizer rules: plain words, no em dashes, outcome first.

```bash
python3 -I ~/.agents/skills/memory-review/scripts/build_page.py --work $W --out ~/projects/plans/_reports/memory-review-$(date +%F).html
~/.local/bin/node ~/.agents/skills/memory-review/scripts/shot.cjs <page.html> $W/shot
```
The builder runs collapsible, scroll-perf and fix-chars itself. `shot.cjs` checks 1440 and 390 px and prints console errors, external requests and overflow; look at the screenshots yourself. Add the page link in `plans/index.html` under "How it works".

## 4. Apply decisions (when the owner pastes Copy choices)

- Back up every changed file as `*.bak-<date>-memreview`. Check it with `node --check`, `bash -n` or `python3 -m py_compile`, and remove any `__pycache__` that creates.
- Edit by matching text, not line numbers, because files shift between weeks.
- Replace a bash script that may be running with a temp file and `mv`; never edit it in place.
- Observatory: run `systemctl --user restart observatory` (never start it by hand), then check RSS after about 2 minutes.
- Desktop apps (for example `~/.local/bin/screenshot-hotkey`): restart them with xfce4-panel's `/proc/<pid>/environ` under `setsid`, and ask the owner to try them once.
- Deleting archives: ask the watcher first if the owner says so. To find it, follow auditq-wait.sh's parent `claude --resume` to `~/.claude/sessions/*.json` and its name, then use SendMessage.
- Log harness changes as a HARNESS.md section 13 entry. Then record the answers in `findings.json`, mark the fixes done, rebuild, and run `/page-update` on the page.

## Rules learned

- Measure before you name a cause: forced GC plus a heap snapshot for Node, and smaps plus ipcs for shared memory.
- A fresh restart that looks small proves nothing. Compare against the same age, or the state after first use.
- When Xorg and a client share SYSV pages, the process list counts them twice.
- End the reply with the page path on two lines: `~/projects/plans/_reports/...` and `http://localhost:8000/projects/plans/_reports/...`.
