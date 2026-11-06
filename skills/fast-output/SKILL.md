---
name: fast-output
description: Quick, low-effort answers for simple asks. Use only when the user types /fast-output or $fast-output or asks for "fast output". Not Claude Code's /fast mode, which is faster output at a higher price.
effort: low
disable-model-invocation: true
---

# fast-output

Quick mode: less thinking, less exploring, shorter replies. It does not change the model or the price tier.

How each host applies it:
- Claude Code: the `effort: low` frontmatter lowers reasoning effort while this skill runs. This is not `/fast`, which keeps full effort and costs more.
- Codex: a skill cannot change reasoning effort. For low effort start Codex with `codex -p fast-output` (layers `~/.codex/fast-output.config.toml`). The rules below apply either way.
- Other agents: follow the rules below.

## Rules

- Treat the request as an explicit "just do it": make reasonable assumptions instead of asking. Still confirm anything destructive, paid or hard to undo.
- No plan, no subagents, no design or review passes, no web search unless the task cannot be done without it.
- Read only the files the request names or obviously needs. No broad searches.
- Run the smallest check that proves the result (one command or one test). Don't re-check finished work.
- Reply in 1-5 lines: the answer first, then the full absolute path of any file created or changed.
- If the task turns out to be big (multi-file build, risky change), say so in one line and suggest running it without fast-output.

With no task given, apply these rules to the following requests in this session until the user says to stop.
