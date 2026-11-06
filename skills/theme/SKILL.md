---
name: theme
description: Pick or apply a named visual theme for generated HTML pages (human summaries, review pages, Markdown twins, reports). Themes include cyberpunk (default), digital, cyberpunk-decisions, neon-ops, and midnight. Use when the user runs /theme NAME, asks for a page "in the digital/cyberpunk/midnight style", or wants an existing HTML file restyled. Also fixes broken special characters (mojibake) in HTML files.
disable-model-invocation: true
---

# theme

The themes live in `~/.claude/skills/theme/themes/<name>.css`. List them with:
`python3 ~/.claude/skills/theme/theme.py list`

| Theme | Look | Based on |
|---|---|---|
| `cyberpunk` (default) | Neon green/purple/red glow, rounded pills, system font | the original /human-summary theme |
| `digital` | Terminal green on near-black with a 42px grid, red top rule, Chakra Petch headings, Manrope body, JetBrains Mono labels, square 3-4px corners | `leads/audits/audit_deep_dive.html`, plus higher-contrast muted text, focus rings, reduced-motion and print rules |
| `cyberpunk-decisions` | Review-page look: neon green #39ff14 and purple chips, asymmetric 5/18px card corners, a solid purple active nav, green primary Copy button, 44px form fields | `video-editing/out/greed_and_darkness/review4`, `review5` (workspace.css + project-nav.css) |
| `neon-ops` | Cyan and hot-pink orbital control-room glow, midnight violet panels, square grid, rounded cards | `/pi-harness-guide/human-review.html` |
| `project` | Charcoal and burnt amber with yellow highlights, dark-first with full light mode; Bricolage Grotesque headings, Instrument Sans body, JetBrains Mono labels; pill nav and chips, outlined giant numerals, 6px cards, yellow-ruled callouts | `project/docs/changes.html` (reusable copy: `ic/docs/assets/ic.css` + `ic.js`) |
| `vram-ember` | Warm graphite, ember orange + sage green, Iowan/Palatino serif headings, system sans body, 12px cards, pill nav | `gpu/local-ai-value.*.html` (design-all, 2026-10) |
| `slate-tide` | Deep blue-slate, tide-teal accent with amber only for warnings, heavy Avenir/Segoe sans display, system sans body, mono labels, 12px cards, pill nav | `leads/notes/2026-10-pi-supervise-loop-explainer.html` (design-all, 2026-10) |
| `silicon-dusk` | Blue-violet ink, lavender + lime, heavy Avenir/Segoe display, 14px cards, pill nav | `gpu/local-ai-value.*.html` (design-all, 2026-10) |
| `kelp-terminal` | Sea-green black, phosphor mint + sand, Seravek/Gill Sans humanist display, mono data labels, 10px cards | `gpu/local-ai-value.*.html` (design-all, 2026-10) |
| `copper-trace` | PCB green-black with a copper glow; copper, solder-silver, PCB-green and gold accents; embedded Space Grotesk display (OFL), system sans body, mono data, via-dot section markers, 8px cards, pill nav | `video-analyzer/topics/2026-10-12-cheap-vram-gpus/knowledge-summary/buying-guide.html` (design-all, 2026-10) |
| `midnight` | Compact midnight editorial layout, subtle 44px cyan grid, soft pink glow, cyan section headings, pink card titles, yellow callouts, 9px rounded cards, system fonts and monospace labels | `ai-models-free/daily-digest-next-steps.html` |
| `ink-fold` | Charcoal, warm white, muted teal and amber; offline system serif headings, system sans body, flat reading surfaces, expandable email sections and compact category menus | `email-compactor/build-plan.html` (design-all, 2026-10) |
| `noir-gallery` | recent.design gallery look in dark: near-black canvas, hairline 16px cards, pill chips and pill dropdowns, arrow-circle buttons, pink + mint accents, Iowan/Palatino serif display, Inter/system sans body | `plans/01-analytics-dashboard/index.html` (design-all, 2026-10) |
| `rose-ledger` | Plum-black canvas, rose-pink primary (#ff7ab6) and blush second accent, soft rose glow top-right, pill nav and chips, 12px cards, system sans display, mono labels | `slate-tide` structure, recoloured for `email-sequence/human-summary.html` (design-all, 2026-10) |
| `orbit-ledger` | Run Observatory look: near-black #0b0c0e canvas, flat #121418 panels, hairline borders, 14px cards, pill nav, mint live-green + indigo accents, amber only for warnings, provider brand colours for charts, system sans + mono numbers | `plans/_observatory/index.html` (design-all, 2026-10) |
| `foundry-shift` | Night-shift factory floor: steel blue-black canvas, graphite panels with hairline seams, molten-amber primary + gauge-blue second accent, red only for faults, heavy condensed system display, system sans body, mono numbers, 14px cards, pill nav | `plans/_reports/week-2026-10-27/index.html` (design-all, 2026-10) |
| `mint-current` | Deep navy with a teal glow top-right, mint-teal primary + soft blue second accent, gradient 15px panels, tight Inter/system headings, sticky blurred header, teal pill nav and chips | `youtube-strategy/yt-growth.html` + `value-offer.html` (design-all, 2026-10) |
| `frame-budget` | Profiler-at-16.7ms look: ink-black canvas, flat graphite panels with hairline seams, signal-blue primary for fast/chosen, coral second accent for cost/slow, embedded Archivo variable (OFL) display and body, mono numbers, 14px cards, pill nav, sticky opaque header | `plans/67-dash-engine/stack-compare.html` (design-all, 2026-11) |

## Choosing the theme

- `/human-summary` with no theme mentioned → `cyberpunk`.
- `/theme NAME` (or "in the NAME style") → use NAME for whatever page you build or restyle in that request.
- An unknown name → run `theme.py list` and ask which one; never guess a new look.

## How to use it

1. **Human summary page:** follow the /human-summary workflow and render with `--theme NAME`:
   `python3 ~/.claude/skills/human-summary/render.py render CONTENT.json --theme NAME [-o OUT]`
   Markdown twins it converts get the same theme. Standalone: `python3 ~/.claude/skills/human-summary/md2html.py --theme NAME FILE.md`.
2. **A page these tools generated** (it has `<style id="theme">`): switch it in place:
   `python3 ~/.claude/skills/theme/theme.py apply NAME FILE.html`
3. **Any other HTML file:** restyle it by hand.
   - Read `themes/NAME.css` and map the page's colours, fonts, radii and accents onto that theme's tokens (`--bg --panel --panel2 --line --text --muted --green --purple --red --amber`, plus `--mono --display --body` for digital).
   - Keep the page's structure and behaviour. Change only styles.
   - Put the result in a `<style id="theme" data-theme="NAME">` block, so `apply` can switch it later.
   - Then run `theme.py fix-chars FILE.html`.
4. **A new page you write yourself:** start the `<head>` with `<meta charset="utf-8">`, then paste `theme.py css NAME` into `<style id="theme" data-theme="NAME">`.

## Required page features (all themes)

Every review/summary page built with a theme must have:
- **Category dropdowns in the top bar** instead of a flat row of links (`nav details > summary + .menu`). Only one opens at a time; it closes on outside click, on choosing a link, and on Esc.
- **Scroll progress bar, back button and fast scroll motion:** finish every page (rendered, restyled or hand-built) with `node ~/.agents/skills/design-all/scroll-perf.mjs FILE.html`. The bar uses the theme's `--purple` accent and the button uses `--line`/`--panel`, so every theme styles them. See design-all for the SVG motion rules: short SVG child transitions, no stagger, loops paused offscreen.
- **A Copy-for-agent section:** decision cards with Undecided defaults, notes, and the buttons **Copy choices / Export JSON / Export Markdown / Reset**. Choices are saved locally.

/human-summary's `render.py` produces the dropdowns and Copy-for-agent section automatically (run scroll-perf.mjs after it), so prefer rendering through it. When you hand-build or restyle another review page, add both, matching its markup (`nav details`, `.menu`, `.decision`, `#dec-copy`) so every theme styles them.

## Special characters (all themes, required)

Broken characters such as `â€”` happen when a page has no charset declaration and a server (e.g. `python -m http.server`) sends it without one. Every page must:
- start with `<!doctype html>` and `<meta charset="utf-8">`, and
- contain only ASCII: entities (`&mdash;` `&rarr;` `&middot;`) in HTML text, `\u2014` escapes in JavaScript, and `\2013` escapes in CSS.

`render.py` and `md2html.py` already write ASCII-only output. For any other page, finish with:
`python3 ~/.claude/skills/theme/theme.py fix-chars FILE.html`
It adds a missing doctype/charset and entity-encodes non-ASCII text outside scripts and styles. Never put raw symbols in a theme CSS file; `theme.py` refuses to load one that has them.

## Adding a theme

Add `themes/<name>.css`, ASCII only, defining the tokens above and styling the shared class contract used by /human-summary:
`header .bar h1 .stamp nav nav a nav details nav summary nav .menu main .strip .card .card.pending .status(.ok .info) .l .muted section h2 h3 .links .missing .table-wrap table th td tr.nh ul .items .item(.shot) .src .doc` (+ `.doc` children), plus the decision UI `.decision .did .recline .choice .dec-tools .actions button #dec-status` when it should differ from the default.
Then render one summary with `--theme <name>` and check it at desktop and phone width. Add a row to the table above.
