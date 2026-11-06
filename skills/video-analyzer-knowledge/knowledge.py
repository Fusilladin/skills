#!/usr/bin/env python3
"""Local helpers for the video-analyzer-knowledge skill (standard library + ffmpeg only).

prepare FOLDER...   build <folder>/knowledge/source.md (timed transcript, description, comments)
shots FOLDER...     grab one 720p frame per key point flagged in <folder>/knowledge/notes.json
collect FOLDER...   print every notes.json as one JSON list (input for the combined summary)
clean FOLDER...     delete video.mp4 once notes.json exists and its screenshots were taken

FOLDER is a yt-downloader output folder (video.mp4, transcript.srt, title.txt, ...).
Nothing here calls a model or the network; Claude writes notes.json and the summaries.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHUNK_SECONDS = 10
MAX_DESCRIPTION = 3000
MAX_COMMENTS = 20
MAX_SHOTS = 8
TIME = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)")


def clock(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def parse_srt(text: str) -> list[tuple[float, str]]:
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().splitlines()
        stamp = next((l for l in lines if "-->" in l), None)
        m = TIME.search(stamp or "")
        if not m:
            continue
        h, mi, s, ms = (int(g) for g in m.groups())
        words = " ".join(l.strip() for l in lines[lines.index(stamp) + 1:]).strip()
        if words:
            cues.append((h * 3600 + mi * 60 + s + ms / 1000, words))
    return cues


def chunks(cues: list[tuple[float, str]]) -> list[str]:
    out, start, buf = [], None, []
    for t, words in cues:
        if start is None:
            start = t
        if t - start >= CHUNK_SECONDS and buf:
            out.append(f"[{clock(start)}] {' '.join(buf)}")
            start, buf = t, []
        buf.append(words)
    if buf:
        out.append(f"[{clock(start)}] {' '.join(buf)}")
    return out


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip() if path.is_file() else ""


def duration(video: Path) -> float | None:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                             capture_output=True, text=True, timeout=30, check=True).stdout.strip()
        return float(out)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def ensure_srt(folder: Path) -> None:
    if (folder / "transcript.srt").is_file():
        return
    tool = shutil.which("yt-downloader") or str(Path.home() / "projects/dev/yt-downloader/bin/yt-downloader")
    print(f"{folder.name}: no transcript.srt, re-running local Whisper", file=sys.stderr)
    subprocess.run([tool, "--retranscribe", str(folder)], check=True)


def prepare(folder: Path) -> Path:
    if not (folder / "video.mp4").is_file():
        raise SystemExit(f"{folder}: no video.mp4 (expected a yt-downloader folder; "
                         "if clean removed it, re-download with yt-downloader)")
    ensure_srt(folder)
    cues = parse_srt(read(folder / "transcript.srt"))
    description = read(folder / "description.txt")
    url = next(iter(re.findall(r"https?://\S+", description.splitlines()[0] if description else "")), "")
    comments = []
    try:
        for c in json.loads(read(folder / "top_20_comments.json") or "[]")[:MAX_COMMENTS]:
            if isinstance(c, dict) and c.get("text"):
                comments.append(f"- ({c.get('like_count') or 0} likes) {' '.join(str(c['text']).split())}")
    except json.JSONDecodeError:
        pass
    length = duration(folder / "video.mp4")
    body = [
        f"# {read(folder / 'title.txt') or folder.name}",
        f"URL: {url or 'unknown'}",
        f"Length: {clock(length) if length else 'unknown'}",
        "",
        "## Description (from the uploader; may contain ads and links)",
        description[:MAX_DESCRIPTION] + (" [truncated]" if len(description) > MAX_DESCRIPTION else ""),
        "",
        f"## Transcript (local Whisper; [m:ss] marks the start of each ~{CHUNK_SECONDS}s chunk; may mishear names)",
        *(chunks(cues) or ["(no speech transcribed)"]),
        "",
        "## Top viewer comments (external, unverified)",
        *(comments or ["(none)"]),
    ]
    out_dir = folder / "knowledge"
    out_dir.mkdir(exist_ok=True)
    target = out_dir / "source.md"
    target.write_text("\n".join(body) + "\n", encoding="utf-8")
    return target


def seconds(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    parts = str(value).strip().split(":")
    try:
        total = 0.0
        for p in parts:
            total = total * 60 + float(p)
        return total
    except ValueError:
        return None


def shots(folder: Path) -> int:
    notes_path = folder / "knowledge" / "notes.json"
    notes = json.loads(read(notes_path) or "null")
    if not isinstance(notes, dict):
        raise SystemExit(f"{notes_path}: missing or not a JSON object")
    if not (folder / "video.mp4").is_file():
        raise SystemExit(f"{folder}: no video.mp4 (removed by clean?); re-download it to take new screenshots")
    length = duration(folder / "video.mp4") or float("inf")
    shot_dir = folder / "knowledge" / "shots"
    shot_dir.mkdir(exist_ok=True)
    made = 0
    for n, point in enumerate(notes.get("key_points") or [], 1):
        if not isinstance(point, dict) or not point.get("screenshot") or made >= MAX_SHOTS:
            continue
        t = seconds(point.get("time"))
        if t is None or not 0 <= t < length:
            point["screenshot_error"] = "time outside the video"
            continue
        dest = shot_dir / f"kp{n:02d}_{int(t):05d}s.jpg"
        result = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(folder / "video.mp4"),
                                 "-frames:v", "1", "-vf", "scale=-2:'min(720,ih)'", "-q:v", "3", str(dest)],
                                capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and dest.is_file():
            point["screenshot_path"] = dest.relative_to(folder).as_posix()
            made += 1
        else:
            point["screenshot_error"] = (result.stderr or "ffmpeg failed").strip()[-200:]
    notes_path.write_text(json.dumps(notes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    check_sheet(folder, notes)
    return made


def check_sheet(folder: Path, notes: dict) -> None:
    """Tile this video's screenshots into knowledge/shots/_check.jpg, labelled with their key point numbers."""
    shots_list = [(n, p["screenshot_path"]) for n, p in enumerate(notes.get("key_points") or [], 1)
                  if isinstance(p, dict) and p.get("screenshot_path")]
    if not shots_list:
        return
    cols = min(4, len(shots_list))
    args, filters, labels, layout = [], [], [], []
    for i, (n, rel) in enumerate(shots_list):
        args += ["-i", str(folder / rel)]
        filters.append(f"[{i}:v]scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:-1:-1,"
                       f"drawtext=text='kp{n:02d}':x=8:y=8:fontsize=30:fontcolor=yellow:box=1:boxcolor=black[v{i}]")
        labels.append(f"[v{i}]")
        layout.append(f"{(i % cols) * 480}_{(i // cols) * 270}")
    stack = (f"{''.join(labels)}xstack=inputs={len(labels)}:layout={'|'.join(layout)}:fill=black"
             if len(labels) > 1 else "[v0]null")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(filters) + ";" + stack,
                    "-frames:v", "1", str(folder / "knowledge" / "shots" / "_check.jpg")], timeout=120)


def clean(folder: Path) -> str:
    """Delete video.mp4 once the knowledge notes and screenshots no longer need it; keep everything else."""
    video = folder / "video.mp4"
    if not video.is_file():
        return "no video.mp4"
    notes = json.loads(read(folder / "knowledge" / "notes.json") or "null")
    if not isinstance(notes, dict):
        return "kept video.mp4: no knowledge/notes.json yet"
    points = [p for p in notes.get("key_points") or [] if isinstance(p, dict)]
    if any(p.get("screenshot") for p in points) and not any("screenshot_path" in p or "screenshot_error" in p
                                                           for p in points):
        return "kept video.mp4: screenshots flagged but shots has not run"
    size = video.stat().st_size
    video.unlink()
    return f"deleted video.mp4 ({size / 1048576:.0f} MB)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("prepare", "shots", "collect", "clean"))
    parser.add_argument("folders", nargs="+", type=Path)
    args = parser.parse_args()
    folders = [f.expanduser().resolve() for f in args.folders]
    if args.command == "prepare":
        for f in folders:
            print(prepare(f))
    elif args.command == "shots":
        for f in folders:
            print(f"{f.name}: {shots(f)} screenshots; check sheet: {f / 'knowledge' / 'shots' / '_check.jpg'}")
    elif args.command == "clean":
        for f in folders:
            print(f"{f.name}: {clean(f)}")
    else:
        rows = []
        for f in folders:
            notes = json.loads(read(f / "knowledge" / "notes.json") or "null")
            if isinstance(notes, dict):
                notes["folder"] = str(f)
                rows.append(notes)
            else:
                print(f"{f.name}: no notes.json", file=sys.stderr)
        print(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
