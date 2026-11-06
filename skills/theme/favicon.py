#!/usr/bin/env python3
"""favicon: find a project's icon and link it from the HTML pages people open.

  favicon.py find ROOT                       print the project's icon path (relative to ROOT) or nothing
  favicon.py scan ROOT [--exclude GLOB ...]  list the pages that would get a link, plus skipped dirs and counts
  favicon.py add ROOT ICON [--exclude GLOB ...] [--dry-run]
                                             insert <link rel="icon"> into those pages (ICON relative to ROOT)

Pages that already have a rel="icon" / "shortcut icon" link are left alone. Only the one <link> line is
inserted; the bytes of the rest of the file are preserved exactly.
"""
import fnmatch, os, re, sys

# Directories that never hold pages a person opens (vendored, build output, scraped caches, test data).
SKIP_DIRS = {"node_modules", ".venv", "venv", ".git", "dist", "build", ".next", "__pycache__", "site-packages",
             "cache", ".cache", "caches", "fixtures", "captures", ".pytest_cache", ".mypy_cache", ".tox"}
# Where a project's icon may already live, in priority order (first existing wins).
ICON_CANDIDATES = ["assets/favicon.svg", "docs/assets/favicon.svg", "favicon.svg", "public/favicon.svg",
                   "static/favicon.svg", "assets/icon.svg", "assets/logo.svg", "docs/logo-mark-bw.svg",
                   "docs/logo.svg", "html/favicon.ico", "public/favicon.ico", "favicon.ico", "src/app/favicon.ico"]
ICON_LINK = re.compile(rb'<link\b[^>]*\brel\s*=\s*["\']?(?:shortcut\s+)?icon\b', re.I)


def find_icon(root):
    for c in ICON_CANDIDATES:
        if os.path.isfile(os.path.join(root, c)):
            return c
    return None


def pages(root, excludes=()):
    """Return (page paths relative to root, {skipped dir: html count})."""
    root = os.path.abspath(root)
    skipped, found = {}, []
    for d, dirs, files in os.walk(root):
        keep = []
        for x in dirs:
            rel = os.path.relpath(os.path.join(d, x), root)
            if x in SKIP_DIRS or any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g) for g in excludes):
                skipped[rel] = sum(1 for _, _, fs in os.walk(os.path.join(d, x)) for f in fs if f.lower().endswith(".html"))
            else:
                keep.append(x)
        dirs[:] = keep
        for f in files:
            if f.lower().endswith((".html", ".htm")):
                rel = os.path.relpath(os.path.join(d, f), root)
                if not any(fnmatch.fnmatch(rel, g) for g in excludes):
                    found.append(rel)
    return sorted(found), skipped


def insert_link(data, href):
    tag = f'<link rel="icon" type="{"image/svg+xml" if href.lower().endswith(".svg") else "image/x-icon"}" href="{href}">'.encode()
    m = re.search(rb"<head\b[^>]*>", data, re.I)
    if m:
        pos = m.end()
        cs = re.match(rb'\s*<meta\b[^>]*charset[^>]*>', data[pos:], re.I)
        if cs:
            pos += cs.end()
        return data[:pos] + tag + data[pos:]
    m = re.search(rb"<title\b", data, re.I)
    if m:
        return data[:m.start()] + tag + b"\n" + data[m.start():]
    m = re.match(rb"\s*<!doctype[^>]*>", data, re.I)
    if m:
        return data[:m.end()] + b"\n" + tag + data[m.end():]
    return tag + b"\n" + data


def main(a):
    if not a or a[0] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd, rest = a[0], a[1:]
    excludes = [rest[i + 1] for i, x in enumerate(rest) if x == "--exclude" and i + 1 < len(rest)]
    pos = [x for i, x in enumerate(rest) if not x.startswith("--") and (i == 0 or rest[i - 1] != "--exclude")]
    dry = "--dry-run" in rest
    if cmd == "find" and pos:
        print(find_icon(pos[0]) or "")
    elif cmd in ("scan", "add") and pos:
        root = os.path.abspath(pos[0])
        icon = pos[1] if cmd == "add" and len(pos) > 1 else None
        if cmd == "add" and not (icon and os.path.isfile(os.path.join(root, icon))):
            sys.exit(f"favicon: icon {icon!r} not found under {root}")
        n_have = n_new = 0
        found, skipped = pages(root, excludes)
        for rel in found:
            full = os.path.join(root, rel)
            with open(full, "rb") as fh:
                data = fh.read()
            if ICON_LINK.search(data[:65536]):
                n_have += 1
                continue
            n_new += 1
            if cmd == "scan" or dry:
                print("would link" if cmd == "add" else "page", rel)
            else:
                href = os.path.relpath(os.path.join(root, icon), os.path.dirname(full)).replace(os.sep, "/")
                with open(full, "wb") as fh:
                    fh.write(insert_link(data, href))
        for d, n in sorted(skipped.items()):
            if n:
                print(f"skipped dir {d} ({n} html)")
        verb = "would add" if (cmd == "scan" or dry) else "added"
        print(f"summary: {verb} {n_new} link(s); {n_have} page(s) already had an icon link")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
