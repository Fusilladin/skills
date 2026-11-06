#!/usr/bin/env python3
"""human-summary: discover project pages/status files, render a themed one-page HTML summary."""
import argparse, fnmatch, html, json, os, re, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md2html  # noqa: E402
from md2html import convert, theme_style, ascii_safe, icon_link  # noqa: E402  shared theme; .md links become themed .html twins

SKIP = {".git", "node_modules", "__pycache__", "dist", "build", "venv"}
OUTNAME = "human-summary.html"
STATUS = ["TODO.md", "README.md", "CLAUDE.md", "AGENTS.md", "BUILD_STATUS.md", "*review*.json", "*decisions*.json"]


def root_of(arg):
    start = os.path.abspath(arg or os.getcwd())
    try:
        r = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except OSError:
        pass
    return start


def walk(root):
    base = root.rstrip(os.sep).count(os.sep)
    for d, dirs, files in os.walk(root):
        depth = d.count(os.sep) - base
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".") and depth < 4]
        for f in files:
            yield os.path.join(d, f)


def title_of(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            m = re.search(r"<title[^>]*>(.*?)</title>", fh.read(65536), re.S | re.I)
        return html.unescape(" ".join(m.group(1).split())) if m else ""
    except OSError:
        return ""


def pages(root, out=None):
    out = os.path.abspath(out) if out else os.path.join(root, OUTNAME)
    res = []
    for p in walk(root):
        # Skip .html twins of .md files; they are reached through the page's links.
        if (p.lower().endswith(".html") and os.path.abspath(p) != out and os.path.basename(p) != OUTNAME
                and not os.path.exists(os.path.splitext(p)[0] + ".md")):
            res.append({"path": os.path.relpath(p, root), "title": title_of(p) or os.path.basename(p),
                        "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(p))),
                        "_t": os.path.getmtime(p)})
    res.sort(key=lambda x: -x["_t"])
    for r in res:
        del r["_t"]
    return res


def discover(a):
    root = root_of(a.root)
    src = [os.path.relpath(p, root) for p in walk(root)
           if any(fnmatch.fnmatch(os.path.basename(p), g) for g in STATUS)
           # Docs anywhere in the top two levels; JSON records only at the top, to avoid evidence-folder noise.
           and os.path.relpath(p, root).count(os.sep) <= (0 if p.endswith(".json") else 1)]
    src.sort(key=lambda s: (s.count(os.sep), s))
    print(json.dumps({"root": root, "html_pages": pages(root), "status_sources": src}, indent=2))


def fail(msg):
    sys.exit("render.py: " + msg)


def validate(c):
    if not isinstance(c, dict):
        fail("content JSON must be an object")
    for k, t in (("title", str), ("summary", list), ("needs_human", list), ("artifacts", list)):
        if k not in c:
            fail(f"missing required key '{k}'")
        if not isinstance(c[k], t):
            fail(f"'{k}' must be a {t.__name__}")
    for k in ("status", "done_recently", "exclude_pages"):
        if k in c and not isinstance(c[k], list):
            fail(f"'{k}' must be a list")
    if not all(isinstance(s, str) for s in c["summary"] + c.get("done_recently", []) + c.get("exclude_pages", [])):
        fail("'summary', 'done_recently', 'exclude_pages' must contain strings")
    for k in ("status", "needs_human", "artifacts"):
        for i, x in enumerate(c.get(k, [])):
            if not isinstance(x, dict):
                fail(f"'{k}[{i}]' must be an object")
    for i, x in enumerate(c["needs_human"]):
        if not isinstance(x.get("title"), str):
            fail(f"needs_human[{i}] needs a string 'title'")
        if not isinstance(x.get("links", []), list) or not all(isinstance(l, dict) for l in x.get("links", [])):
            fail(f"needs_human[{i}].links must be a list of objects")
    if "sections" in c and not isinstance(c["sections"], list):
        fail("'sections' must be a list")
    for i, s in enumerate(c.get("sections", [])):
        if not isinstance(s, dict) or not isinstance(s.get("heading"), str) or not isinstance(s.get("items", []), list):
            fail(f"sections[{i}] needs a string 'heading' and a list 'items'")
        for j, it in enumerate(s.get("items", [])):
            if not isinstance(it, dict) or not isinstance(it.get("text", ""), str):
                fail(f"sections[{i}].items[{j}] must be an object with string 'text'")
            if "image" in it and not (isinstance(it["image"], dict) and isinstance(it["image"].get("path"), str)):
                fail(f"sections[{i}].items[{j}].image needs a string 'path'")
    for i, x in enumerate(c["artifacts"]):
        if not isinstance(x.get("label"), str) or not isinstance(x.get("path"), str):
            fail(f"artifacts[{i}] needs string 'label' and 'path'")
    for i, g in enumerate(c.get("nav_groups") or []):
        if not isinstance(g, dict) or not isinstance(g.get("label"), str) or not isinstance(g.get("pages", []), list):
            fail(f"nav_groups[{i}] needs a string 'label' and a list 'pages' (paths or {{path,label}})")
    # Enforced: anything waiting on the human must be answerable on the page and copyable back to the agent.
    decisions = c.get("decisions", [])
    if not isinstance(decisions, list):
        fail("'decisions' must be a list")
    if c["needs_human"] and not decisions:
        fail("'needs_human' is not empty, so 'decisions' is required: give every open item a decision card "
             "(id, title, why, options, recommended) so the human can answer and copy the choices back")
    seen = set()
    for i, d in enumerate(decisions):
        if not isinstance(d, dict):
            fail(f"decisions[{i}] must be an object")
        did = d.get("id")
        if not isinstance(did, str) or not re.fullmatch(r"[a-z0-9_]{1,60}", did):
            fail(f"decisions[{i}].id must be snake_case [a-z0-9_]")
        if did in seen:
            fail(f"decisions[{i}].id '{did}' is duplicated")
        seen.add(did)
        if not isinstance(d.get("title"), str):
            fail(f"decisions[{i}] needs a string 'title'")
        opts = d.get("options")
        if not isinstance(opts, list) or len(opts) < 2 or not all(isinstance(o, str) and o for o in opts):
            fail(f"decisions[{i}].options must list at least 2 non-empty strings")
        if "recommended" in d and d["recommended"] not in opts:
            fail(f"decisions[{i}].recommended must be one of its options")
        if not isinstance(d.get("links", []), list) or not all(isinstance(l, dict) for l in d.get("links", [])):
            fail(f"decisions[{i}].links must be a list of objects")


E = lambda s: html.escape(str(s if s is not None else ""), quote=True)

# Category names for the nav dropdowns when the content JSON gives no "nav_groups".
NAV_DIRS = {"runs": "Run outputs", "output": "Run outputs", "audits": "Audits", "notes": "Notes", "docs": "Docs",
            "reports": "Reports", "plans": "Plans", "review": "Reviews", "reviews": "Reviews", "topics": "Topics",
            "out": "Outputs", "examples": "Examples", "media": "Media", ".artifacts": "Artifacts"}


def nav_html(found, groups, root, outdir):
    """Top bar: a jump to the decisions plus one dropdown per category (explicit nav_groups first)."""
    href = lambda path: E(os.path.relpath(os.path.join(root, path), outdir).replace(os.sep, "/"))
    title = {p["path"]: p["title"] for p in found}
    cats, used = [], set()
    for g in groups or []:
        items = [(x if isinstance(x, dict) else {"path": x}) for x in g.get("pages", [])]
        items = [(i["path"], i.get("label") or title.get(i["path"]) or os.path.basename(i["path"])) for i in items
                 if os.path.exists(os.path.join(root, i["path"]))]
        if items:
            cats.append((g["label"], items)); used.update(pth for pth, _ in items)
    rest = {}
    for p in found:
        if p["path"] in used:
            continue
        parts = p["path"].split(os.sep)
        label = "Pages" if len(parts) == 1 else NAV_DIRS.get(parts[0], parts[0].strip(".").replace("-", " ").replace("_", " ").title())
        rest.setdefault(label, []).append((p["path"], p["title"]))
    cats += sorted(rest.items(), key=lambda kv: (kv[0] == "Pages", kv[0]))
    menus = "".join(f'<details><summary>{E(lbl)}</summary><div class="menu">'
                    + "".join(f'<a href="{href(pth)}">{E(t)}</a>' for pth, t in items) + "</div></details>"
                    for lbl, items in cats)
    return '<a href="#decisions">Decisions &darr;</a>' + menus


NAV_CSS = """
nav details{position:relative}
nav summary{list-style:none;cursor:pointer;color:var(--text);padding:3px 11px;border:1px solid var(--line);border-radius:99px;background:var(--panel2);font-size:13px}
nav summary::-webkit-details-marker{display:none}
nav summary::after{content:" \\25BE";color:var(--purple)}
nav details[open] summary,nav summary:hover{color:var(--green);border-color:var(--green)}
nav .menu{position:absolute;top:calc(100% + 6px);left:0;z-index:20;min-width:220px;max-width:min(420px,90vw);display:grid;gap:2px;padding:6px;background:var(--panel);border:1px solid var(--purple);border-radius:10px;box-shadow:0 12px 30px #000a}
nav .menu a{border:0;border-radius:6px;background:none;white-space:normal}
nav .menu a:hover{background:rgba(189,112,255,.12)}
@media(max-width:520px){nav .menu{position:fixed;left:12px;right:12px;top:auto;max-width:none}}
"""

NAV_JS = """(()=>{const d=[...document.querySelectorAll('nav details')];d.forEach(x=>x.addEventListener('toggle',()=>{if(x.open)d.forEach(o=>o!==x&&(o.open=false))}));document.addEventListener('click',e=>{if(!e.target.closest('nav details')||e.target.closest('.menu a'))d.forEach(x=>x.open=false)});document.addEventListener('keydown',e=>{if(e.key==='Escape')d.forEach(x=>x.open=false)})})();"""

DEFAULT_DECISION = {"id": "feedback", "title": "Anything for the agent?",
                    "why": "Nothing on this page needs a decision; use this to approve, ask for changes or add notes.",
                    "options": ["Looks good, continue", "Changes needed (see notes)", "Hold"],
                    "recommended": "Looks good, continue"}

DECISION_CSS = """
.decision{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:16px;margin:10px 0}
.decision.done{border-left:3px solid var(--green)}
.did{font-family:ui-monospace,monospace;color:var(--muted);font-size:12px}
.recline{color:#dcbcff;font-size:14px}.recline b{color:var(--purple)}
.choice{display:grid;gap:6px;align-content:start;min-width:0}
.choice label,.dec-tools label{font-size:12px;color:var(--green);font-weight:700}
.choice select,.choice textarea,.dec-tools input{width:100%;max-width:100%;min-width:0;font:inherit;font-size:14px;color:var(--text);background:#080a10;border:1px solid #596078;border-radius:7px;padding:8px}
.dec-tools input{max-width:420px;display:block;margin-top:4px}
.actions{display:flex;flex-wrap:wrap;gap:8px}
.actions button{border:1px solid var(--green);border-radius:7px;background:#10271c;color:var(--text);font:inherit;font-size:14px;padding:7px 12px;cursor:pointer}
.actions .danger{border-color:var(--red);background:#30151b}
#dec-status{margin:10px 0;padding:8px;border:1px solid var(--line);border-radius:6px;font-size:13px}
#dec-status[data-state=saved]{color:var(--green)}#dec-status[data-state=error]{color:#ff9aa4;border-color:var(--red)}
@media(max-width:720px){.decision{grid-template-columns:minmax(0,1fr)}}
"""

DECISION_JS = r"""(()=>{
const M=HS_META,KEY=M.key,VER='human-summary-decisions-v1';
const q=s=>document.querySelector(s),sel=()=>[...document.querySelectorAll('select[data-choice]')],st=q('#dec-status');
function msg(t,k){st.textContent=t;st.dataset.state=k}
function gather(){const d={schema_version:VER,title:M.title,project:M.project,page_generated:M.generated,reviewer:q('#dec-reviewer').value,updated_at:new Date().toISOString(),decisions:{}};
 for(const s of sel()){const card=s.closest('.decision');d.decisions[s.dataset.choice]={title:card.querySelector('h3').textContent,choice:s.value,notes:q(`[data-note="${s.dataset.choice}"]`).value}}return d}
function progress(){const all=sel(),n=all.filter(s=>s.value).length,t=n+' / '+all.length+' decided';
 for(const id of ['dec-badge','dec-badge-2']){const b=document.getElementById(id);if(b){b.textContent=t;b.classList.toggle('ok',n===all.length)}}
 all.forEach(s=>s.closest('.decision').classList.toggle('done',!!s.value))}
function save(){progress();try{localStorage.setItem(KEY,JSON.stringify(gather()));msg('Saved in this browser · '+new Date().toLocaleString(),'saved')}catch(e){msg('Could not save locally ('+e.name+'). Copy or export now.','error')}}
function load(){try{const raw=localStorage.getItem(KEY);if(!raw){msg('No local save yet. Everything starts Undecided.','info');return}
 const x=JSON.parse(raw);if(x.schema_version!==VER)throw Error('older save');q('#dec-reviewer').value=x.reviewer||'';
 for(const s of sel()){const v=(x.decisions||{})[s.dataset.choice];if(v){if([...s.options].some(o=>o.value===v.choice))s.value=v.choice;q(`[data-note="${s.dataset.choice}"]`).value=v.notes||''}}
 msg('Loaded your saved choices from '+(x.updated_at||'earlier')+'.','saved')}catch(e){msg('Saved choices unreadable ('+e.message+'). Page still works.','error')}}
function md(d){const L=['# '+d.title+' — decisions','','Project: '+(d.project||'-')+'  ','Page generated: '+d.page_generated+'  ','Reviewer: '+(d.reviewer||'Not provided')+'  ','Updated: '+d.updated_at,'','## Decisions'];
 for(const [k,v] of Object.entries(d.decisions))L.push('','### '+k+' — '+v.title,'Choice: '+(v.choice||'Undecided'),'','Notes: '+(v.notes||'—'));const NL=String.fromCharCode(10);return L.join(NL)+NL}
function dl(name,type,body){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([body],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
const base=(M.project||'summary').replace(/[^a-z0-9]+/gi,'-').toLowerCase()+'-decisions';
document.querySelectorAll('.decision select,.decision textarea,#dec-reviewer').forEach(e=>{e.addEventListener('change',save);if(e.tagName!=='SELECT')e.addEventListener('input',save)});
q('#dec-copy').addEventListener('click',async()=>{const t=md(gather());try{await navigator.clipboard.writeText(t);msg('Choices copied. Paste them back to the agent.','saved')}catch(e){const a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();let ok=false;try{ok=document.execCommand('copy')}catch(_){}a.remove();msg(ok?'Choices copied. Paste them back to the agent.':'Copy blocked by the browser. Use Export Markdown.',ok?'saved':'error')}});
q('#dec-json').addEventListener('click',()=>{dl(base+'.json','application/json',JSON.stringify(gather(),null,2));msg('JSON exported.','saved')});
q('#dec-md').addEventListener('click',()=>{dl(base+'.md','text/markdown',md(gather()));msg('Markdown exported.','saved')});
q('#dec-reset').addEventListener('click',()=>{if(!confirm('Clear all choices saved in this browser?'))return;try{localStorage.removeItem(KEY)}catch(e){}sel().forEach(s=>s.value='');document.querySelectorAll('.decision textarea').forEach(t=>t.value='');q('#dec-reviewer').value='';progress();msg('Reset. Everything is Undecided.','info')});
load();progress();
})();"""



def link(root, outdir, label, path):
    if not path:
        return f"<span>{E(label)}</span>"
    full = os.path.normpath(os.path.join(root, path))
    rel = os.path.relpath(full, outdir)
    if not os.path.exists(full):
        return f'<span class="missing">{E(label or path)}</span> <span class="status">missing file</span>'
    if full.lower().endswith(".md"):
        rel = os.path.relpath(convert(full), outdir)
    return f'<a href="{E(rel.replace(os.sep, "/"))}">{E(label or path)}</a>'


def render(a):
    try:
        with open(a.content, encoding="utf-8") as fh:
            c = json.load(fh)
    except OSError as e:
        fail(f"cannot read {a.content}: {e.strerror}")
    except json.JSONDecodeError as e:
        fail(f"{a.content} is not valid JSON: {e}")
    validate(c)
    theme = (a.theme or c.get("theme") or "cyberpunk").strip().lower()
    md2html.THEME = theme  # .md twins converted below use the same theme
    md2html.theme_css(theme)  # fail early on an unknown theme
    root = root_of(a.root)
    # A summary without a discoverable project SVG has no reliable tab identity.
    # Keep this check here so rendering cannot silently produce an unbranded page.
    try:
        from favicon import find_icon
    except ImportError:
        fail("cannot locate favicon discovery helper; install the /theme skill")
    project_icon = find_icon(root)
    if not project_icon or not project_icon.lower().endswith(".svg"):
        fail("a project SVG favicon is required; reuse a relevant icon or create assets/favicon.svg before rendering")
    icon_tag = icon_link(root, os.path.dirname(os.path.abspath(a.o or os.path.join(root, OUTNAME))))
    if 'rel="icon" type="image/svg+xml"' not in icon_tag:
        fail("could not link the project SVG favicon")
    out = os.path.abspath(a.o or os.path.join(root, OUTNAME))
    outdir = os.path.dirname(out)
    ex = set(c.get("exclude_pages", []))
    found = [p for p in pages(root, out) if p["path"] not in ex]
    nav = nav_html(found, c.get("nav_groups"), root, outdir)
    n = len(c["needs_human"])
    badge = (f'<span class="status">{n} need{"s" if n == 1 else ""} your review</span>' if n
             else '<span class="status ok">Nothing waiting on you</span>')
    strip = "".join(
        f'<div><strong>{E(s.get("value"))}</strong><span class="l">{E(s.get("label"))}</span> '
        f'<span class="status {"ok" if s.get("state") == "done" else "info" if s.get("state") == "info" else ""}">'
        f'{E({"done": "done", "info": "info"}.get(s.get("state"), "needs human"))}</span></div>'
        for s in c.get("status", []))
    cards = "".join(
        f'<div class="card pending"><h3>{E(x["title"])}</h3><p>{E(x.get("detail"))}</p><div class="links">'
        + "".join(link(root, outdir, l.get("label"), l.get("path")) for l in x.get("links", []))
        + "</div></div>" for x in c["needs_human"]) or '<p class="muted">Nothing is waiting on you.</p>'
    rows = "".join(
        f'<tr class="{"nh" if x.get("needs_human") is True else ""}"><td>{link(root, outdir, x["label"], x["path"])}</td>'
        f'<td>{E(x.get("note"))}</td><td>{"<span class=status>needs human</span>" if x.get("needs_human") is True else ""}</td></tr>'
        for x in c["artifacts"])
    def item(it):
        head = f"<h3 style=\"color:var(--green)\">{E(it['title'])}</h3>" if it.get("title") else ""
        src = f'<div class="src">{E(it["source"])}</div>' if it.get("source") else ""
        img = it.get("image")
        fig = ""
        if img:
            full = os.path.normpath(os.path.join(root, img["path"]))
            if os.path.exists(full):
                rel = os.path.relpath(full, outdir).replace(os.sep, "/")
                fig = (f'<figure style="margin:0"><a href="{E(rel)}"><img loading="lazy" src="{E(rel)}" alt="{E(img.get("caption"))}"></a>'
                       f'<figcaption>{E(img.get("caption"))}</figcaption></figure>')
            else:
                fig = f'<p class="missing">{E(img["path"])}</p>'
        return f'<div class="card item{" shot" if fig else ""}"><div>{head}<p>{E(it.get("text"))}</p>{src}</div>{fig}</div>'
    sections = "".join(
        f'<section><h2>{E(s["heading"])}</h2>{"<p class=muted>" + E(s.get("intro")) + "</p>" if s.get("intro") else ""}'
        f'<div class="items">{"".join(item(it) for it in s.get("items", []))}</div></section>'
        for s in c.get("sections", []))
    done = "".join(f"<li>{E(d)}</li>" for d in c.get("done_recently", []))
    decisions = c.get("decisions") or [DEFAULT_DECISION]  # the Copy-for-agent section is always present
    dec_html = ""
    if decisions:
        def dcard(i, d):
            did = d["id"]
            opts = "".join(f'<option value="{E(o)}">{E(o)}</option>' for o in d["options"])
            rec = f'<p class="recline"><b>Recommended:</b> {E(d["recommended"])}</p>' if d.get("recommended") else ""
            links = "".join(link(root, outdir, l.get("label"), l.get("path")) for l in d.get("links", []))
            return (f'<article class="card decision" data-id="{E(did)}"><div><span class="did">{i:02d} · {E(did)}</span>'
                    f'<h3>{E(d["title"])}</h3>{"<p>" + E(d.get("why")) + "</p>" if d.get("why") else ""}{rec}'
                    f'{"<div class=links>" + links + "</div>" if links else ""}</div>'
                    f'<div class="choice"><label for="choice-{E(did)}">Your choice</label>'
                    f'<select id="choice-{E(did)}" data-choice="{E(did)}"><option value="">Undecided</option>{opts}</select>'
                    f'<label for="note-{E(did)}">Notes</label><textarea id="note-{E(did)}" data-note="{E(did)}" rows="2"></textarea></div></article>')
        dec_html = (f'<section id="decisions"><h2>Your decisions <span class="status" id="dec-badge-2">0 / {len(decisions)} decided</span></h2>'
                    '<p class="muted">Recommended answers are shown on each card; nothing is preselected. Choices save in this browser. '
                    'Click <b>Copy choices</b> and paste the result back to the agent.</p>'
                    '<div class="card dec-tools"><label for="dec-reviewer">Reviewer (optional)</label>'
                    '<input id="dec-reviewer" type="text" placeholder="Name or initials">'
                    '<p id="dec-status" role="status" aria-live="polite">No local save yet.</p>'
                    '<div class="actions"><button id="dec-copy">Copy choices</button><button id="dec-json">Export JSON</button>'
                    '<button id="dec-md">Export Markdown</button><button id="dec-reset" class="danger">Reset…</button></div></div>'
                    + "".join(dcard(i + 1, d) for i, d in enumerate(decisions)) + "</section>")
        meta = {"title": c["title"], "project": c.get("project", ""), "generated": time.strftime("%Y-%m-%d %H:%M"),
                "key": "human-summary." + re.sub(r"[^a-z0-9]+", "-", (c.get("project", "") + "-" + c["title"]).lower()).strip("-")}
        dec_html += "<script>const HS_META=" + json.dumps(meta).replace("</", "<\\/") + ";</script><script>" + DECISION_JS + "</script>"
        badge = f'<span class="status" id="dec-badge">0 / {len(decisions)} decided</span>'
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(c["title"])}</title>{icon_tag}{theme_style(theme)}<style>{NAV_CSS}{DECISION_CSS}</style></head><body>
<header><div class="bar"><h1>{E(c["title"])}</h1>{badge}<span class="stamp">Generated {time.strftime("%Y-%m-%d %H:%M")}</span></div>
<nav>{nav}</nav></header><main>
{f'<div class="strip">{strip}</div>' if strip else ""}
<section><h2>Needs your review</h2>{cards}</section>
{dec_html}
<section><h2>Summary</h2>{"".join(f"<p>{E(s)}</p>" for s in c["summary"])}</section>
{sections}
<section><h2>Artifacts</h2><div class="table-wrap"><table><thead><tr><th>Artifact</th><th>What to look at</th><th></th></tr></thead><tbody>{rows}</tbody></table></div></section>
{f"<section><h2>Done recently</h2><ul>{done}</ul></section>" if done else ""}
</main><script>{NAV_JS}</script></body></html>
"""
    os.makedirs(outdir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(ascii_safe(page))
    print(out)


p = argparse.ArgumentParser(description=__doc__)
s = p.add_subparsers(dest="cmd", required=True)
d = s.add_parser("discover"); d.add_argument("root", nargs="?"); d.set_defaults(f=discover)
r = s.add_parser("render"); r.add_argument("content"); r.add_argument("-o"); r.add_argument("--root")
r.add_argument("--theme", help="theme from the /theme skill (default: cyberpunk)"); r.set_defaults(f=render)
a = p.parse_args()
a.f(a)
