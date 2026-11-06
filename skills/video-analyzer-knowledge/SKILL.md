---
name: video-analyzer-knowledge
description: Learn from videos fast - turn one or more YouTube URLs or yt-downloader folders into per-video notes (synopsis, timestamped key points, tools/links, claims to check, useful comments), one combined executive summary, and a /human-summary HTML page with key-point screenshots. Skips scene detection, frame sampling, audio and the vision model. Use for tutorials, talks, explainers and "N use cases" videos when the goal is what was said or taught, not how the video is edited.
disable-model-invocation: true
---

# video-analyzer-knowledge

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

## Human-readable files are HTML

The user does not read Markdown. Every file written for a person to read gets a
themed `.html` twin next to it; the `.md` stays for agents and subagents.
Convert with `python3 ~/.agents/skills/human-summary/md2html.py FILE.md...`
(writes `FILE.html`, and twins of any `.md` it links to). Any page you build or
show must link to the `.html`, never the `.md`; `--relink PAGE.html` fixes an
existing page. In final replies, give the `.html` paths.

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

Goal: extract what a video teaches, cheaply. All media work is local and quick
(a timed transcript that yt-downloader already made, plus a few ffmpeg frame
grabs). Claude does the reading and writing.

Helper: `python3 ~/.agents/skills/video-analyzer-knowledge/knowledge.py`
(`prepare`, `shots`, `collect`, `clean`; each takes one or more download folders).

## 1. Get the inputs

- A YouTube URL (or several): run the `yt-downloader` skill first with default
  media settings and `--output "<topic-folder>/downloads"` as chosen above
  (`yt-downloader --videos "URL" ... --output "<topic-folder>/downloads"`).
  Then use those downloaded folders.
- A yt-downloader folder: use it as is. A folder of such folders (e.g.
  `downloads/`): use every subfolder that contains `video.mp4`. Folders whose
  video was already deleted by step 7 still have `knowledge/notes.json`, so they
  work for `collect` and a new summary; re-download them to redo `prepare` or `shots`.
- A loose video file (not in a yt-downloader folder): this mode needs the
  folder layout; say so and offer `/video-analyzer-creative` instead.

## 2. Prepare (local, seconds)

```bash
python3 ~/.agents/skills/video-analyzer-knowledge/knowledge.py prepare FOLDER...
```

Writes `FOLDER/knowledge/source.md`: title, URL, length, description, the
transcript in ~10 s chunks with `[m:ss]` starts, and top comments. If a folder
has no `transcript.srt` (older downloads), it runs `yt-downloader --retranscribe`
on the GPU first (about 20 s per 5 minutes of video).

## 3. Notes per video (Claude)

For one video, do it inline. For two or more, launch one subagent per video,
all in a single message so they run in parallel, each with this brief and
nothing else. Do not set a model; subagents use whatever the session or the
user's settings choose, so the skill works with any model.

> Read `<FOLDER>/knowledge/source.md` only. Write `<FOLDER>/knowledge/notes.json`
> and `<FOLDER>/knowledge/notes.md` (a readable rendering of the same content),
> then run `python3 ~/.agents/skills/human-summary/md2html.py <FOLDER>/knowledge/notes.md`
> (writes `notes.html`), then reply "done". Be terse; do not explore other files.

`notes.json` shape (all fields required; use empty lists when nothing applies):

```json
{"title": "...", "url": "...", "length": "12:34",
 "synopsis": "3-5 sentences: what the video covers and its main takeaway.",
 "key_points": [{"time": "4:10", "point": "One-line takeaway", "detail": "1-3 sentences, specific (commands, numbers, steps).", "screenshot": true}],
 "tools_and_links": [{"name": "...", "what": "what it is / how it was used", "url": "from the description, or null"}],
 "how_to_steps": ["Ordered steps if the video teaches a procedure"],
 "claims_to_check": ["Factual or performance claims stated without evidence"],
 "useful_comments": ["Comments that add corrections, tips or caveats (paraphrased)"],
 "skip": "What is filler, promotion or repetition (one line)",
 "quality": "high | medium | low - one line on how useful this video is"}
```

Rules for the notes: only what the video or its description says; mark opinions
as opinions; keep transcript mishearings out (fix obvious ones from context, or
say "unclear"); `time` is the `[m:ss]` marker of the chunk where the point is shown or said (not where the topic is first announced), so screenshots land on it. Set
`screenshot: true` on at most 8 points where the screen likely shows something
useful (a UI, code, a diagram, a result), not for talking heads.

## 4. Screenshots (local, seconds)

```bash
python3 ~/.agents/skills/video-analyzer-knowledge/knowledge.py shots FOLDER...
```

Grabs one 720p frame per flagged key point into `FOLDER/knowledge/shots/` and
writes `screenshot_path` back into `notes.json`. It also writes
`knowledge/shots/_check.jpg`, all of the video's screenshots tiled and labelled
`kpNN` (the key point number). Read that one image per video and keep a
screenshot only if it actually shows what its point describes. Screens often
lag speech by 10-30 s, so a shot may show the previous point's demo: reassign it
to the point it does show, or drop it; drop faces, blank screens, sponsor segments and
mismatches. Screenshots are cheap to view; a wrong one is worse than none.

## 5. Combined executive summary (Claude)

Run `knowledge.py collect FOLDER...` and read its JSON (all notes in one list).
Then write, for the whole set (one video or many):

- Output folder: the video folder's `knowledge/` for one video; for several,
  `<their common parent>/knowledge-summary/`.
- `knowledge_report.md`: executive summary first (5-10 bullets of what was
  learned), then the merged material grouped by topic, not by video:
  techniques and how-tos, tools and links, claims to verify, open questions.
  De-duplicate repeated points (keep the clearest version and cite every video
  that made it), and drop weak, promotional, vague or contradicted items.
  Cite sources as `Title @ m:ss`.
- Then `python3 ~/.agents/skills/human-summary/md2html.py <output folder>/knowledge_report.md`
  (writes `knowledge_report.html`; also re-converts any `notes.md` it links to).

## 6. Human summary page

Build the content JSON for `~/.agents/skills/human-summary/render.py` (see the
human-summary skill) and render it into the same output folder:

```bash
python3 ~/.agents/skills/human-summary/render.py render CONTENT.json \
  -o <output folder>/human-summary.html --root <output folder>
```

Write CONTENT.json to a temp location. Content: `summary` = the executive
summary; `sections` = one per topic (`items` with `title`, `text`, `source`
"Title @ m:ss", and `image` `{path, caption}` for the best screenshots, paths
relative to `--root`); `artifacts` = `knowledge_report.md` and each video's
`notes.md` (render.py links their `.html` twins, never the `.md`); `needs_human` = only real decisions for the user (e.g. claims worth
checking before acting, conflicting advice between videos), else empty.
`--root` must be a folder that contains the screenshots (use the common parent
for several videos and set `-o` to the output folder inside it).

## 7. Delete the videos

Once `human-summary.html` is rendered, free the disk space:

```bash
python3 ~/.agents/skills/video-analyzer-knowledge/knowledge.py clean FOLDER...
```

It deletes each folder's `video.mp4` only if `knowledge/notes.json` exists and
`shots` has run for any flagged screenshots; transcripts, description,
comments, thumbnail, notes and screenshots stay. Skip this step only if the user
asked to keep the videos or wants creative/vision analysis of them next (those
modes need the video).

Finish by printing the paths of `knowledge_report.html` and `human-summary.html` (no `.md` paths),
the executive summary bullets, and one line on how much video was deleted.

## Cost and time

Local steps take seconds per video (plus ~20 s per 5 minutes for any missing
`transcript.srt`). Claude cost is mostly reading `source.md`: roughly 2k tokens
per 5 minutes of speech per video, plus the combined summary.
