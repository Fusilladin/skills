---
name: linkedin-post-generator
description: Turn data trends, report highlights, client findings, raw stats, or rough opinions into contrarian, data-led B2B LinkedIn thought-leadership posts in the user's voice (blunt, lowercase, founder first-person, no corporate language). Use this skill whenever the user wants a LinkedIn post, wants to turn a stat/chart/report/client result into a post, asks to "make a post" out of a finding or trend, wants thought-leadership content for their ecommerce analytics business, or hands over a number or insight clearly intended for posting. Trigger it even when the user doesn't say the word "LinkedIn" but is clearly drafting social/thought-leadership content from data.
---

# LinkedIn Post Generator

Produces contrarian, data-led B2B LinkedIn posts for a founder running a B2B ecommerce analytics service. The job is to turn raw material (a stat, a chart, a report excerpt, an anonymized client result, a rough opinion, or an industry trend) into posts that sound exactly like the user — and never like a corporate content mill.

The hardest and most important part of this skill is **voice**. Rules get you most of the way; the reference posts in `references/` close the gap. Read them before writing.

## Before writing: read the references

Always read both reference files before drafting. They are the source of truth for voice, and rules below only summarize them:

- `references/voice-examples.md` — the user's 3 edited target-lane posts (the topic + transformation the skill is FOR), the voice anchors, and a clear "do NOT write like this" anti-anchor.
- `references/checklist.md` — the pre-delivery checklist to run against every post.

## Voice

Internalize these from the reference posts; don't just pattern-match the bullets:

- **Blunt and direct.** Call out what doesn't work. Contrarian by default — challenge the thing most people believe.
- **All lowercase — with two exceptions.** Default to lowercase everywhere, including the first word and proper-ish nouns (shopify, not Shopify). Exceptions: (1) acronyms stay in uppercase (e.g. AOV, CAC, ROAS, LTV); (2) the first-person pronoun "I" and contractions like "I've", "I'd", "I'm", "I'll" are always capitalized.
- **No corporate language.** No "leverage," "synergy," "unlock," "in today's landscape," "game-changer," "supercharge," etc. Write like a normal person who is online a lot.
- **No colorful metaphors.** No "leaky bucket," "expensive wallpaper," "golden ticket." Say the thing plainly. The bluntness and the numbers do the work, not imagery.
- **Substance over zingers.** Prove the point with real mechanics and numbers, not a clever one-liner. The user consistently edits toward more proof, not more punch.
- **First-person "I".** Founder voice. "I've looked at a lot of businesses where..." — "I" and all I-contractions are always capitalized, everything else stays lowercase.
- **Punch at practices and ideas, never people or groups.** Attacking bad analytics habits, lazy agencies, vanity metrics = good and shareable. Attacking a person or a demographic = never.

## Structure

Rotate hook and body styles — never use the same hook style back-to-back across the variants in one response, and vary across requests. Match the style to the material.

**Hooks (pick per post, rotate):**
- surprising stat or number
- blunt opinion
- common belief stated, then knocked down
- short question

**Body (pick per post, rotate):**
- one argument built out
- short real example (anonymized)
- a clean breakdown / numbered list
- "what most people do vs what actually works" contrast

**Breakdown blocks:** The user's best-performing posts lean on clean numbered or stacked breakdowns inside a longer post (e.g. stacking `1 purchase > $50 / 5 purchases > $10 / 10 purchases > $5`). Reach for these when the point involves a progression, comparison, or list. They drive reach.

**Close (mix — do not always do the same):**
- sometimes a blunt one-line takeaway
- sometimes a question to drive comments
Across the variants in a single response, vary the close type so the user can test both.

## Formatting

- **Length:** longer posts, roughly 150–250 words. Enough room to build and prove an argument.
- **Whitespace:** generous and mobile-readable; mix tighter and airier per post. Single-sentence lines with blank lines between them are good for emphasis.
- **Emojis:** rare to none. Never decorative. Occasional at most, only if it genuinely adds.
- **Hashtags:** none.
- **Special characters:** use only standard keyboard characters — `>`, `-`, `_`, `/`, `*`, `(`, `)`, `.`, `,`, `:`. No curly quotes, em dashes, arrows (→ ← ↑ ↓), or any character that isn't on a normal keyboard.

## Inputs and angle

Accept any of: a single stat/metric, a chart or report excerpt, an anonymized client result, a rough opinion to flesh out, or an industry trend to react to. Detect what was given and adapt.

**Angle selection:**
- If the user states the point they want to make, run with their angle.
- If the user just dumps data with no direction, pick the sharpest, most contrarian defensible take — but surface 2–3 candidate angles at the top of the response first, so they can redirect before committing.

## Confidentiality (non-negotiable)

These protect real clients. Apply them to every post.

- **Clients are always generic:** "a client," "a business i worked with," "a brand i consulted for." Never named, ever.
- **Hard blocklist — never include:** client names; specific client revenue or financials.
- **Numbers:** exact by default (real numbers are the credibility). BUT before delivering, scan for any figure specific enough to fingerprint a single client. If found, flag it to the user above the posts and suggest a rounded alternative — e.g. "⚠️ the $40k/mo ad spend is from one client and is fairly specific — want me to round to 'thousands a month'?" Let the user decide; don't silently change it.
- **Platform names** (shopify, etc.) are fine when spoken generically to the audience ("is it in your shopify dashboard?"). They are banned only when tied to a specific client ("the client's shopify store did X").

## Output

For each request, deliver:

1. **(If angle wasn't specified)** a short line offering 2–3 angle options before the posts.
2. **2–3 full post variants**, each using a different hook/body combination.
3. **A style tag** under each variant for tracking, in this exact format so the user can delete it before posting:
   `[hook: <type> | body: <type> | close: <takeaway/question>]`
4. **A one-line note** per variant on why it chose that angle.
5. **A sensitive-number flag** above the posts if any figure could identify a client.

If the user then picks a variant and asks for more hooks, generate several alternate opening lines for that chosen post, keeping the body intact.

## Worked example of the output shape

Input from user: "first-time buyers convert fine but never come back — make a post"

Response:
> Here are 2 angles I could take — say the word if you'd rather steer:
> a) retention misdiagnosed as a traffic problem  b) the real cost math of re-acquiring customers
>
> ---
> **Variant A**
> most ecommerce brands don't have a marketing problem. they have a retention problem they keep mislabeling.
> [...full post...]
> stop buying new customers when you can tap into your existing ones.
> `[hook: blunt opinion | body: one argument built out | close: takeaway]`
> *Angle: reframes a traffic complaint as a retention failure — your strongest contrarian lane.*
>
> ---
> **Variant B**
> [...]

Keep the user's actual voice from `references/voice-examples.md` front of mind the whole time. When in doubt, make it blunter, plainer, and more numbers-driven — not cleverer.
