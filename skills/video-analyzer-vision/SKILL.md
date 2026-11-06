---
name: video-analyzer-vision
description: The full video-analyzer workflow plus the local vision model - everything video-analyzer-creative produces (transcript, scenes, frames, audio, cut list, report, exports) plus per-scene vision-model notes on captions, overlays, memes, zooms and other on-screen editing. Slowest mode (roughly 30 min to 2+ hours per 30-minute video). Accepts YouTube URLs, yt-downloader folders or video files. Use when on-screen editing devices matter, e.g. studying how a creator edits.
disable-model-invocation: true
---

## Current vision defaults (user-selected 2026-10-08)

- Normal: `qwen3.6-35b-a3b`, native Windows llama.cpp, port 8081, thinking enabled with a 512-token reasoning budget (medium-budget), 1024 total output tokens.
- High: `qwen3.8-flash-next-iq3_xxs`, native Windows Strata, port 8082, native low reasoning, 4096 total output tokens.
- Use `video-analyzer analyze INPUT --vision` for normal; add `--vision-quality high` for high. Config: `vision_quality = "normal"` or `"high"`. Vision remains opt-in.
- Start the matching server before analysis; run one model at a time. The analyzer never starts servers, downloads models, falls back to Gemma, or increases output caps automatically. WSL requests use installed Windows Python to reach Windows localhost.
- Native vision profiles allow the user-authorized hybrid CPU/GPU execution; Flash uses CPU vision encoding. WhisperX remains configured for CUDA. Legacy Ollama clients retain their GPU checks.
- Native cache identities fingerprint server metadata and the reasoning profile; they are not model weight hashes. Historical benchmark results remain unchanged. Model observations still require evidence review.


# video-analyzer-vision

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

Same as `video-analyzer-creative`, plus the vision stage. Read
`~/.agents/skills/video-analyzer-creative/SKILL.md` for inputs, options,
outputs, the cutting workflow and the exports; everything there applies,
including converting `report.md` and `frontier_brief.md` to `.html` twins with
`~/.agents/skills/human-summary/md2html.py` before pointing the user at them.

## Run

- A YouTube URL: run the `yt-downloader` skill first with default media settings and
  `--output "<topic-folder>/downloads"` as chosen above, then use the downloaded
  folder.
- Then, once per video and never in parallel (one GPU):

```bash
video-analyzer analyze "downloads/<title> [<id>]" --vision
```

- To add vision to an existing creative run instead of starting over:
  `video-analyzer analyze SAME_INPUT --resume --vision` (finished stages are
  reused; only the vision stage and report run).

Start long runs in the background and tell the user the expected time: about
20 s per scene on top of the creative run (a talking-head video has few scenes,
a fast-cut one hundreds).

## Reading the results

Vision notes are hints, not facts: the user-selected models remain screening candidates
and in testing models misidentified objects and reported motion it cannot see in still
frames. Before relying on an event in `events.json`, open its cited frame. Never
present a vision note as an observation in anything written for the user.
