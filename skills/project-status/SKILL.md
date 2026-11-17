---
name: project-status
description: Write or refresh STATUS.md in the current client/project repo so a zero-context agent can pick up where the last session left off weeks later. Reviews the whole session, git log/status and existing STATUS.md, then updates it in place. Invoked as /project-status [notes].
---

# project-status

Goal: one file, `STATUS.md` at the project root, that a new agent with zero context
can read in two minutes and know what the project is, what's done, and what's next.

## Steps
1. Gather facts, don't guess:
   - Re-read this whole session: decisions, deploys, commands the owner ran, confirmations
     ("it worked"), things the owner said are irrelevant or done.
   - `git log --oneline -15`, `git status -s`, and the existing STATUS.md / AGENTS.md / README.
   - Respect project privacy rules (e.g. AGENTS.md wrappers); never copy secrets or client data.
2. Update STATUS.md in place (create it if missing). Keep these sections:
   - **Last updated:** today's absolute date.
   - **What this project is**: 2-4 lines.
   - **Where things stand**: what's live and working, with commit hashes, image or service names, dates.
   - **Open items**: numbered, each with who's waiting on what and the next concrete action.
   - **Handy commands**: only the ones that recur.
   - **Gotchas**: traps that cost time.
   Remove items that are finished or that the owner called irrelevant; don't keep history (git has it).
3. Make sure AGENTS.md (or CLAUDE.md) has the line
   "Read STATUS.md first; update it at the end of a session (skill: project-status)." Add it if missing.
4. Don't commit unless asked. Reply with done plus the open items, 1-3 lines each.

## CRITICAL GIT RULES

- Never commit, amend, merge, rebase, cherry-pick, or switch branches.
- Never delete, discard, revert, overwrite, clean up, or otherwise remove any existing Git change.
- Never run `git reset`, `git restore`, `git checkout`, `git clean`, `git stash`, or an equivalent destructive/discarding command.
- Never stage new changes or unstage existing changes.
- Preserve all unrelated modified, staged, and untracked files exactly as found; do not alter another person's changes.
- Leave completed changes only in the working tree.
- If files or changes unexpectedly appear, disappear, or change during work, stop and report the concurrent-worktree conflict; do not reconstruct, revert, or clean anything.
