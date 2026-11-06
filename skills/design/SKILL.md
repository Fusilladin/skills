---
name: design
description: "Design router for frontend and visual work: websites, landing pages, dashboards, app screens, components, brand assets, banners, slides. Picks taste, impeccable or ui-ux-pro-max, then hands off."
license: MIT
---

# design (router)

Pick ONE skill below, then load it and follow it. Loading means: invoke it by name with the current agent's skill mechanism, or read its `SKILL.md` from `$HOME/.agents/skills/<name>/SKILL.md` if the agent has no skill tool or the skill tool refuses it (these skills are hidden from auto-invocation). Do not do the design work in this skill.

## 1. Check what already exists

- **A named skill or style wins.** If the user said "taste", "impeccable", "brutalist", "polish", "audit" and so on, go straight to that skill.
- **An existing look wins over a new one.** If the project has a design system, DESIGN.md, PRODUCT.md, or a named theme (for example a `/theme` such as `ic`), tell the chosen skill to work inside it rather than invent a new aesthetic.

## 2. Route

| What is needed | Skill | Why |
|---|---|---|
| A new page, site, portfolio or app screen from scratch | **taste** | Opinionated anti-template builds; picks a style direction |
| A full new look for an existing site ("make it look premium", "redesign it") | **taste** (its redesign sub-skill) | Replaces the aesthetic while keeping function |
| Design reference images, mobile screen concepts, brand-kit boards | **taste** (image sub-skills) | Image-first workflows |
| Review, audit, critique, or score an existing UI | **impeccable** | Structured audit and critique commands |
| Polish, harden, fix spacing/typography/color/motion, make bolder or quieter, responsive or accessibility fixes on existing UI | **impeccable** | Targeted refinement commands |
| Onboarding, empty, error or loading states; live in-browser tweaking | **impeccable** | Dedicated commands |
| "Which palette / fonts / style suits a <product type>?" | **ui-ux-pro-max** | Searchable style, palette and font database |
| Design tokens, a MASTER.md design system, shadcn/Tailwind setup | **ui-ux-pro-max** | design-system and ui-styling sub-skills |
| Brand voice and identity, logos, banners, social images, HTML slide decks | **ui-ux-pro-max** | brand, design, banner-design and slides sub-skills |

## 3. Combining

Use at most two, in this order, and say so to the user:
1. **ui-ux-pro-max first, then taste:** look up palette and fonts for the product type, then build with taste.
2. **taste first, then impeccable:** build, then run an impeccable audit or polish pass.

## 4. When unclear

If the request fits two rows equally (for example "make my site better"), ask one question: "A fresh new look (taste) or improve what's there (impeccable)?" Default to **impeccable** when existing UI code is present and the user did not ask for a new look; default to **taste** when there is nothing to start from.
