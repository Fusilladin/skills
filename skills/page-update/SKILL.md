---
name: page-update
description: Update an HTML report the owner has already read. Puts "New since you read it" first, then new "Waiting on you" decisions, compacts the old content into a short recap with one chart, folds the full detail and answered decisions into closed panels, and drops what no longer matters. Keeps the page's theme and URL. Use when the owner says "update the html, I already read it", "simplify it", "add the new stuff", or "compact the old info". Invoked as /page-update <page.html>.
---

# /page-update

For a page the owner has **already read**. They want only the delta, plus a short memory of the rest.
Example: `~/projects/plans/_reports/verify-review-2026-11-02.html`, updated on 2026-11-03. Its builder was the session's `page/build.py`, and `/verify-review` now carries the same pattern.

## Steps

1. **Back up first**: copy the page to `<page>.bak-<YYYYMMDD-HHMM>` beside it. If the page has a builder script or content.json, edit those instead of the HTML and rebuild. Hand-edit only when there is no builder.
2. **Read marks, always (owner 2026-11-04).** Every New item gets a checkbox; the list also gets "Mark all read" and "Copy read marks" (fallback). Each tick saves itself, with no message from the owner:
   - The page POSTs `{"page": "<path under ~/projects>", "read": [titles]}` as `text/plain` to `http://127.0.0.1:18990/api/page-read` (the Observatory; it accepts only the :8000 page server's origin). On load it GETs `?page=<path>` to restore ticks. Keep localStorage as a cache.
   - Stored in `~/projects/plans/_observatory/data/page-read.json`, keyed by page path. The builder reads that file (plus `<project>/.page-read.json` for marks the owner said in chat, like "I read all").
   - On every rebuild, read items fold into the closed "Earlier updates (N, already read)" panel, unless absolutely critical (an open risk, data loss, a blocker); critical ones stay with a chip saying why. Pages that auto-rebuild (a refresh loop) fold within minutes; others fold on the next /page-update.
   - Show a status line after each tick: "Saved..." or "Not saved: Observatory is not running. Use Copy read marks."
   - Example: ai-local/scripts/bench/assess.py.
3. **Collect what changed since the owner last read it.** Look at this session's work, HARNESS §13 entries, watcher messages and fixed items. Each item gets one line saying what changed and one sentence saying what it means for the owner, with a number where there is one ("15 v3 shows 165 min of waiting").
4. **Build the new layout**, top to bottom, with nothing else:
   - **New since you read it (<date>)**: a status donut (done / no change / open), one lead line ("All 16 fixes done. Nothing open."), then a list. Each entry has a `New` chip, a bold title and one plain sentence.
   - **The <topic> in short**: the page's main chart (only one), plus up to 5 bullets. Each bullet is a headline number plus what was done about it ("35 h waiting; verify now goes first").
   - **Waiting on you (new, <date>)**: right under the New list, only the questions or approvals that appeared since the owner last read the page. Decision cards with a `New` chip, the recommended answer, a red Risk line and Copy choices. Omit the section when there are none.
   - **Open items / decisions still waiting**: older open items the owner has already seen, as decision cards with recommended answers and Copy choices.
   - **Closed panels** (`<details>`, closed by default): "All fixes (N done)" with the full status list, and "Your decisions" with each answer and a Done chip.
5. **Remove**:
   - sections the owner already absorbed (long explanations, single-incident timelines, per-cause bar charts);
   - artifact tables that only point at sources;
   - "suggestion, not done" notes that are now done;
   - the decision-count badge when nothing is open.
   - Keep the earlier version's numbers consistent; don't recompute them differently.
6. **Keep**:
   - theme, title prefix, URL and nav: section-jump links to New / Recap / Fixes, plus the Plans menu;
   - the SVG tab icon (design-all "Tab icon" rule): add one if missing;
   - one SVG chart per section (design-all rule); tables move into closed `<details>`;
   - if there is no builder, write one from the page's data files and rebuild from it.
   - collapsible sections (design-all `collapsible.html`);
   - `scroll-perf.mjs --home ../index.html` and `theme.py fix-chars`.
   - Rename the title to "... update (<date>)".
7. **Text**: humanizer rules. Plain words, no em dashes, the outcome first, under 2 lines per item.
8. **Verify**: Playwright at 1440 and 390 px with no console errors and no horizontal scroll, and look at the screenshot yourself. The new section must be visible without scrolling at 1440.
9. **Reply: no chat summary.** Everything the owner needs (findings, decisions, caveats, what changed) goes into the HTML. The chat reply is only the page path in two lines: `~/projects/...` and `http://localhost:8000/projects/...` (same path; the :8000 server root is ~/dev) (plus one line if something failed or is blocked).

## CSS used (neon-ops tokens)

- `.newlist` = panel list of `li{display:grid;grid-template-columns:86px 1fr}`. Each li has a `.chip`: green-dim background for New/Done, red tint for Open, purple-dim for No change.
- `.recap` = bullet list. `b{color:var(--green)}` holds the numbers.
- `.done-dec summary` = closed panel bar on `var(--panel)`, with a 1px `var(--line)` border and 10px radius.
