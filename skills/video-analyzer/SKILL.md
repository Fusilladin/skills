---
name: video-analyzer
description: Entry point for analyzing a video (a YouTube URL, a yt-downloader folder or a video file). It always asks which of three modes to run - knowledge (what the video teaches; fast), creative (editing analysis and cut list; ~10 min per 30 min of video) or vision (creative plus local vision-model notes; slowest) - and then follows that mode's skill. Use when the user says /video-analyzer or asks to analyze a video without naming a mode.
disable-model-invocation: true
---

## Current vision defaults (user-selected 2026-10-08)

- Normal: `qwen3.6-35b-a3b`, native Windows llama.cpp, port 8081, thinking enabled with a 512-token reasoning budget (medium-budget), 1024 total output tokens.
- High: `qwen3.8-flash-next-iq3_xxs`, native Windows Strata, port 8082, native low reasoning, 4096 total output tokens.
- Use `video-analyzer analyze INPUT --vision` for normal; add `--vision-quality high` for high. Config: `vision_quality = "normal"` or `"high"`. Vision remains opt-in.
- Start the matching server before analysis; run one model at a time. The analyzer never starts servers, downloads models, falls back to Gemma, or increases output caps automatically. WSL requests use installed Windows Python to reach Windows localhost.
- Native vision profiles allow the user-authorized hybrid CPU/GPU execution; Flash uses CPU vision encoding. WhisperX remains configured for CUDA. Legacy Ollama clients retain their GPU checks.
- Native cache identities fingerprint server metadata and the reasoning profile; they are not model weight hashes. Historical benchmark results remain unchanged. Model observations still require evidence review.


# video-analyzer

## Refresh the knowledge map

After finishing a download or analysis batch and writing its final reports/status,
refresh the shared folder map before the final response:

```bash
python3 ~/projects/video-analyzer/bin/update-knowledge-map.py
```

This rebuilds `~/projects/video-analyzer/knowledge-map.html` from
current folders and saved evidence, including related Jev work. Run it after a
partial or interrupted batch too, once its status is recorded. Keep partial,
failed, and unfinalized runs visible; do not label them complete just because a
report exists. This is a skill completion step, not a background watcher or an
automatic hook in the analyzer CLI. If refresh fails, retain the previous map
and report that it is stale.

## Topic folders

For a new topic without an explicit destination, use
`~/projects/video-analyzer/topics/YYYY-MM-DD-topic-slug/`.
Use the batch start date in America/Chicago and a short lowercase,
hyphen-separated topic name (for example `2026-10-05-agent-routing`).
Put downloads in that folder's `downloads/` by passing an explicit
`yt-downloader --output` path; keep analysis, notes, screenshots, and summaries
within the same dated topic folder. Reuse its path when continuing a batch;
for a distinct same-day batch with the same name, append `-2`, `-3`, etc.
A user-specified destination or an existing input folder takes precedence.
Other related work belongs in a separate project at `~/projects/related-project/`; keep its downloads
and results there, without adding a date or moving it into `topics/`.
These are skill workflow defaults; the CLI's own defaults are unchanged.

Do not run anything until the mode is chosen. If the user already named a
mode (knowledge, creative, vision, or the matching skill name), use it.
Otherwise ask using the current agent’s available question mechanism (single choice):

| Option | What it does | Time for a 30-min video |
| --- | --- | --- |
| Knowledge | Notes, executive summary and a human-summary page of what the video teaches, with key-point screenshots. No scene, frame, audio or vision stages. | ~1 min local + Claude reading the transcript |
| Creative | Word-timed transcript, scenes, frames, audio, cut list, report; exports to video-editor-agent or video-os. | ~8-10 min local |
| Vision | Creative plus per-scene local vision-model notes on on-screen editing. | ~30 min to 2+ h local |

Then read and follow exactly one skill file:

- Knowledge: `~/.agents/skills/video-analyzer-knowledge/SKILL.md`
- Creative: `~/.agents/skills/video-analyzer-creative/SKILL.md`
- Vision: `~/.agents/skills/video-analyzer-vision/SKILL.md`

## Human-readable files are HTML

The user does not read Markdown. Every file written for a person to read gets a
themed `.html` twin next to it; the `.md` stays for agents and subagents.
Convert with `python3 ~/.agents/skills/human-summary/md2html.py FILE.md...`
(writes `FILE.html`, and twins of any `.md` it links to). Any page you build or
show must link to the `.html`, never the `.md`; `--relink PAGE.html` fixes an
existing page. In final replies, give the `.html` paths.

Every mode accepts YouTube URLs and runs the `yt-downloader` skill first when
given one. The `video-analyzer` command reference (all subcommands and flags)
is in the creative skill file and in `~/projects/dev/video-analyzer/README.md`.
