---
name: update-skills
description: Audit and maintain agent-neutral global and project skills across Claude, Codex, and other coding agents. Use when asked to update-skills, synchronize skill libraries, copy Claude or Codex skills into .agents/skills, or make skill instructions portable across agents. Preserve source skills, existing changes, resources, and genuine provider requirements.
disable-model-invocation: true
---

# Update skills

Use the current host agent and its available filesystem tools. This skill does not require a particular model, provider, CLI, browser, or subagent. Honor the user's selected scope and models. Do not delegate unless explicitly requested. Updating a skill library does not authorize running its workflows, paid API calls, or external writes.

## Scope and discovery

Default global destination: `~/.agents/skills`. Default project search root: `~/projects/dev`; use an explicit user path instead when supplied. Inspect global `~/.claude/skills`, `~/.codex/skills` (respect `CODEX_HOME` if set), and `~/.agents/skills`. Inspect project `.claude/skills`, `.codex/skills`, and `.agents/skills`, including nested projects. Read applicable project `AGENTS.md` before project writes.

Look for skill packages containing `SKILL.md`. Include personal Claude `synced/<bucket>/<skill>` packages, flattening only the destination layout. Exclude provider-managed `.system`, plugin caches/bundles, Git internals, dependencies, virtual environments, generated outputs, and fixtures inside skill packages. Do not copy arbitrary repository-root `SKILL.md` files unless an established skill link or the user identifies them as skills.

Global skills belong in `~/.agents/skills/<name>`. Project skills belong in `<project>/.agents/skills/<name>`. Preserve project scope; do not promote project skills globally. For established global links into a project, make both global and project-local portable copies when the request includes both scopes. Discover the linked project from the filesystem rather than hardcoding project names.

## Safe copy and update

1. Inventory sources, canonical destinations, symlinks, existing differences, and relevant dependencies. Record initial fingerprints and Git status for touched paths. Never expose credentials from skill resources.
2. Resolve skill-root symlinks before choosing what to copy. **Never copy an entire linked project as a skill.** A repository-root link usually needs only `SKILL.md`; retain its references to existing project tools. Copy relative supporting resources only when the entry point requires them. A link to a dedicated skill package may include its scripts, references, assets, and metadata. Inspect resource symlinks; preserve their links and never follow them into unrelated trees or transform their targets.
3. Create missing portable packages without modifying sources. Preserve required resources and executable modes. Detect duplicate names before writing: identical packages can share a destination; differing packages are conflicts, not a reason to silently pick one or overwrite.
4. For existing portable packages, inspect differences first. Preserve modified, staged, untracked, and user-edited files. Update a clean tracked file only within the requested scope; update an untracked/global generated copy only when a recorded previous synchronization fingerprint proves it has no intervening edits. Without that evidence, leave it intact and report the conflicting source and destination. Do not create duplicate suffixed skills merely to avoid a conflict.
5. Recheck fingerprints immediately before each write. Stop and report unexpected concurrent changes. Use exclusive creation for new files and directories. If interrupted, retain and report partial state; a retry must verify it rather than blindly overwrite or delete it.

Use standard filesystem tooling or a narrowly scoped helper when useful. A preview should enumerate actual writes and conflicts. Do not automatically run a historical copier without inspecting it: hardcoded paths, symlink traversal, and assumptions about existing destinations can be wrong.

## Make instructions portable

Preserve the workflow's intent, authorization boundaries, and operational constraints. Change only host-specific assumptions that have a safe equivalent:

- Rewrite skill-library references to the actual portable destination, including flattened synced paths. Distinguish global paths from project-relative paths. Rewrite references only when the referenced destination exists or is successfully created; leave unresolved dependencies visible.
- Express generic host actions in plain language: ask the user using the available question mechanism, read files with available tools, or use the current agent's supported delegation mechanism when delegation is authorized. Keep explicit invocation possible even if hosts use different slash-command or dollar-command syntax.
- Keep YAML frontmatter valid with a meaningful `name` and `description`. Translate host-only invocation metadata into portable prose when needed. Preserve explicit-only activation, tool restrictions, and approval conditions; do not weaken them by dropping metadata. Keep original host metadata in the source, and disclose any setting that the destination host cannot enforce.
- Preserve actual model selections, provider APIs, MCP tool requirements, browser capabilities, harness configuration such as `.claude/agents`, and project runtime paths. These are operational dependencies, not branding to replace. Do not invent substitute tools or claim a skill is executable on a host lacking them. Report remaining dependencies and say which skills need adapters.
- Inspect scripts before rewriting embedded paths. Preserve executable code and API identifiers unless a verified equivalent is available. Retain supporting references and assets; never copy runtime environments, repositories, media collections, caches, or run outputs to make a skill appear self-contained.

The canonical package is agent-neutral. For a newly created skill that should be discoverable by both Claude and Codex, create missing per-skill aliases in `~/.claude/skills/<name>` and `~/.codex/skills/<name>` to `~/.agents/skills/<name>` when supported. Never replace an existing alias or source package, and do not replace a whole skills directory. Other hosts may load the canonical `SKILL.md` explicitly. Do not change agent configuration merely to enable discovery without a request covering that change.

## CRITICAL GIT RULES

- Never commit, amend, merge, rebase, cherry-pick, or switch branches.
- Never delete, discard, revert, overwrite, clean up, or otherwise remove any existing Git change.
- Never run `git reset`, `git restore`, `git checkout`, `git clean`, `git stash`, or an equivalent destructive/discarding command.
- Never stage new changes or unstage existing changes.
- Preserve all unrelated modified, staged, and untracked files exactly as found; do not alter another person's changes.
- Leave completed changes only in the working tree.
- If files or changes unexpectedly appear, disappear, or change during work, stop and report the concurrent-worktree conflict; do not reconstruct, revert, or clean anything.

Include this complete, clearly labeled section in every coding-agent instruction prompt written or materially revised during the work, including delegated tasks. Do not add it to unrelated noncoding skills merely because they were inventoried.

## Validate and report

Validate frontmatter and required fields in new or revised entry points, referenced resource paths, executable modes, and symlink targets. Verify new contents against the intended conversion and confirm sources remain unchanged. Use the host's existing skill validator if available; do not install dependencies solely for validation. Test a helper only in an isolated temporary fixture covering a conflicting destination and a skill linked to a repository root. Do not execute the skills' substantive workflows as a validation shortcut.

Report counts of new, updated, identical, conflicting, and blocked packages; destination roots; and remaining runtime dependencies. Distinguish portable discovery from cross-host execution. Include elapsed time in minutes and seconds when the project requires it. Keep the report concise.
