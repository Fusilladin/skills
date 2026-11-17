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
| `cyberpunk` (default) | Neon green/purple/red glow, rounded pills, system font | Bundled reusable report theme |
| `digital` | Terminal green on near-black with a 42px grid, red top rule, Chakra Petch headings, Manrope body, JetBrains Mono labels, square 3-4px corners | Bundled reusable report theme |
| `cyberpunk-decisions` | Review-page look: neon green #39ff14 and purple chips, asymmetric 5/18px card corners, a solid purple active nav, green primary Copy button, 44px form fields | Bundled reusable report theme |
| `neon-ops` | Cyan and hot-pink orbital control-room glow, midnight violet panels, square grid, rounded cards | Bundled reusable report theme |
| `charcoal-amber` | Charcoal and burnt amber with yellow highlights, dark-first with full light mode; Bricolage Grotesque headings, Instrument Sans body, JetBrains Mono labels; pill nav and chips, outlined giant numerals, 6px cards, yellow-ruled callouts | Bundled reusable report theme |
| `vram-ember` | Warm graphite, ember orange + sage green, Iowan/Palatino serif headings, system sans body, 12px cards, pill nav | Bundled reusable report theme |
| `slate-tide` | Deep blue-slate, tide-teal accent with amber only for warnings, heavy Avenir/Segoe sans display, system sans body, mono labels, 12px cards, pill nav | Bundled reusable report theme |
| `silicon-dusk` | Blue-violet ink, lavender + lime, heavy Avenir/Segoe display, 14px cards, pill nav | Bundled reusable report theme |
| `kelp-terminal` | Sea-green black, phosphor mint + sand, Seravek/Gill Sans humanist display, mono data labels, 10px cards | Bundled reusable report theme |
| `copper-trace` | PCB green-black with a copper glow; copper, solder-silver, PCB-green and gold accents; embedded Space Grotesk display (OFL), system sans body, mono data, via-dot section markers, 8px cards, pill nav | Bundled reusable report theme |
| `midnight` | Compact midnight editorial layout, subtle 44px cyan grid, soft pink glow, cyan section headings, pink card titles, yellow callouts, 9px rounded cards, system fonts and monospace labels | Bundled reusable report theme |
| `ink-fold` | Charcoal, warm white, muted teal and amber; offline system serif headings, system sans body, flat reading surfaces, expandable email sections and compact category menus | Bundled reusable report theme |
| `noir-gallery` | recent.design gallery look in dark: near-black canvas, hairline 16px cards, pill chips and pill dropdowns, arrow-circle buttons, pink + mint accents, Iowan/Palatino serif display, Inter/system sans body | Bundled reusable report theme |
| `rose-ledger` | Plum-black canvas, rose-pink primary (#ff7ab6) and blush second accent, soft rose glow top-right, pill nav and chips, 12px cards, system sans display, mono labels | Bundled reusable report theme |
| `orbit-ledger` | Operations dashboard look: near-black #0b0c0e canvas, flat #121418 panels, hairline borders, 14px cards, pill nav, mint live-green + indigo accents, amber only for warnings, provider brand colours for charts, system sans + mono numbers | Bundled reusable report theme |
| `foundry-shift` | Night-shift factory floor: steel blue-black canvas, graphite panels with hairline seams, molten-amber primary + gauge-blue second accent, red only for faults, heavy condensed system display, system sans body, mono numbers, 14px cards, pill nav | Bundled reusable report theme |
| `mint-current` | Deep navy with a teal glow top-right, mint-teal primary + soft blue second accent, gradient 15px panels, tight Inter/system headings, sticky blurred header, teal pill nav and chips | Bundled reusable report theme |
| `frame-budget` | Profiler-at-16.7ms look: ink-black canvas, flat graphite panels with hairline seams, signal-blue primary for fast/chosen, coral second accent for cost/slow, embedded Archivo variable (OFL) display and body, mono numbers, 14px cards, pill nav, sticky opaque header | Bundled reusable report theme |
| `signal-console` | Calm operator console after linear.app: graphite canvas, hairline panels, mono status rows, electric teal for live, amber for needs-you, coral for down | Bundled reusable report theme |
| `brass-sextant` | Navigator's chart table at night: deep navy canvas, slate-blue panels, brass primary + seafoam second accent, red only for faults, Charter/Palatino serif display with small-cap labels, system sans body, mono bearings | Bundled reusable report theme |
| `velvet-ledger` | Bound ledger under a reading lamp: plum-black canvas, wine panels ruled with hairlines, old-gold primary + sage credits, rose debits, Charter/Georgia serif display and body with tabular numerals, 4-6px corners | Bundled reusable report theme |
| `blueprint-night` | Drafting table after dark: Prussian-blue canvas with a faint 24px drafting grid, chalk-cyan primary + chalk-white second accent, amber revision notes, Space Grotesk (embedded, OFL) or condensed system display, mono dimensions, square 4px corners | Bundled reusable report theme |
| `watchfire` | Fire-lookout tower at night: pine-charcoal canvas, smoke-green panels with hairline seams, flare-orange primary + ash-blue second accent, red only for faults, Rockwell/Roboto Slab display, system sans body, mono codes, 6px corners | Bundled reusable report theme |
| `assay-night` | Assay office after hours: soot-black canvas, iron-grey panels, assay-gold primary + verdigris second accent, red only for failing results, condensed system display, mono readings, 10px cards, pill nav | Bundled reusable report theme |
| `chalk-docket` | Court docket under a desk lamp: blue-black slate canvas, flat ink panels with hairline rules, chalk-white text, verdict-amber primary + steel-cyan second accent, coral only for faults, Noto Serif SemiCondensed (embedded subset, OFL) or Charter/Iowan display, system sans body, mono tabular figures, 12px cards, pill nav, opaque sticky header | Bundled reusable report theme |
| `lathe-night` | Machine shop after the last shift: cool graphite canvas, flat steel panels with hairline seams, machined-white text, tolerance-green primary (verified) + hot-coral second accent (slop, risk), Noto Sans Display Condensed (embedded subset, OFL) or Bahnschrift display, system sans body, mono gauges, 10px cards, square-cornered chips, opaque sticky header; sister of chalk-docket | Bundled reusable report theme |

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
