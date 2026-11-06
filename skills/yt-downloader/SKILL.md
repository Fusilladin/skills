---
name: yt-downloader
description: Download YouTube videos, Shorts, or whole playlists as MP4 together with a local Whisper transcript, title, description, thumbnail, and top comments. Use whenever the user asks to download, save, grab, or archive a YouTube video or playlist, or when a task needs a local copy of a video or its transcript/metadata.
disable-model-invocation: true
---

# yt-downloader

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

Run the `yt-downloader` command (on PATH; works from any directory). It manages
its own virtualenv, so do not `pip install` anything or call the Python script
directly. If the command is not found, use
`~/projects/dev/yt-downloader/bin/yt-downloader`.

## Usage

```bash
yt-downloader "URL"                                 # one video, 1080p target
yt-downloader --videos URL_1 URL_2 URL_3            # several videos, concurrently
yt-downloader --videos-file urls.txt                # one URL per line
yt-downloader "PLAYLIST_URL"                        # playlist -> one subfolder per video
yt-downloader "URL" --list-formats                  # show available formats, download nothing
```

Always quote URLs (they contain `&` and `?`).

| Option | Default | Meaning |
| --- | --- | --- |
| `--output DIR` | `./downloads` | Root folder; relative to the current working directory |
| `--resolution N\|best` | `1080` | Target height; 1080 falls back to 720, 480, 360, 144, then best MP4 |
| `--workers N` | `3` | Concurrent downloads (also applies to playlist items) |
| `--log-file PATH` | none | Also write the timestamped log to a file |
| `--whisper-model NAME\|PATH` | `ggml-large-v3-turbo` | whisper.cpp model in `~/.local/share/whisper/models`, or a path to a `.bin` |
| `--no-whisper` | off | Skip Whisper; save YouTube's own captions as the transcript instead |
| `--retranscribe FOLDER...` | none | Re-run Whisper on existing download folders (adds `transcript.srt`); downloads nothing |

## Output

The CLI uses `./downloads` unless `--output` is given. For this skill, pass
`--output "<topic-folder>/downloads"` using the destination selected above.

```text
<output>/<video title> [<video id>]/
    video.mp4               # original streams merged, no re-encoding
    transcript.txt          # local Whisper (whisper.cpp, ggml-large-v3-turbo, language auto-detected)
    transcript.srt          # same transcript with timestamps (from YouTube captions with --no-whisper)
    title.txt
    description.txt         # first line is the video URL
    thumbnail.<ext>
    thumbnail_url.txt
    top_20_comments.json
<output>/<playlist title> [<playlist id>]/<video title> [<video id>]/...
```

## Notes

- Downloads can take minutes and files are large; for playlists or many URLs,
  run the command in the background and pass `--log-file`.
- Exit code is 1 if any URL failed; the rest of the batch still completes. Check
  the log for `Failed:` lines and re-run only those URLs.
- Comments are capped at the top 20 top-level comments (no replies), so
  metadata extraction is quick even on very popular videos.
- Requires `ffmpeg` on PATH (already installed on this machine).
- Transcripts are produced locally by whisper.cpp from `~/.local/share/whisper`
  (override with `WHISPER_HOME`). The CUDA build is used first, the CPU build if
  it fails. Transcriptions run one at a time even with several workers.
- Whisper can invent a line of text for videos with no speech (music, timers);
  treat a one-line transcript on such videos as empty.
- There is no transcript-only mode: every run downloads the video file.

## Next step: analyze the video

yt-downloader's `transcript.txt` has no timestamps (`transcript.srt` does). To
go further, pass the downloaded folder (not the mp4) to one of:

- `video-analyzer-knowledge`: notes and an executive summary of what was taught (fast).
- `video-analyzer-creative`: transcript, scenes, audio and a cut list for editing.
- `video-analyzer-vision`: creative plus local vision-model notes (slow).

`/video-analyzer` asks which one. Each of them also accepts a URL and calls
yt-downloader itself.
