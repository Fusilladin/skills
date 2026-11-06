---
name: next-steps
description: Write or refresh a "next steps" HTML page for any task or project, listing the setup or rollout steps still left in order (owner actions, sudo commands, purchases, confirmations, steps waiting on a build), each with a status from a real check, who acts, why, copyable commands and an undo. Invoked as /next-steps [project or topic]. Not the plans approvals page (that is plan-status-page).
---

# next-steps

`/next-steps [project or topic]` writes `next-steps.html` for a task or project: the steps still left before something works, in the order they must happen. It works for any folder or topic, not only plans in `~/projects/plans`.

Reference page: `~/projects/plans/10-agent-sandbox/next-steps.html` (plan 10 Incus rollout, 2026-10-22). Skeleton: `template.html` in this folder. Check runner: `check.sh` in this folder.

## How this differs from plan-status-page

`plan-status-page` (in `~/projects/plans/.claude/skills/`) builds a plan's `approvals.html`: every approval item and decision the Observatory knows, with calls saved back to the Observatory, rebuilt automatically. `/next-steps` is a short, hand-made, ordered checklist for one rollout or setup job in any project: what to run, buy or confirm next, with live status checks and copyable commands. It saves nothing outside the browser and nothing rebuilds it. For a plan, the next-steps page links the plan's `approvals.html` when one exists, and does not repeat its decision cards.

## Inputs

1. Work out the target from the argument: a folder path, a plan number or slug (`10`, `10-agent-sandbox`), or a topic in the current project. If it is unclear which project or rollout is meant, ask once.
2. Output path: `<project>/next-steps.html`, or `<project>/next-steps-<topic>.html` when the project has more than one rollout. If a page already exists there, refresh it: keep its step ids (so saved checkmarks still match), update statuses, add and remove steps.
3. Read the sources:
   - Plan projects: `PLAN.md`, `_build/VERIFY.md` (verdict, what is mocked, how to make it real), `_build/DEFERRED.md` (owner items, exact commands, "Next step" lines), any spec the rollout names (e.g. `INCUS-SPEC.md`), the newest `_run/handoff/` brief for it.
   - Other projects: README, setup/deploy docs, TODO notes, the conversation so far.
4. Theme: if the project has a theme (`theme/*.css`, or the `<head>` of its `index.html`), link or copy that head and delete the fallback `<style id="fallback-theme">` block. With no theme, keep the fallback (it has light and dark tokens). Never invent colours: the page rules use only `--bg --panel --panel2 --text --muted --line --green --amber --red --purple --mono --body`. If the theme lacks one, define it from the theme's existing values.

## Statuses come from real checks (required)

Never assume a status, and never copy one from a doc without checking it now.

1. For each step, pick a read-only check that shows whether it is done: `command -v X`, `X --version`, `id -nG | grep -w grp`, `test -e path && echo yes`, `systemctl --user is-active svc`, `lsmod | grep mod`, `ls -l file` (mode), `curl -s -o /dev/null -w '%{http_code}' URL`, a grep in VERIFY.md/DEFERRED.md. Never put sudo, installs, purchases, network writes or anything that changes state in a check.
2. Write them to a scratch TSV (`<step-id><TAB><command>`) and run `~/.agents/skills/next-steps/check.sh FILE.tsv`. Read every result.
3. Set the status from the result:
   - `done`: the check proves it. Badge `done`.
   - `you`: the owner must act. Badge `you · sudo`, `you · paid`, `you · reply` or `you · login`.
   - `wait`: blocked on something else. Badge `waits on <thing>` (a build, another step, a reply).
   - `claude`: an agent can do it without the owner. Badge `by Claude`.
   - If no check is possible (a purchase, a policy confirmation), say so: `Check: none possible; DEFERRED.md §A item 6 still open`. If a check fails to run or times out, the status is "unknown", not done.
4. Show the check behind every status on the page, in the step's `.chk` line: the command, what it printed (short) and when. Example: `Check: incus --version → 6.0.4 (2026-10-22 09:40)`.
5. For plan projects, cross-check VERIFY.md and DEFERRED.md: a step a doc calls open but the check shows done is `done` (mention the doc is behind); a step a doc calls done but the check fails is not done.

## Page contents (copy the reference structure)

- **Header:** a stamp (`Plan 10 · Agentbox v3` or the project name) and a nav. For a plan, link `index.html` and, when it exists, `approvals.html`.
- **Hero:** `<h1>` "<Thing>: next steps", a lede of 2-3 sentences saying what is left before what works and what does not need these steps, the date, and "Checkmarks are saved in this browser only." Then the summary counts (`#sum`: done / total, waiting on the owner, waiting on something else), filled by the script.
- **Steps:** an ordered list, one `<li class="step">` per step, in the order they must happen; merge steps that are one command (the reference's "3–4"). Each has a stable `data-id`, `data-st`, a checkbox, a numbered title with the status badge and a `.who` tag when useful (`by Claude`), one or two plain sentences on what and why, copyable commands (`.cmd` with a `data-copy` button holding the exact text), a `<details class="undo">` with the undo command for anything that changes the system (sudo, config, firewall, installs), and the `.chk` line. For replies, give the exact reply to copy ("yes to 6-8"). Never put a secret in a command or a page; say where the owner puts it instead ("in the folder below; never paste it in chat").
- **Options and costs** (optional): a table when the owner must buy or choose something: need, default, alternatives, cost or limit with the date checked. Give prices only from a source you read; otherwise write "not checked" and say where the build confirms them.
- **Sources:** the files and URLs used.
- **Script:** as in `template.html`: one localStorage key per page (`<topic>-next-steps-v1`), every storage read and write wrapped in try/catch, a box defaults to checked when its status is `done`, the summary re-renders on change, copy buttons fall back to "Select and copy".

## Writing rules

Presentation rules: plain language, and the reader is "the owner" or "you". Never write a person's name, including in commands' comments; use generic home-relative paths. Roles for everyone else (client, builder, watcher).

- One idea per sentence, everyday words. Explain any term the owner needs (WireGuard, bridge, preseed) in a few words the first time.
- Keep numbers exact; label estimates as estimates. If the sources do not say, write "not measured" or "not checked".
- File paths and commands belong in `code`/`.cmd` blocks, not in the prose.
- No `.md` links (link HTML pages only; name `.md` files as plain text in Sources).

## Check the result

1. Grep the page: no `{{` placeholders left, no person's name, no secrets, every step has a `.chk` line.
2. Open it at 1280 and 390 wide with Playwright (`require('playwright')`; scroll with `behavior:'instant'`). Look for: no horizontal scroll at 390 (`document.documentElement.scrollWidth <= innerWidth`), no page errors, the summary shows the right counts, a checkbox click survives a reload.
3. Reply with the page path (`~/...`), the counts (done / you / waiting) and the next owner step.
