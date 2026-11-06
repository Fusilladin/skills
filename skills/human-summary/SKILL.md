---
name: human-summary
description: "Create or update HTML project summaries and interactive Q&A pages in place, keeping their design; adds artifact links and charts. Invoked as /human-summary."
---

# human-summary

Help the human understand project status, review artifacts, and answer open questions. Keep writing short, plain, and factual. Separate completed work from decisions needed; claim approval only when recorded.

## Existing HTML: preserve first

- Resolve the target from the user's path, active file when available, or conversation. Reuse a clearly identified existing summary. Ask which file only when the target is ambiguous; modification time alone is insufficient.
- Read the HTML source and edit that file directly, keeping its path. Make the smallest changes needed for the request.
- Preserve existing content, fonts, colors, effects, object shapes, corner radii, spacing, and general sizes, along with layout, charts, links, scripts, and responsive behavior. Match the actual page, even if it differs from a named theme.
- Reuse existing components and CSS tokens. Scope new styles and scripts to the added feature; avoid global overrides, class-name collisions, and changes to unrelated elements.
- Put Q&A where it belongs in the existing flow, such as beside the relevant build-sequence steps. Keep instructional content and avoid duplicating the same questions in another section.
- Do not run the full renderer on an existing page unless the user explicitly requests regeneration or replacement. Do not apply a theme stylesheet, redesign navigation, add a favicon, or impose other new-page conventions as part of a focused edit unless requested or necessary for that feature.
- Preserve existing decision IDs and local-save keys for unchanged questions. New or materially changed questions start unanswered and must not inherit stale answers.

## New summary

Create `human-summary.html` only when no existing target is identified or a new page is requested. Respect project instructions for output locations.

**Style default: creative.** New summaries are narrative and visual-first: a short story-style summary, a few titled sections that each make one point in plain sentences, and custom charts added after rendering. Use the informational style (dense status strip, every value in scannable items or tables) only when the user asks for it.

1. Discover with `python3 ~/.claude/skills/human-summary/render.py discover`. Read only relevant status files and the newest 1-2 review pages.
2. Write content JSON in `/tmp`. Required fields: `title`, `summary`, `needs_human`, `artifacts`; include `decisions` whenever `needs_human` is nonempty. All text fields are plain text; paths are relative to the project root.
3. Render with `python3 ~/.claude/skills/human-summary/render.py render /tmp/content.json -o TARGET.html --theme NAME`. New pages default to `cyberpunk`; use the user's requested theme, including `midnight`, via /theme.
4. Reuse a relevant project SVG favicon or create a compact ASCII-only icon with a square viewBox. The renderer requires one. Use category dropdown navigation with clear labels, grouping related pages through `nav_groups` and excluding noise through `exclude_pages`.

Minimal content example:

```json
{
  "title": "Project review",
  "summary": ["Where the project stands and what matters next."],
  "needs_human": [{"title": "Choose hosting", "detail": "Needed before deployment."}],
  "decisions": [{"id": "hosting", "title": "Hosting", "why": "Determines deployment.", "options": ["Managed", "Self-hosted"], "recommended": "Managed"}],
  "artifacts": [{"label": "Review", "path": "review.html", "note": "What to inspect."}]
}
```

Optional fields include `project`, `status`, `done_recently`, `nav_groups`, `exclude_pages`, and `sections`. Inspect `render.py` for their schema when needed. If the renderer inserts a default feedback section when there are no real questions, remove that section and its dedicated navigation link, controls, and script initialization from the output HTML before delivery.

## Interactive Q&A

Include Q&A only when there are real, unresolved questions that require human input, or the user explicitly requests a feedback form. Otherwise omit the entire section, its navigation link, progress badge, and answer controls. Do not invent a question to fill the space or add generic cards such as "Anything for the agent?", "Looks good, continue", or approval/notes prompts when no decision is needed. When updating a summary, remove such placeholder Q&A if there are no real questions, preserving unrelated content and behavior.

When questions are needed, let the human answer on the page and return those answers to the agent. The following requirements apply only when Q&A is present.

- Ask only relevant questions. Use clear labels, a short reason where helpful, 2-4 choices when appropriate, or a text field for answers such as an email address or time.
- Every question must include the model's recommendation with a brief reason. Put it first among substantive answer options and label it **Recommended**; an Undecided placeholder may precede it. For renderer JSON, put the recommended option first in `options` and set `recommended` to that same value. For text fields, show the suggested answer first, above the input. If a personal detail is unknown, recommend an explicit next step such as "Provide your recipient address" rather than inventing a value; leave that field unanswered until supplied.
- Start choices at Undecided and text answers empty; allow per-question notes. Provide local save, progress feedback, and working **Copy choices**, **Export JSON**, **Export Markdown**, and **Reset** controls. Reset clears this form's answers and saved state only.
- Place a **Use recommended** button at both the top and bottom of the Q&A. Both buttons apply recommendations only to questions still Undecided or empty, preserving existing answers and all notes. Fill text fields only when a concrete suggested value is available; keep requests for missing personal details unanswered. Save the updated state, refresh progress, and announce how many answers were applied and whether any still need input. Recommendations remain unselected until the user chooses an answer or clicks this button. Add these controls after rendering if the renderer does not supply them.
- Copy readable Markdown with stable question IDs, `Choice:` or `Answer:` lines, and `Notes:`. Include unanswered questions as Undecided. Provide a clipboard fallback and accessible status feedback, such as an aria-live region.
- Use keyboard-accessible controls with associated labels. Match the surrounding page's appearance; enlarge controls only as needed for usability.
- When delivering a page with Q&A, tell the user to click **Copy choices** and paste the result back. Treat pasted answers as decisions and notes as instructions.

## Charts and graphs

Add simple, beautiful, visually appealing charts when they clarify comparisons, trends, progress, or relationships. Use HTML, CSS, inline SVG, and JavaScript only where interaction helps. Match the surrounding design; preserve existing charts during updates.

Use real data, honest scales, clear titles, labels, units, and source context. Make visuals responsive and accessible, with readable contrast and a text takeaway or data table. Do not rely on color or hover alone. Embed additions in the HTML without new external dependencies. Renderer JSON escapes markup, so add custom charts to the output HTML after rendering.

## Finish and verify

- Keep pages standalone: no new paid APIs, uploads, or external dependencies. Limit project writes to the target HTML, required HTML artifact twins, and a favicon when creating a new summary.
- Link humans to HTML rather than Markdown. Reuse existing HTML twins; otherwise use `md2html.py`. Rendering Markdown links can recursively create twins; remove only unlinked twins created by this run.
- Keep output ASCII-only with a UTF-8 charset: entities in HTML, escapes in CSS/JavaScript. For manual edits, run `python3 ~/.claude/skills/theme/theme.py fix-chars TARGET.html` and inspect the resulting diff.
- Review the diff for unintended content or style changes. Check desktop and narrow layouts, links, keyboard access, local save, copy/export/reset, both Use recommended buttons, and existing interactions as applicable. Verify recommendations fill only unanswered questions and preserve answers and notes. State any checks that could not run.
- Return the output path and a short explanation of what changed and what needs review.
