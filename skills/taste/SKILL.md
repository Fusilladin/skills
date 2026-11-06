---
name: taste
description: "Build a NEW landing page, portfolio, marketing site or app screen with a distinctive, non-templated look, or generate design reference images. Routes to taste-skill styles: default v2, soft/premium, minimalist, brutalist, GSAP motion, image-to-code, website or mobile design images, brand-kit boards, Google Stitch DESIGN.md, or a full aesthetic overhaul of an existing site. For critique or polish of existing UI use impeccable; for palette, font or design-token lookups use ui-ux-pro-max."
disable-model-invocation: true
license: MIT
metadata:
  source: https://github.com/Leonxlnx/taste-skill
---

# taste

Router for the taste-skill collection. Pick ONE sub-skill from the table, read its `SKILL.md` in full, and follow it as if it had been invoked directly. Sub-skill paths are relative to this skill's folder (`$HOME/.agents/skills/taste/`). Load a second sub-skill only when the table says it combines.

| Task | Sub-skill | Read |
|---|---|---|
| New landing page, portfolio or site; no style named (default) | design-taste-frontend (v2) | `subskills/taste-skill/SKILL.md` |
| Upgrade or audit an existing site or app without breaking it | redesign-existing-projects | `subskills/redesign-skill/SKILL.md` |
| Expensive, soft, agency look: premium fonts, whitespace, depth | high-end-visual-design | `subskills/soft-skill/SKILL.md` |
| Clean editorial, Notion/Linear-style monochrome | minimalist-ui | `subskills/minimalist-skill/SKILL.md` |
| Raw Swiss/terminal brutalism, data-heavy dashboards (beta) | industrial-brutalist-ui | `subskills/brutalist-skill/SKILL.md` |
| Awwwards-style GSAP motion, AIDA structure, bento grids | gpt-taste | `subskills/gpt-tasteskill/SKILL.md` |
| Generate design images first, then code the site to match | image-to-code | `subskills/image-to-code-skill/SKILL.md` |
| Website design reference images only (no code) | imagegen-frontend-web | `subskills/imagegen-frontend-web/SKILL.md` |
| Mobile app screen concepts as images only (no code) | imagegen-frontend-mobile | `subskills/imagegen-frontend-mobile/SKILL.md` |
| Brand-kit / identity board images (no code) | brandkit | `subskills/brandkit/SKILL.md` |
| DESIGN.md for Google Stitch | stitch-design-taste | `subskills/stitch-skill/SKILL.md` |
| Exact v1 behavior only, when a project depends on it | design-taste-frontend-v1 | `subskills/taste-skill-v1/SKILL.md` |

**Combines with any of the above:** `subskills/output-skill/SKILL.md` (full-output-enforcement) when the job needs complete, unabridged code with no placeholders.

## Rules

- If the request is ambiguous between two rows, ask which look the user wants instead of guessing; default to `taste-skill` (v2) when they have no preference.
- The image sub-skills need an image-generation tool. If the current agent has none, say so and offer the code-only route (`taste-skill` or `redesign-skill`).
- Project instructions and an existing design system or theme take precedence over a sub-skill's defaults.
- One-line summaries of every sub-skill are in `llms.txt`.
