#!/usr/bin/env python3
"""theme: shared HTML themes for generated pages.

  theme.py list                 themes available (default first)
  theme.py css NAME             print a theme's CSS
  theme.py apply NAME FILE...   swap the <style id="theme"> block of generated pages, then fix-chars
  theme.py fix-chars FILE...    add doctype/charset if missing and turn non-ASCII text into HTML entities
                                (outside <script>/<style>), so pages never show broken special characters
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = os.path.join(HERE, "themes")
DEFAULT = "cyberpunk"


def names():
    found = sorted(f[:-4] for f in os.listdir(THEMES) if f.endswith(".css"))
    return [DEFAULT] + [n for n in found if n != DEFAULT] if DEFAULT in found else found


def theme_css(name=None):
    name = (name or DEFAULT).strip().lower()
    path = os.path.join(THEMES, name + ".css")
    if not os.path.isfile(path):
        sys.exit(f"theme: unknown theme '{name}'. Available: {', '.join(names())}")
    with open(path, encoding="utf-8") as fh:
        css = fh.read()
    if any(ord(c) > 127 for c in css):
        sys.exit(f"theme: {path} contains non-ASCII characters; use CSS escapes like \\2013")
    return css


def ascii_safe(page):
    """Entity-encode non-ASCII outside <script>/<style>; \\u-escape it inside scripts."""
    parts = re.split(r"(?is)(<script\b.*?</script>|<style\b.*?</style>)", page)
    out = []
    for p in parts:
        if p[:7].lower() == "<script":
            out.append(re.sub(r"[^\x00-\x7f]", lambda m: _js_escape(m.group(0)), p))
        elif p[:6].lower() == "<style":
            out.append(re.sub(r"[^\x00-\x7f]", lambda m: "\\%x " % ord(m.group(0)), p))
        else:
            out.append(p.encode("ascii", "xmlcharrefreplace").decode("ascii"))
    return "".join(out)


def _js_escape(ch):
    cp = ord(ch)
    if cp < 0x10000:
        return "\\u%04x" % cp
    cp -= 0x10000
    return "\\u%04x\\u%04x" % (0xD800 + (cp >> 10), 0xDC00 + (cp & 0x3FF))


def ensure_head(page):
    if not re.search(r"(?i)<meta[^>]+charset", page):
        if re.search(r"(?i)<head[^>]*>", page):
            page = re.sub(r"(?i)(<head[^>]*>)", r'\1<meta charset="utf-8">', page, count=1)
        else:
            page = '<meta charset="utf-8">\n' + page
    if not re.match(r"(?is)\s*<!doctype", page):
        page = "<!doctype html>\n" + page
    return page


def fix_chars(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    new = ascii_safe(ensure_head(src))
    if new != src:
        with open(path, "w", encoding="ascii") as fh:
            fh.write(new)
    return new != src


def apply(name, path):
    css = theme_css(name)
    with open(path, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    block = f'<style id="theme" data-theme="{name}">{css}</style>'
    new, n = re.subn(r'(?is)<style id="theme"[^>]*>.*?</style>', lambda m: block, src, count=1)
    if not n:
        sys.exit(f"theme: {path} has no <style id=\"theme\"> block; restyle it by hand (see SKILL.md), then run fix-chars")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new)
    fix_chars(path)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "list":
        print("\n".join(f"{n}{' (default)' if n == DEFAULT else ''}" for n in names()))
    elif cmd == "css" and len(a) == 2:
        sys.stdout.write(theme_css(a[1]))
    elif cmd == "apply" and len(a) >= 3:
        for p in a[2:]:
            apply(a[1], p); print(p)
    elif cmd == "fix-chars" and len(a) >= 2:
        for p in a[1:]:
            print(("fixed " if fix_chars(p) else "already clean ") + p)
    else:
        sys.exit(__doc__)
