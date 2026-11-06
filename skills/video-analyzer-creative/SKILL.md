---
name: video-analyzer-creative
description: Editing-oriented video analysis without the vision model - word-timed WhisperX transcript and SRT, scene cuts, frames and contact sheets, audio silence/onset measurements, a cut list (cut_candidates.json), a report, and exports to video-editor-agent or video-os. Accepts YouTube URLs (downloads them with yt-downloader first), yt-downloader folders or video files. Use to tighten a video, find pauses and cut points, cut it into pieces, or study its editing rhythm.
disable-model-invocation: true
---

## Current vision defaults (user-selected 2026-10-08)

- Normal: `qwen3.6-35b-a3b`, native Windows llama.cpp, port 8081, thinking enabled with a 512-token reasoning budget (medium-budget), 1024 total output tokens.
- High: `qwen3.8-flash-next-iq3_xxs`, native Windows Strata, port 8082, native low reasoning, 4096 total output tokens.
- Use `video-analyzer analyze INPUT --vision` for normal; add `--vision-quality high` for high. Config: `vision_quality = "normal"` or `"high"`. Vision remains opt-in.
- Start the matching server before analysis; run one model at a time. The analyzer never starts servers, downloads models, falls back to Gemma, or increases output caps automatically. WSL requests use installed Windows Python to reach Windows localhost.
- Native vision profiles allow the user-authorized hybrid CPU/GPU execution; Flash uses CPU vision encoding. WhisperX remains configured for CUDA. Legacy Ollama clients retain their GPU checks.
- Native cache identities fingerprint server metadata and the reasoning profile; they are not model weight hashes. Historical benchmark results remain unchanged. Model observations still require evidence review.


# video-analyzer-creative

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

The everyday editing workflow: English word-timed transcript, scene cuts,
frames and contact sheets, audio measurements, a cut list and a report. No
vision model. About 8-10 minutes for a 30-minute 1080p video, all local.

## Input

- A YouTube URL (or several): run the `yt-downloader` skill first with its
  default media settings and `--output "<topic-folder>/downloads"` as
  chosen above, then analyze each downloaded folder.
- A yt-downloader folder or a local video file: analyze it directly.

Then run, once per video (the GPU stages are serial, so do not run videos in
parallel):

```bash
video-analyzer analyze "downloads/<title> [<id>]"
```

For a non-English video add `--language CODE`. Do not add `--vision`; that is
the `video-analyzer-vision` skill.

## Reference

Run the `video-analyzer` command (on PATH; works from any directory). It uses
its own virtualenv and never installs, downloads, uploads, or modifies the
input video. If the command is not found, use
`~/projects/dev/video-analyzer/bin/video-analyzer`.

## Usage

```bash
video-analyzer doctor                                   # check tools, models, GPU (read-only)
video-analyzer analyze VIDEO                            # English transcript, scenes, frames, audio, cut list
video-analyzer analyze "downloads/<title> [<id>]"       # a yt-downloader folder (most common)
video-analyzer analyze VIDEO --vision                   # also local vision-model notes (slow)
video-analyzer benchmark CLIPS_DIR --models MODEL_A,MODEL_B             # local model comparison
video-analyzer export-edit-request RUN_DIR              # cut list -> edit_request.json for video-editor-agent
video-analyzer export-video-os RUN_DIR                  # cut list -> a video-os project folder
video-analyzer export-brief RUN_DIR                     # compact brief for a frontier model
video-analyzer export-motion-review RUN_DIR              # short source clips for human motion review
```

`VIDEO` is a video file or a yt-downloader output folder (it then analyzes
`video.mp4`, records title/URL/comments as provenance, and writes to
`<folder>/analysis`). For a plain file the output root is `./analysis`.
The run directory is `<output root>/<filename>-<hash>/`; the command prints it.

| Option | Meaning |
| --- | --- |
| `--vision` | Also run the local vision model (off by default; about 20 s per scene, and its notes are hints only). `--fast` is still accepted and means the default. |
| `--language CODE` | Transcription language; defaults to `en`. Pass it for non-English videos (a missing alignment model is reported, never downloaded). |
| `--start T` / `--end T` | Analyze a range (seconds or `[HH:]MM:SS`). Reported times stay on the source file's clock. |
| `--transcript FILE` | Reuse an existing WhisperX JSON instead of transcribing. |
| `--skip-transcript`, `--skip-audio` | Skip those stages. |
| `--resume` | Continue or extend an existing run, reusing finished stages (e.g. `--resume --vision` adds the vision stage to an earlier run). |
| `--force` | Redo the run from scratch. Keeps `human_notes.json` and `cut_decisions.json`. |
| `--output DIR` | Output root. |
| `--model TAG` | Explicit local vision model override; normal defaults to Qwen3.6 medium-budget. |
| `--sample-fps F`, `--max-frames-per-scene N` | Denser frame sampling. |

## Comparing local vision models

```bash
video-analyzer benchmark CLIPS_DIR \
  [--models MODEL_A,MODEL_B] [--output DIR] [--sample-fps FPS] [--force]
```

The benchmark command is implemented. Use only Ollama models already installed
on the machine. Transcription and model inference are GPU-only; if CUDA or full
GPU model allocation is unavailable, report the blocker and do not retry on
CPU. The command does not install or pull models and does not call an external
API. It extracts each clip's evidence once, then gives the identical evidence
and prompt to each requested model. Reports remain separate by model and record
runtime, errors, and structured-output validity. Use the accompanying human
scorecard to judge factual accuracy, missed or invented events, timing,
specificity, and editing usefulness. The benchmark does not select a default
winner automatically. No real candidate comparison has been completed, so
there is no benchmark winner or selected default model. Running it is a
separate, explicit command; ordinary analysis does not start benchmark jobs.
Larger models can be slower or fail the full-GPU residency check if they exceed
available VRAM. The benchmark never downloads a smaller substitute.

## Reviewing motion around candidate moments

```bash
video-analyzer export-motion-review RUN_DIR \
  [--output DIR] [--duration SECONDS] \
  [--focus TIMECODE ...] [--graphics-model MODEL]
```

`--duration` accepts 0.5 through 1.0 seconds and defaults to 1.0. Run this extra
export manually when still frames may have missed motion graphics. It writes
short previews using timestamps on the original source clock and retains
original audio when present. Encoding uses GPU `h264_nvenc`; there is no
software-encoding fallback.

Automatic coverage includes the analyzed-range start, detected scene cuts, and
scene midpoints, up to 24 previews. This is sampling, not graphics detection;
it can miss a brief event between sample points. Repeat `--focus TIMECODE` to
prioritize user-selected source times. Each focus time requests a 0.5–1.0
second preview centered on that time. To review a longer animation, supply
multiple overlapping focus times.

`--graphics-model MODEL` is optional and uses an already-installed local Ollama
vision model to review five still frames sampled from each preview. The model
receives one labelled 3×2 contact image of those frames, not the preview video;
it compares still images rather than analyzing continuous video. The contact
image fits the configured 4096-token context; sending the five frames
separately exceeded that limit. No context or model settings were changed. The
individual evidence JPEGs remain in `graphics_frames/`, with frame indices and
source-clock times recorded in the review data. The command does not download a
model or call an external API. Before inference, Ollama verifies the model is
fully GPU-resident and rejects CPU or partial CPU allocation; never fall back
to CPU. The versioned prompt is
`src/video_analyzer/prompts/graphics_review.txt`. Results go to
`graphics_review.json` with one status per preview:

- `animated_graphic`: an editor-added graphic visibly changes across sampled
  frames;
- `graphic_static`: an editor-added graphic is visible and appears unchanged;
- `no_graphic_evidence`: the sampled frames do not show evidence of a graphic;
- `uncertain`: the samples are ambiguous or insufficient.

Each observation also records the focused element and graphic kind. The origin
is derived in code from the kind, not supplied by the model: title, caption, logo
and overlay map to `screen_graphic`, `scene_text` to `scene_content`, `native_ui`
to `native_ui`, and `none` to `none`. Asking for both was the single most common
model failure, and the pairing is a fixed lookup. The schema still rejects an
animated or static claim for a scene sign or a game interface, and still rejects
a static claim that is not fully visible in all five frames.
`no_graphic_evidence` does not establish absence from the full preview or
source, and a model result is not human acceptance. Sampled frames are kept in
`graphics_frames/`; raw model responses and errors are kept in
`graphics_model/`. In the latest GPU trial, the model returned schema-valid
output in 32.014 seconds, but labeled an opening animation as static with 0.95
confidence. It correctly classified a static logo and marked a street scene
uncertain while missing a credit. Valid structure and confidence do not
establish accuracy: treat these optional observations as untrusted pending the
model benchmark. These outputs are evidence for human review; they do not
isolate graphics or make editing decisions. The export remains opt-in, does not
invoke an editor, and is not part of normal analysis.

Re-running on an existing run directory without `--resume` or `--force` is
refused (exit 2). Exit 1 means a stage failed; the other artifacts and the
report are still written. Exit 0 means every stage completed or was skipped.
Resume checks artifact contents as well as settings. Evidence reruns remove
default brief and editor-request exports; export them again after the run.

## After yt-downloader

yt-downloader saves `<output>/<title> [<id>]/video.mp4` (default output
`./downloads`). Pass that folder, not the mp4, so the title, URL and comments
are recorded: `video-analyzer analyze "downloads/<title> [<id>]"`. The run is
written to `<that folder>/analysis/<name>-<hash>/`. For several downloads, run
them one at a time (the GPU stages are serial anyway).

## Output

```text
<run dir>/
    analysis.json           # index: stage statuses + paths of every artifact (read this first)
    transcript.json / .srt  # segments with word-level start/end (source-file clock)
    cut_candidates.json     # contiguous keep/drop segments from measured pauses, with the kept text
    scenes.json             # detected cuts (long shots are subdivided; subdivisions are not edits)
    frames.json, frames/, contact_sheets/   # labelled evidence frames
    audio_features.json     # loudness series, silence and onset candidates
    events.json, model/     # vision-model observations (only with --vision)
    report.md               # summary with evidence links (agents read this)
    report.html             # themed twin for the human (make it with md2html.py, below)
    manifest.json           # source identity, settings, versions, stage signatures
```

After every run, give the human HTML, not Markdown:
`python3 ~/.agents/skills/human-summary/md2html.py "<run dir>/report.md"` (and
`frontier_brief.md` after `export-brief`). Point the user at the `.html` files.

## Timing

Roughly: transcription takes about as long as 40-75% of the audio duration on
the local GPU; scenes and frames about 30 s per minute of 1080p video. The
vision stage is about 20 s per scene (several minutes per minute of fast-cut
video), so run long jobs in the background.

## Cutting a video into tighter pieces

1. `video-analyzer analyze VIDEO` (or the yt-downloader folder).
2. Read `cut_candidates.json` (measured pauses, the text of each kept span,
   listed filler words) and `transcript.json` for word-level times.
3. Decide what to keep. The candidates are measurements only; choosing the
   entertaining parts is an editorial judgement for you and the user. Snap
   your cut points to word boundaries from the transcript. Keep all three
   human-reviewed pause candidates. Lack of speech by itself does not make a
   pause dead time or a reason to cut it.
4. Write `cut_decisions.json` in the run directory, same shape as the
   candidates but with only your choices:

   ```json
   {"schema_version": "1.0", "source_id": "<from cut_candidates>",
    "source_path": "<from cut_candidates>", "basis": "editorial",
    "segments": [{"id": "keep_01", "start": 18.76, "end": 31.2,
                  "action": "keep", "reason": "strong opening line"}]}
   ```

   Segments must be in time order and must not overlap. To reorder clips (for
   example to move a hook to the front), edit `timeline_order` in the exported
   request afterwards. Segments must stay within the manifest's analyzed range,
   and any supplied source path must match the manifest.
5. `video-analyzer export-edit-request RUN_DIR` writes `RUN_DIR/edit_request.json`
   (it prefers `cut_decisions.json`, else the candidates). It never writes into
   the editor project unless `--output` points there.
6. In `~/projects/dev/video-editing/video-editor-agent`: copy the request to
   `config/edit_request.json` (ask first; it overwrites the user's current
   request), then `npm run probe -- /abs/path/to/video.mp4` (probe only reads
   `raw/` by default), `npm run plan`, `npm run preview`.

### Reviewing in video-os instead

`video-analyzer export-video-os RUN_DIR [--id ID] [--cuts FILE] [--output DIR]`
writes `RUN_DIR/video-os/<id>/` with `project.json`, `cut_proposal.json` and
`silence.json`. Source and transcript paths are absolute, so the folder can be
copied or symlinked into `~/projects/dev/video-os/projects/<id>/` as is (ask the
user first; this tool never writes into video-os itself). Then run `npm start`
in video-os and open `/app/?project=<id>`.

Each cut is a span not covered by a keep segment (from `cut_decisions.json` if
present, else `cut_candidates.json`). `risk_level` is `low` only when no
transcribed word falls inside the cut; cuts that remove speech are `medium`
with `needs_bridge: true` and the removed words in `transcript_excerpt`.

## Notes

- WhisperX transcription and Ollama model inference are GPU-only. Never fall
  back to CPU. The benchmark verifies full GPU model allocation; if execution
  restrictions hide the GPU, preserve completed evidence and use a GPU-enabled
  context. The real 45-second transcription test passed there on CUDA/float16.

- Vision-model events are hints, not facts. In testing `gemma3:4b` produced
  valid structure but misidentified objects and reported "holds" and "freezes"
  it cannot see from still frames. Check any event against its cited frame
  before relying on it, and never present its guesses as observations.
- Silence and onset events are loudness measurements, not identified sounds.
- `export-brief` makes no network call; it only writes `frontier_brief.md`
  and lists which local files a human would need to attach. Convert it with
  `md2html.py` before showing it to the user.
- Project rules and architecture: `AGENTS.md`, `README.md` in this folder.


### Approved Review 2 screening follow-up (2026-10-02)

The opening-preview coverage is human accepted. Five clip ranges are approved
as provisional screening candidates; their category ground truth is incomplete.
The three installed candidates plus Qwen3-VL 8B Q4_K_M, Gemma 4 E2B Q4_K_M,
MiniCPM-V 4.6 1B, and Ornith 1.5 9B are authorized for local trials. Those four
additional models have been downloaded explicitly for this pilot. The analyzer
itself still never downloads models or software.

The focused classifier now records the same target's visibility across all
five samples (`absent`, `partial`, `full`, or `unknown`). An entrance cannot be
validated as static. A visible graphic cannot simultaneously have kind `none`.
Screen-space placement uses `screen_graphic`; this is not authorship evidence.
Legacy `editor_added` labels remain unverified suggestions. Requests are bounded
to 1,024 generated tokens with thinking disabled and temperature zero; the
generation policy participates in resume signatures. Context is not overridden.

Three-window model trials are triage, not the five-clip acceptance benchmark.
Inspect Review 3 and the ignored local screening JSON for actual results and
GPU residency checks. Failed full-GPU loading never falls back to CPU. Human
category notes and scoring remain necessary before model selection; no new
default model is selected automatically.
