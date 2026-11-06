---
name: design-all
description: Run all three design skills in sequence from one prompt - ui-ux-pro-max (design system), then taste (build), then impeccable (critique and polish) - then a humanizer pass on the page text. Starts with an intake interview (data/files/research, purpose/audience, theme, human-summary style), favors animated SVG charts, self-contained offline HTML by default. For an existing UI, skips taste. Use when the user says /design-all or asks to use all three design skills.
disable-model-invocation: true
---

# design-all

Load ui-ux-pro-max, taste, impeccable and theme by reading `$HOME/.agents/skills/<name>/SKILL.md` directly (Read tool or cat), plus any files it points to. Do NOT call the Skill tool for them: they are user-only (`disable-model-invocation`), so Claude Code refuses it. The user invoking /design-all is the request to use them. humanizer, human-summary and dataviz can load either way.

## 0. Intake (always, before any work)

Ask before building anything. In Claude Code, call `EnterPlanMode`, then ask with `AskUserQuestion` (batch the questions; skip any the prompt already answers). In other agents (Codex, Pi, OpenCode), ask the same questions in plain text and wait for answers.

1. **Inputs:** which data, files or research to use (local files, a dataset, web research, or the prompt only)?
2. **Purpose and audience:** what the page must make clear, and to whom?
3. **Theme:** use an existing `/theme` (list with `python3 ~/.claude/skills/theme/theme.py list`) or create a new theme? Either way the design is dark mode.
4. **Human-summary:** build it as a `/human-summary` page or not? If yes, what style: **creative** (narrative, visual-first; the default, offer it first as Recommended) or **informational** (dense, scannable)?

Then present the plan (path, inputs, theme, charts planned) and exit plan mode. After approval, run straight through without pausing again.

## Path

- **New build:** ui-ux-pro-max -> taste -> impeccable -> humanizer.
- **Existing UI** (user points at an existing page/component): ui-ux-pro-max -> impeccable -> humanizer. Skip taste.
- **Human-summary = yes:** generate the content with `/human-summary`, then run the design steps on its output.

## Steps

1. **ui-ux-pro-max:** produce the design system (style, palette, fonts, UX rules).
   - Existing theme chosen: take palette and fonts from that theme; this step only sets layout, chart and motion rules.
   - New theme chosen: invent a short, creative, evocative theme name (e.g. `aurora-ledger`, `ink-tide`; never generic like `theme2`), then create `~/.agents/skills/theme/themes/<name>.css` following the theme skill's "Adding a theme" rules (ASCII only, all required tokens), and add its row to the theme skill's table.
2. **taste** (new build only): build the page with the step 1 system. Do not change palette or fonts.
3. **impeccable:** critique, then apply polish fixes. Keep the design system.
4. **humanizer** (always): rewrite the visible copy (headings, body, captions, labels) so it sounds natural, plain and short. Cut filler and AI patterns; keep each point to one simple sentence where possible. Never change data values, numbers, names, links or code. Keep the layout and markup intact.

## Defaults

- **Offline by default:** the HTML file must be fully self-contained: no CDN, no external fonts, scripts, styles or images. Inline all CSS/JS/SVG, use system font stacks, and do animation with CSS or small inline vanilla JS (no GSAP/D3 from CDN). Use a CDN only if the user explicitly asks.
- **No .md links:** never link `.md` files from the page (human-summary twins every linked .md). Link only if the user explicitly asks.
- **Charts:** use SVG heavily. Prefer animated SVG charts and graphs (draw-in lines, growing bars, counting numbers, staggered reveals of HTML elements) via CSS or inline vanilla JS, following the fast scroll motion rules below; respect `prefers-reduced-motion`. Every chart must show real data from the intake inputs, never placeholder numbers. Follow the `dataviz` skill if available.
- **Tab icon (every page, new or updated):** an inline SVG favicon as a data URI `<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,...">`, at most 3 shapes (rounded square in the theme `--bg`, one accent ring or glyph, one dot), no text. On updates, check it exists and is still simple.
- **One chart per section:** each `<main> > <section>` carries exactly one SVG chart or diagram with real data, placed before its text. Long tables and per-item lists go in closed `<details>` below it. No separate "charts" or "by the numbers" section.
- **Builder over hand-edits:** when a page is made from data files, write a small build script next to it (data json in, html out) so later updates rebuild instead of patching HTML.
- **Dark mode by default:** always design in dark mode (dark background, light text; set `color-scheme: dark`). Pick or create a dark theme, and make new themes dark. Use light mode only if the user explicitly asks.
- **Simple:** lots of whitespace, one idea per section, at most 2 accent colors.
- **Collapsible sections:** every `<main> > <section>` with a direct `<h2>` gets a show/hide toggle on its heading, plus Show all / Hide all in the header; state is remembered per page. Paste `collapsible.html` from this skill folder (its `<style>` in the head, its `<script>` before `</body>`). Keep sections as `<section>` + `<h2>` so it works, and nav links open a hidden section.
- **Scroll progress bar + back button + fast motion (every page, new or existing):** finish every page with
  `node ~/.agents/skills/design-all/scroll-perf.mjs [--home ../index.html] FILE.html...`
  It is idempotent and adds:
  - a thin accent bar (`--purple`) that fills as you scroll. It sits on the bottom edge of a sticky header, or fixed at the top when there is none, and an existing undriven `#prog` is adopted.
  - a `&larr; Plan home` pill button at the start of the header nav, or at the top of the page, on every page except the home page. Pages that already have a button-styled or arrow link home are left alone. `--home` defaults to the nearest `index.html` above the file.
  - runtime speed fixes: SVG child transitions are capped at 0.6s with no delay, and infinite animations pause offscreen.
  - shortened transitions for the known lantern chart classes (`.draw .gx .pop .fade`).
  - blurred headers made solid: any CSS rule with `backdrop-filter: blur(...)` loses the blur and its `rgba()` background becomes opaque.
  Generators should call its `inject(html, {home})` export; plan-status-page's `build.mjs` does. For a hand-built header you can paste `scroll-perf.html` instead (style in head, `<div class="prog" id="prog">` in the header, script before `</body>`). Then run the mjs anyway for the back button.
- **Fast scroll motion (always):** shapes inside an `<svg>` are not GPU-composited, so every frame of a transition on an SVG child (bar, dot, line draw) repaints the whole chart on the main thread. Measured on plan 03's index (4x CPU throttle): long staggered child transitions gave ~22ms average / ~47ms p95 frames while scrolling; short ones gave ~14ms / ~26ms.
  - SVG children: transitions of 0.6s or less (bars/dots ~0.45s, fades ~0.4s), **no per-element `transition-delay` stagger**. Stagger HTML elements instead.
  - Animate only `transform` and `opacity` (plus `stroke-dashoffset` for line draws). Never animate layout properties, `filter`, or `d`/geometry on scroll.
  - Prefer HTML/CSS bars (`div` + `transform:scaleX`) where a chart allows it; those are composited and cost almost nothing.
  - Infinite loops (dash flows, marquees, JS/GSAP `repeat:-1` tweens) pause while offscreen (`scroll-perf.html` handles `.flow`, `.loop`, `.marquee`; pause GSAP loops with a ScrollTrigger `onToggle`).
  - Reveal IntersectionObserver uses `rootMargin:'0px 0px 5% 0px'` so motion starts just before the element enters view; unobserve after reveal.
  - Scroll listeners are `{passive:true}` and rAF-throttled. `will-change` on an `<svg>` does not help; do not add it.
  - No `backdrop-filter: blur()` on sticky/fixed headers or other large layers: the browser re-blurs everything behind them every scroll frame (felt as laggy scroll on plan 03, worse without GPU acceleration on Linux). Use an opaque background in the theme's `--bg` color instead.
  - Keep `prefers-reduced-motion` turning all of this off.
- Apply theme rules: `<style id="theme" data-theme="NAME">`, then `theme.py fix-chars FILE.html`.

## Rules

- Load the design sub-skills by reading their SKILL.md files, never via the Skill tool (see top).
- Same session, no subagents.
- Finish with: path taken, theme (and new theme name if created), files written, charts built, fixes applied, text humanized, and the absolute path of the HTML file as the last line.
