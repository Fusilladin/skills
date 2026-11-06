#!/usr/bin/env python3
"""md2html: render Markdown files as themed HTML twins (notes.md -> notes.html); no dependencies.

The .md stays for agents; humans open the .html. Relative links to other .md files
are converted too and point at their .html twins.

  md2html.py FILE.md...          write each FILE.html next to its source
  md2html.py --relink PAGE.html  convert every .md a page links to and point the links at the .html
"""
import html, os, re, sys, time
from urllib.parse import quote, unquote

CSS = """:root{color-scheme:dark;--bg:#07080d;--panel:#0e1018;--panel2:#161927;--line:#30344b;--text:#e6f1ea;--muted:#9299ad;--green:#39ff8b;--purple:#bd70ff;--red:#ff596b;--amber:#ffc857}
*{box-sizing:border-box}
body{margin:0;color:var(--text);background:radial-gradient(ellipse at 85% 0%,#251039 0,transparent 36rem),radial-gradient(ellipse at 5% 12%,#09271e 0,transparent 32rem),var(--bg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
header{position:sticky;top:0;z-index:5;background:rgba(7,8,13,.96);border-bottom:1px solid var(--purple);box-shadow:0 0 18px #bd70ff25;padding:10px 16px}
.bar,nav,main{width:min(1240px,100%);margin-inline:auto}
.bar{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
h1{flex:1;margin:0;color:var(--green);font-size:17px;letter-spacing:.08em;text-transform:uppercase;text-shadow:0 0 12px #39ff8b55}
.stamp{color:var(--muted);font-size:13px}
nav{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}
nav a{color:var(--text);text-decoration:none;padding:3px 11px;border:1px solid var(--line);border-radius:99px;background:var(--panel2);font-size:13px}
nav a:hover{color:var(--green);border-color:var(--green)}
main{padding:20px 16px 50px}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:0 0 26px}
.strip div,.card{background:linear-gradient(145deg,#11131d,#0b0d14);border:1px solid var(--line);border-radius:9px;padding:14px}
.strip div{border-top:2px solid var(--purple)}
.strip strong,.strip span.l{display:block}
.strip strong{color:var(--green);font-size:16px}
.l,.muted{color:var(--muted);font-size:13px}
section{margin:30px 0}
h2{color:var(--purple);font-size:20px;margin:0 0 8px}
h3{margin:0 0 7px;font-size:16px;color:#ff9aa4}
.status{display:inline-block;padding:2px 8px;border-radius:99px;border:1px solid var(--red);color:var(--red);font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.status.ok{border-color:var(--green);color:var(--green)}
.status.info{border-color:var(--amber);color:var(--amber)}
.card.pending{border-color:#6b2631;border-left:3px solid var(--red)}
.card p{margin:4px 0}
a{color:var(--green)}
.links{display:flex;flex-wrap:wrap;gap:10px;margin-top:8px}
.missing{color:var(--red);text-decoration:line-through}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;min-width:520px}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:9px}
th{color:var(--purple)}
tr.nh td:first-child{box-shadow:inset 3px 0 var(--red)}
ul{padding-left:20px}
.items{display:grid;gap:10px}
.item{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;align-items:start}
.item.shot{grid-template-columns:minmax(0,1fr) minmax(0,320px)}
.item img{width:100%;border-radius:6px;border:1px solid var(--line);display:block}
.item figcaption{color:var(--muted);font-size:12px;margin-top:4px}
.src{color:var(--purple);font-size:12px;font-family:ui-monospace,monospace}
.doc{width:min(900px,100%);margin-inline:auto}
.doc h1{font-size:22px;margin:0 0 14px}
.doc h2{margin-top:30px;border-bottom:1px solid var(--line);padding-bottom:4px}
.doc h3{margin-top:20px}
.doc code{background:var(--panel2);border:1px solid var(--line);border-radius:4px;padding:0 4px;font:13px ui-monospace,monospace;color:#ffd6f0}
.doc pre{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto}
.doc pre code{background:none;border:0;padding:0;color:var(--text)}
.doc blockquote{margin:10px 0;padding:6px 14px;border-left:3px solid var(--purple);color:var(--muted)}
.doc li{margin:3px 0}
.doc img{max-width:100%;border-radius:6px;border:1px solid var(--line)}
.doc hr{border:0;border-top:1px solid var(--line);margin:24px 0}
@media(max-width:700px){.item.shot{grid-template-columns:minmax(0,1fr)}}
@media(max-width:520px){main,header{padding-inline:11px}}
"""

E = lambda s: html.escape(s, quote=True)

# Themes live in the /theme skill (~/.claude/skills/theme). Default: cyberpunk (the CSS above is its fallback copy).
THEME = "cyberpunk"
_THEME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "theme")
try:
    sys.path.insert(0, _THEME_DIR)
    from theme import theme_css as _theme_css, ascii_safe  # noqa: E402
except ImportError:  # theme skill missing: built-in cyberpunk, still ASCII-safe output
    _theme_css = None
    def ascii_safe(page):
        return page.encode("ascii", "xmlcharrefreplace").decode("ascii")


def theme_css(name=None):
    name = name or THEME
    if _theme_css is None:
        if name != "cyberpunk":
            sys.exit(f"md2html: theme '{name}' needs the /theme skill at {_THEME_DIR}")
        return CSS
    return _theme_css(name)


def icon_link(root, outdir):
    """<link rel=icon> to the project's icon (see /theme favicon.py), or '' when the project has none."""
    try:
        from favicon import find_icon  # noqa: E402  (lives next to theme.py)
    except ImportError:
        return ""
    rel = find_icon(root) if root else None
    if not rel:
        return ""
    href = os.path.relpath(os.path.join(root, rel), outdir).replace(os.sep, "/")
    kind = "image/svg+xml" if rel.lower().endswith(".svg") else "image/x-icon"
    return f'<link rel="icon" type="{kind}" href="{E(href)}">'


def _git_root(path):
    d = os.path.dirname(os.path.abspath(path))
    while d != os.path.dirname(d):
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


def theme_style(name=None):
    name = name or THEME
    return f'<style id="theme" data-theme="{E(name)}">{theme_css(name)}</style>'
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def html_twin(md_path):
    return os.path.splitext(md_path)[0] + ".html"


def _href(url, base, todo):
    """Point relative .md links at their .html twin (queued for conversion); leave others alone."""
    if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", url, re.I):
        return url
    path, frag = (url.split("#", 1) + [""])[:2]
    if path.lower().endswith(".md"):
        target = os.path.normpath(os.path.join(base, unquote(path)))
        if os.path.isfile(target):
            todo.append(target)
            return quote(os.path.splitext(unquote(path))[0] + ".html", safe="/") + ("#" + frag if frag else "")
    return url


def _inline(text, base, todo):
    keep = []

    def stash(s):
        keep.append(s)
        return f"\x00{len(keep) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: stash(_code_span(m.group(1), base, todo)), text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
                  lambda m: stash(f'<img src="{E(m.group(2))}" alt="{E(m.group(1))}">'), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: stash(f'<a href="{E(_href(m.group(2), base, todo))}">') + m.group(1) + stash("</a>"), text)
    text = re.sub(r"(?<![\"'=])(https?://[^\s<>)]+)", lambda m: stash(f'<a href="{E(m.group(1))}">{E(m.group(1))}</a>'), text)
    text = E(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)


def _code_span(code, base, todo):
    """Inline code that names an existing local file becomes a link (e.g. `knowledge/shots/kp04.jpg`)."""
    out = f"<code>{E(code)}</code>"
    if " " in code.strip() and not os.path.exists(os.path.join(base, code)):
        return out
    # Paths in notes are often relative to the video folder, one level up from knowledge/.
    for cand in (code, "../" + code):
        if os.path.isfile(os.path.join(base, cand)):
            rel = _href(quote(cand, safe="/"), base, todo)
            if cand.lower().endswith(IMG_EXT):
                return f'<a href="{E(rel)}">{out}</a><br><img loading="lazy" src="{E(rel)}" alt="" style="max-width:420px">'
            return f'<a href="{E(rel)}">{out}</a>'
    return out


def md_to_body(md, base, todo):
    lines = md.replace("\r\n", "\n").split("\n")
    out, para, i = [], [], 0
    lists = []  # stack of (indent, tag)

    def flush():
        if para:
            out.append("<p>" + "<br>".join(_inline(p.strip(), base, todo) for p in para) + "</p>")
            para.clear()

    def close_lists(to=-1):
        while lists and lists[-1][0] > to:
            out.append(f"</li></{lists.pop()[1]}>")

    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            flush(); close_lists()
            j, code = i + 1, []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j]); j += 1
            out.append("<pre><code>" + E("\n".join(code)) + "</code></pre>")
            i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", ln)
        if m:
            flush(); close_lists()
            n = len(m.group(1))
            out.append(f"<h{n}>{_inline(m.group(2), base, todo)}</h{n}>")
            i += 1; continue
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", ln):
            flush(); close_lists(); out.append("<hr>"); i += 1; continue
        if "|" in ln and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            flush(); close_lists()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln)
            rows, j = [], i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                rows.append(cells(lines[j])); j += 1
            out.append('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{_inline(c, base, todo)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{_inline(c, base, todo)}</td>" for c in r) + "</tr>" for r in rows)
                       + "</tbody></table></div>")
            i = j; continue
        if ln.startswith(">"):
            flush(); close_lists()
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].lstrip()); i += 1
            out.append("<blockquote>" + md_to_body("\n".join(q), base, todo) + "</blockquote>")
            continue
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", ln)
        if m:
            flush()
            ind, tag = len(m.group(1).expandtabs(4)), ("ol" if m.group(2)[0].isdigit() else "ul")
            if lists and ind > lists[-1][0]:
                out.append(f"<{tag}><li>"); lists.append((ind, tag))
            else:
                close_lists(ind)
                if lists and lists[-1][0] == ind and lists[-1][1] == tag:
                    out.append("</li><li>")
                else:
                    close_lists(ind - 1)
                    out.append(f"<{tag}><li>"); lists.append((ind, tag))
            out.append(_inline(m.group(3), base, todo))
            i += 1; continue
        if not ln.strip():
            flush()
            # A blank line ends a list unless the next line continues it.
            nxt = next((l for l in lines[i + 1:] if l.strip()), "")
            if lists and not re.match(r"^\s*([-*+]|\d+[.)])\s+|^\s{2,}\S", nxt):
                close_lists()
            i += 1; continue
        if lists and re.match(r"^\s{2,}\S", ln):
            out.append("<br>" + _inline(ln.strip(), base, todo)); i += 1; continue
        close_lists()
        para.append(ln)
        i += 1
    flush(); close_lists()
    return "\n".join(out)


def convert(md_path, _done=None):
    """Write md_path's .html twin (and those of the .md files it links to). Returns the .html path."""
    md_path = os.path.abspath(md_path)
    done = _done if _done is not None else set()
    out = html_twin(md_path)
    if md_path in done:
        return out
    done.add(md_path)
    with open(md_path, encoding="utf-8", errors="replace") as fh:
        md = fh.read()
    todo = []
    body = md_to_body(md, os.path.dirname(md_path), todo)
    m = re.search(r"^#\s+(.+)$", md, re.M)
    title = m.group(1).strip() if m else os.path.basename(md_path)
    src = os.path.basename(md_path)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>{icon_link(_git_root(md_path), os.path.dirname(out))}{theme_style()}</head><body>
<header><div class="bar"><h1>{E(title)}</h1><span class="stamp">Source: {E(src)} · {time.strftime("%Y-%m-%d %H:%M")}</span></div></header>
<main><article class="doc">
{body}
</article></main></body></html>
"""
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(ascii_safe(page))
    for t in todo:
        convert(t, done)
    return out


def relink(page_path):
    """Convert every local .md a page links to, and rewrite those links to the .html twins."""
    base = os.path.dirname(os.path.abspath(page_path))
    with open(page_path, encoding="utf-8") as fh:
        src = fh.read()
    done, todo = set(), []
    new = re.sub(r'href="([^"]+)"', lambda m: f'href="{E(_href(html.unescape(m.group(1)), base, todo))}"', src)
    for t in todo:
        convert(t, done)
    if new != src:
        with open(page_path, "w", encoding="utf-8") as fh:
            fh.write(new)
    return sorted(html_twin(t) for t in set(todo))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--theme" and len(args) > 2:
        THEME = args[1]
        args = args[2:]
    if args[0] == "--relink":
        for p in args[1:]:
            for h in relink(p):
                print(h)
    else:
        for p in args:
            print(convert(p))
