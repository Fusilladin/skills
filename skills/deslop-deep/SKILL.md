---
name: deslop-deep
description: De-slop a codebase area (kill duplication, split god-files, cut comment noise) without changing behavior. Use only when the user explicitly invokes /deslop-deep.
disable-model-invocation: true
---

De-slop the target below: make it read as if a careful human wrote it, without
changing behavior.

**Target and modules:** $ARGUMENTS

If no target was given, ask which paths and which modules before touching
anything. If modules were not named, pick them yourself from what the code
actually is and say which you chose. The modules below are written for any
language; the ecosystem notes at the end are hints, not a whitelist. A language
with no note gets the same treatment under its own idioms.

## Core pass (always)

1. **Survey before editing.** List the tracked files by size, read the biggest,
   and write down the concrete duplication you found. No edits in this step.
2. **Baseline.** Find the repo's own test, build and lint commands (whatever the
   manifest, task runner or CI config uses) and run them; record the numbers. If
   either is already red, report that and stop.
3. **Kill duplication.** Logic appearing 3+ times becomes one helper at the
   right layer. Two similar blocks may stay two blocks; six identical ones may
   not. Delete a copy before inventing an abstraction.
4. **One concern per file.** When a file's name stops describing its contents,
   split it along the seams already visible inside it.
5. **Delete dead code.** Commented-out functions, disabled components, retired
   flags, unused exports. Git history is the archive; the file is not.
6. **Comments: one line, no prefixes.** Keep only what explains *why*, a
   non-obvious constraint, or a gotcha that cost someone an hour. Cut anything
   restating the code. A comment longer than its code is a smell.
7. **Doc comments state the contract:** what goes in, what comes out, how it
   fails (raises, returns an error, panics), what invariant holds. Two or three
   lines, in the language's own doc format.
8. **Verify per area,** not once at the end: tests, build, and where cheap a
   real smoke run against the running app. Type-checking alone is not
   verification.
9. **Commit per topic** as you go, following the repo's commit convention. Never
   one giant unreviewable diff.

Hard rules:
- Behavior stays identical. Spotted a real bug? Report it, do not fix it inside
  a refactor commit.
- Never touch generated files, lockfiles, vendored code, or applied migrations.
- Never restructure my own docs, checklists, plans or roadmaps (`CHECKS.md` and
  friends). Read-only.
- Preserve public shapes: HTTP payload keys, exported names, CSS class names.
  Diff them before and after if unsure.

## Module: application code (any language)

- Repeated parse-or-error blocks become one validator, decorator, guard clause
  or combinator; repeated serialization shapes become one mapping helper.
- One write path per entity, shared by every caller (HTTP handlers, CLI
  commands, background jobs, tools). Validation duplicated between them is the
  bug being fixed.
- Client plumbing (auth, retries, pagination, usage accounting, response
  unwrapping, error mapping) lives in one module, never at each call site.
- Imports and `use` declarations sit at the top of the file, not inside
  functions, unless they break a real cycle or gate a feature. Say where they do.
- Error handling is one scheme per layer: one error type or hierarchy, converted
  at the boundary, not ad-hoc strings raised from the middle of a call chain.
- Long functions split along the phases their own comments or blank lines
  already mark. A function whose name needs "and" is two functions.
- Types, structs and interfaces that carry the same field set converge on one
  definition, or get an explicit note saying why they must stay separate.
- Tests: repeated fixture, mock server and setup blocks become one builder or
  helper; keep the assertions, cut the ceremony around them.

## Module: UI components (any framework)

- Repeated fetch plus loading plus error state becomes one hook, store, resource
  or equivalent for the framework in use.
- Components past ~250 lines split into the pieces their own markup implies.
- More than ~10 props or params usually wants one grouped object of related
  handlers.
- Duplicated presentational fragments (badges, chips, toolbars, empty states)
  become shared components, one per idea.
- Pure helpers (dates, grouping, parsing, formatting) move out of the component
  file and become testable.
- Delete route-local or view-local copies of helpers that already exist app-wide.

## Module: styles (css, scss, tailwind, inline style objects)

- One palette, defined once, consumed through a map, mixin, token or custom
  property. Repeated colour literals are the target.
- Repeated visual patterns (carets, pills, icon buttons, tinted states) become
  mixins, tokens or shared classes.
- Split any file that became a dumping ground; name files after what they style.
- Prove nothing was lost: diff the selector set before and after, and grep the
  built output for a sample of generated class names.

## Module: ops (containers, shell, CI, infra config)

- Repeated blocks (healthcheck timings, shared env, job steps) become anchors,
  reusable workflows or a shared fragment.
- Multi-line shell crammed into a YAML `command` or CI `run` moves to a script
  file with `set -euo pipefail` and real error handling.
- Prove equivalence: the rendered config before and after (`docker compose
  config`, `helm template`, `terraform plan`) must match apart from keys you
  deliberately added.
- Check every long-running loop and daemon for the silent-failure case: is a
  failure noticed, and does anything actually restart it?
- Pinned versions and magic numbers keep the one-line comment saying why.

## Module: docs / markdown

- A doc that duplicates code is slop: generate it from the source, or replace it
  with a pointer. Check whether it already drifted and report by how much.
- Trim prose repeating the sample beneath it; keep the ops knowledge (why a
  value is what it is, what breaks otherwise).
- My instruction files and checklists stay untouched.

## Ecosystem notes (hints, not a whitelist)

- **Python:** decorators and context managers are the dedupe tool; `__init__.py`
  re-exports are the public shape; verify with pytest plus the real entry point,
  not mypy alone.
- **Django:** one model manager or service function per write path; fat views are
  the usual dumping ground; migrations already applied are read-only.
- **TypeScript / React:** hooks for stateful duplication, plain modules for pure
  helpers; a `type` exported from a barrel file is public shape.
- **Rust:** collapse repeated request-response plumbing into one helper on the
  client; `pub` items and trait impls are public shape; prefer `?` with one error
  enum per crate over per-call-site mapping; keep `#[cfg(test)]` modules with the
  code they test; verify with `cargo test`, `cargo clippy` and `cargo build`.
- **Go:** one constructor per client, options structs over long parameter lists;
  exported identifiers are public shape; verify with `go test ./...` and `go vet`.
- **Shell:** every script gets `set -euo pipefail`; repeated argument parsing
  becomes one function; verify with `shellcheck`.

## Styling

- No em dashes or en dashes anywhere: prose, comments, commits, UI strings. Use
  commas, colons, semicolons, parentheses or separate sentences.
- No emojis. No spaced slashes ("View/feedback", never "View / feedback").
- Comments never exceed one line, and carry no `CLAUDE:`-style prefix.
- Commits: `type(scope): summary`, lower case, no trailing full stop, 72 chars or
  less. Types: feat, fix, refactor, docs, test, chore, build, perf, ci. Scope is
  the area (backend, frontend, ops, ci), not a file name. No body unless the
  change is too large to read from the diff, and then three lines of why at most.
  No trailers, no emojis, no dashes. Split by topic, never by file.

## Report

Per area: what was duplicated and where it lives now, what was deleted, what
shrank (file, before, after), and what you verified with which command. Flag
what you chose not to touch and why. Found a real bug? Describe the failure case
and ask before changing behavior.
