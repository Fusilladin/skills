#!/usr/bin/env python3
"""review_kit.py - shared page kit for the weekly review pages (handoff, verify, memory, review-all index).

One visual system (orbit-ledger dark theme), few words, SVG first (owner 2026-11-10):
  hero = one short verdict line + 3-4 big numbers; every section = one SVG chart + at most one short line,
  technical detail only in one closed "Details" panel; fixes = cards, each with its own small SVG built from
  that fix's own data (viz spec), a done/open chip and one short line; decision cards with Copy choices;
  read marks (Run Dashboard /api/page-read); collapsible sections; scroll-perf; theme fix-chars.

Builders import the adjacent module: import review_kit as K
Fix / finding viz specs (put on each item as "viz"; numbers come from the review data, never invented):
  {"type":"ba", "before":10, "after":0, "unit":"failed launches", "bl":"11-04", "al":"since 11-05"}       before -> after bars
  {"type":"dots", "n":23, "good":0, "label":"lost rounds with a note"}                                  n dots, `good` green (or "bad":k red)
  {"type":"ticks", "n":71, "bad":66, "cap":3, "label":"cloud launches"}                                 strip of n ticks; optional cap marker
  {"type":"segs", "segs":[["attempt 1",364,"bad"],["attempt 2",366,"bad"],["start over",301,"warn"]], "unit":"min"}  proportional segments
  {"type":"events", "events":[["06:46:41","relaunch","ok"],["+26 s","reopen drops it","bad"]]}           markers on a line
  {"type":"flow", "steps":[["All tasks done","ok"],["Build skipped","skip"],["Audit","ok"]]}            boxes with arrows
  {"type":"split", "parts":[["wallpaper",128,"warn"],["second",256,"warn"]], "unit":"MB"}             one stacked bar
  {"type":"gap", "minutes":20, "a":"rc=75", "b":"next launch"}                                          a wait between two events
kinds: ok (green), bad (red), warn (amber), skip/muted (grey), info (indigo).
"""
import html, json, os, re, subprocess

E = lambda s: html.escape(str(s), quote=True)
HOME = os.path.expanduser('~')
PROJECTS = os.environ.get('PROJECTS_ROOT', os.path.join(HOME, 'projects'))
COL = {'ok': 'var(--green)', 'bad': 'var(--red)', 'warn': 'var(--amber)', 'skip': '#3a404a', 'muted': '#3a404a', 'info': 'var(--purple)'}
c = lambda k: COL.get(k, k if str(k).startswith(('var', '#')) else 'var(--purple)')


def fmt(v):
    return f'{v:,.0f}' if isinstance(v, (int, float)) and float(v).is_integer() else f'{v:,.1f}' if isinstance(v, float) else str(v)


# ---------- big charts ----------
def tiles(items):
    """items: [(value, label, kind)] -> big number row (counts up on reveal)."""
    out = ''
    for v, l, k in items:
        num = re.match(r'^([$]?)([\d.,]+)(.*)$', str(v))
        inner = (f'{E(num[1])}<span class="cnum" data-to="{num[2].replace(",", "")}">{E(num[2])}</span>{E(num[3])}' if num else E(v))
        out += f'<div class="tile t-{k or "n"}"><b>{inner}</b><span>{E(l)}</span></div>'
    return f'<div class="tiles">{out}</div>'


def donut(parts, center, sub, size=150):
    tot = sum(v for _, v, _ in parts) or 1; C = 2 * 3.14159265 * 42; off = 0; g = ''
    for n, v, k in parts:
        if not v: continue
        L = C * v / tot
        g += (f'<circle cx="60" cy="60" r="42" fill="none" stroke="{c(k)}" stroke-width="13" stroke-dasharray="{max(L - 1.5, .5):.2f} {C:.2f}" '
              f'stroke-dashoffset="{-off:.2f}" transform="rotate(-90 60 60)"><title>{E(n)}: {v}</title></circle>'); off += L
    leg = ''.join(f'<li><i style="background:{c(k)}"></i><b>{fmt(v)}</b> {E(n)}</li>' for n, v, k in parts)
    return (f'<div class="dwrap"><svg class="donut" viewBox="0 0 120 120" width="{size}" height="{size}" role="img" aria-label="{E(center)} {E(sub)}">'
            f'<circle cx="60" cy="60" r="42" fill="none" stroke="var(--panel2)" stroke-width="13"/>{g}'
            f'<text x="60" y="62" text-anchor="middle" class="dn-n">{E(center)}</text><text x="60" y="78" text-anchor="middle" class="dn-s">{E(sub)}</text></svg>'
            f'<ul class="leg">{leg}</ul></div>')


def hbars(items, unit='', W=640, label='bars'):
    """items: [(label, value, kind)]"""
    mx = max([v for _, v, _ in items] + [1]); lw = min(260, W * .38); rh = 34; g = ''
    for i, (l, v, k) in enumerate(items):
        y = 6 + i * rh; w = max(3, (W - lw - 70) * v / mx)
        g += (f'<text class="lb" x="0" y="{y + 15}">{E(l)}</text><rect class="grow" x="{lw:.0f}" y="{y + 4}" width="{w:.1f}" height="16" rx="4" fill="{c(k)}"/>'
              f'<text class="vl" x="{lw + w + 8:.1f}" y="{y + 17}">{fmt(v)}{E(unit)}</text>')
    return f'<svg viewBox="0 0 {W} {12 + len(items) * rh}" role="img" aria-label="{E(label)}">{g}</svg>'


def funnel(top, parts, W=640):
    """top: (label, n); parts: [(label, n, kind, note)] -> one wide bar split into blocks, legend below."""
    tot = top[1] or 1; x = 0; g = f'<text class="lb" x="0" y="14">{E(top[0])}: {fmt(top[1])}</text>'
    for l, n, k, note in parts:
        w = W * n / tot
        g += f'<rect class="grow" x="{x:.1f}" y="24" width="{max(w - 3, 2):.1f}" height="44" rx="6" fill="{c(k)}"><title>{E(l)}: {n}</title></rect>'
        if w > 36: g += f'<text class="fv" x="{x + 10:.1f}" y="54" fill="#0b0c0e" style="fill:#0b0c0e">{fmt(n)}</text>'
        x += w
    leg = ''.join(f'<li><i style="background:{c(k)}"></i><b>{fmt(n)}</b> {E(l)}{(" (" + E(note) + ")") if note else ""}</li>' for l, n, k, note in parts)
    return f'<svg viewBox="0 0 {W} 72" role="img" aria-label="{E(top[0])} split by outcome">{g}</svg><ul class="leg row">{leg}</ul>'


def stacked_days(days, keys, W=640, H=190):
    """days: [{'date':..., k: n}]; keys: [(key, label, kind)]"""
    n = max(len(days), 1); bw = min(56, W / n * .6); mx = max([sum(d.get(k, 0) for k, _, _ in keys) for d in days] + [1]); g = ''
    for i, d in enumerate(days):
        x = (i + .5) * W / n - bw / 2; y = H - 28; tot = 0
        for k, l, kind in keys:
            v = d.get(k, 0)
            if not v: continue
            h = (H - 60) * v / mx; y -= h; tot += v
            g += f'<rect class="grow" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h - 2:.1f}" rx="3" fill="{c(kind)}"><title>{E(d["date"])} {E(l)}: {v}</title></rect>'
        g += f'<text class="vl" x="{x + bw / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle">{tot or ""}</text><text class="lb" x="{x + bw / 2:.1f}" y="{H - 8}" text-anchor="middle">{E(d["date"][5:])}</text>'
    leg = ''.join(f'<li><i style="background:{c(kind)}"></i>{E(l)}</li>' for _, l, kind in keys)
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="per day">{g}</svg><ul class="leg row">{leg}</ul>'


def smallmult(series, W=640):
    """series: [(name, [(xlabel, pct or None)], trend_kind)] -> one SVG, one mini line per plan."""
    cols = 3; cw = W / cols; ch = 92; rows = (len(series) + cols - 1) // cols; g = ''
    for i, (name, pts, k) in enumerate(series):
        ox = (i % cols) * cw; oy = (i // cols) * ch
        g += f'<text class="lb" x="{ox + 6:.0f}" y="{oy + 16}">{E(name)}</text><line x1="{ox + 6}" x2="{ox + cw - 14:.0f}" y1="{oy + 78}" y2="{oy + 78}" stroke="var(--line)"/>'
        vals = [(j, p) for j, (_, p) in enumerate(pts) if p is not None]
        sx = lambda j: ox + 12 + j * (cw - 34) / max(len(pts) - 1, 1); sy = lambda p: oy + 76 - p * .5
        if len(vals) > 1:
            g += f'<polyline class="draw" pathLength="1" points="{" ".join(f"{sx(j):.1f},{sy(p):.1f}" for j, p in vals)}" fill="none" stroke="{c(k)}" stroke-width="2.2"/>'
        for j, p in vals:
            g += f'<circle cx="{sx(j):.1f}" cy="{sy(p):.1f}" r="3.2" fill="{c(k)}"><title>{E(name)} {E(pts[j][0])}: {p:.0f}%</title></circle>'
        if not vals: g += f'<text class="vl" x="{ox + 12:.0f}" y="{oy + 60}">no verdict</text>'
        last = vals[-1][1] if vals else None
        if last is not None: g += f'<text class="fv sm" x="{ox + cw - 14:.0f}" y="{oy + 16}" text-anchor="end">{last:.0f}%</text>'
    return f'<svg viewBox="0 0 {W} {rows * ch}" role="img" aria-label="pass rate per plan">{g}</svg>'


def timeline(span, marks, W=640):
    """span: (start_label, end_label, total_units); marks: [(pos_units, title, sub, kind, [bar values])] -> axis with event pins, each with mini bars."""
    lo, hi, T = span; g = f'<line x1="10" x2="{W - 10}" y1="40" y2="40" stroke="var(--line)" stroke-width="2"/><text class="lb" x="10" y="20">{E(lo)}</text><text class="lb" x="{W - 10}" y="20" text-anchor="end">{E(hi)}</text>'
    for m in marks:
        pos, t, sub, k, bars = m[:5]
        x = 10 + (W - 20) * pos / T
        g += f'<circle cx="{x:.1f}" cy="40" r="8" fill="{c(k)}"/><line x1="{x:.1f}" x2="{x:.1f}" y1="48" y2="66" stroke="{c(k)}"/>'
        anchor = m[5] if len(m) > 5 else ('start' if x < W * .7 else 'end'); tx = x - 8 if anchor == 'start' else x + 8
        g += f'<text class="fv sm" x="{tx:.1f}" y="84" text-anchor="{anchor}">{E(t)}</text><text class="lb" x="{tx:.1f}" y="100" text-anchor="{anchor}">{E(sub)}</text>'
        mx = max(bars + [1])
        for j, v in enumerate(bars):
            bx = tx + (j * 14 if anchor == 'start' else -(len(bars) - j) * 14)
            h = 44 * v / mx if mx > 1 else 0
            g += f'<rect class="grow" x="{bx:.1f}" y="{156 - h:.1f}" width="10" height="{max(h, 2):.1f}" rx="2" fill="{c(k)}"><title>{v} min</title></rect>'
    return f'<svg viewBox="0 0 {W} 164" role="img" aria-label="timeline">{g}</svg>'


def tickstrip(n, bad, label, W=640, cap=None):
    g = ''; w = W / n
    for i in range(n):
        g += f'<rect x="{i * w:.2f}" y="8" width="{max(w - 1.6, 1):.2f}" height="40" rx="1.5" fill="{c("bad" if i < bad else "skip")}"/>'
    if cap: g += f'<line x1="{cap * w:.1f}" x2="{cap * w:.1f}" y1="0" y2="56" stroke="var(--green)" stroke-width="2.5"/><text class="lb" x="{cap * w + 6:.1f}" y="70" fill="var(--green)">stop here</text>'
    return f'<svg viewBox="0 0 {W} 76" role="img" aria-label="{E(label)}">{g}</svg>'


def line2(points, unit, W=640, H=150, k='ok'):
    """points: [(xlabel, value)]"""
    mx = max(v for _, v in points) * 1.15; n = len(points); g = ''
    xs = [40 + i * (W - 80) / max(n - 1, 1) for i in range(n)]; ys = [H - 30 - (H - 50) * v / mx for _, v in points]
    g += f'<polyline class="draw" pathLength="1" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))}" fill="none" stroke="{c(k)}" stroke-width="3"/>'
    for (l, v), x, y in zip(points, xs, ys):
        g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{c(k)}"/><text class="fv sm" x="{x:.1f}" y="{y - 12:.1f}" text-anchor="middle">{fmt(v)} {E(unit)}</text><text class="lb" x="{x:.1f}" y="{H - 8}" text-anchor="middle">{E(l)}</text>'
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="trend">{g}</svg>'


def meter(done, total, label):
    W = 640; w = W * done / max(total, 1)
    return (f'<svg viewBox="0 0 {W} 30" role="img" aria-label="{E(label)}"><rect x="0" y="6" width="{W}" height="14" rx="7" fill="var(--panel2)"/>'
            f'<rect class="grow" x="0" y="6" width="{max(w, 0):.1f}" height="14" rx="7" fill="var(--green)"/></svg><p class="cap">{E(label)}</p>')


# ---------- per-item mini SVGs ----------
def mini(v):
    if not v: return ''
    t = v.get('type'); W, H = 220, 74; g = ''
    if t == 'ba':
        mx = max(v['before'], v['after'], 1)
        for i, (val, lab, k) in enumerate(((v['before'], v.get('bl', 'before'), v.get('bk', 'bad')), (v['after'], v.get('al', 'after'), v.get('ak', 'ok')))):
            w = max(150 * val / mx, 3); y = 6 + i * 30
            g += f'<text class="m-l" x="0" y="{y + 12}">{E(lab)}</text><rect class="grow" x="66" y="{y + 2}" width="{w:.1f}" height="13" rx="3" fill="{c(k)}"/><text class="m-v" x="{66 + w + 5:.1f}" y="{y + 13}">{fmt(val)}</text>'
        g += f'<text class="m-l" x="0" y="70">{E(v.get("unit", ""))}</text>'
    elif t == 'dots':
        n = v['n']; per = 12 if n > 12 else n; r = 6 if n <= 24 else 4.2; sp = 2 * r + 4
        good = v.get('good'); bad = v.get('bad')
        for i in range(n):
            k = ('ok' if i < good else 'bad') if good is not None else ('bad' if i < (bad or 0) else 'skip')
            if v.get('kind'): k = v['kind']
            g += f'<circle cx="{r + 1 + (i % per) * sp:.1f}" cy="{r + 2 + (i // per) * sp:.1f}" r="{r}" fill="{c(k)}"/>'
        g += f'<text class="m-l" x="0" y="70">{E(v.get("label", ""))}</text>'
    elif t == 'ticks':
        n = v['n']; w = W / n
        for i in range(n): g += f'<rect x="{i * w:.2f}" y="8" width="{max(w - .8, .8):.2f}" height="30" fill="{c("bad" if i < v.get("bad", 0) else "skip")}"/>'
        if v.get('cap'): g += f'<line x1="{v["cap"] * w:.1f}" x2="{v["cap"] * w:.1f}" y1="2" y2="46" stroke="var(--green)" stroke-width="2.5"/><text class="m-v" x="{v["cap"] * w + 4:.1f}" y="54" fill="var(--green)">stop after {v["cap"]}</text>'
        g += f'<text class="m-l" x="0" y="70">{E(v.get("label", ""))}</text>'
    elif t == 'segs':
        tot = sum(s[1] for s in v['segs']) or 1; x = 0
        for lab, val, k in v['segs']:
            w = W * val / tot
            g += f'<rect class="grow" x="{x:.1f}" y="10" width="{max(w - 2, 1):.1f}" height="22" rx="3" fill="{c(k)}"><title>{E(lab)}: {val}</title></rect><text class="m-v" x="{x + 2:.1f}" y="46">{fmt(val)}{E(v.get("unit", ""))}</text><text class="m-l" x="{x + 2:.1f}" y="60">{E(lab)}</text>'
            x += w
    elif t == 'events':
        ev = v['events']; n = len(ev); g += f'<line x1="8" x2="{W - 8}" y1="22" y2="22" stroke="var(--line)" stroke-width="2"/>'
        for i, (when, lab, k) in enumerate(ev):
            x = 10 + i * (W - 20) / max(n - 1, 1); a = 'start' if i == 0 else 'end' if i == n - 1 else 'middle'
            g += f'<circle cx="{x:.1f}" cy="22" r="6" fill="{c(k)}"/><text class="m-v" x="{x:.1f}" y="10" text-anchor="{a}">{E(when)}</text><text class="m-l" x="{x:.1f}" y="44" text-anchor="{a}">{E(lab)}</text>'
    elif t == 'flow':
        st = v['steps']; n = len(st); bw = (W - (n - 1) * 14) / n
        for i, (lab, k) in enumerate(st):
            x = i * (bw + 14)
            g += (f'<rect x="{x:.1f}" y="10" width="{bw:.1f}" height="36" rx="6" fill="none" stroke="{c(k)}" stroke-width="1.6"' + (' stroke-dasharray="4 3"' if k in ('skip', 'bad') else '') + '/>')
            words = lab.split(' '); l1 = ' '.join(words[:2]); l2 = ' '.join(words[2:])
            g += f'<text class="m-l b" x="{x + bw / 2:.1f}" y="{26 if l2 else 32}" text-anchor="middle">{E(l1)}</text>' + (f'<text class="m-l b" x="{x + bw / 2:.1f}" y="39" text-anchor="middle">{E(l2)}</text>' if l2 else '')
            if i < n - 1: g += f'<path d="M{x + bw + 2:.1f} 28 l9 0 m-4 -4 l4 4 l-4 4" fill="none" stroke="var(--faint)" stroke-width="1.5"/>'
        if v.get('label'): g += f'<text class="m-l" x="0" y="66">{E(v["label"])}</text>'
    elif t == 'split':
        tot = sum(p[1] for p in v['parts']) or 1; x = 0
        for lab, val, k in v['parts']:
            w = W * val / tot
            g += f'<rect class="grow" x="{x:.1f}" y="10" width="{max(w - 2, 1):.1f}" height="22" rx="3" fill="{c(k)}"/><text class="m-v" x="{x + 2:.1f}" y="46">{fmt(val)} {E(v.get("unit", ""))}</text><text class="m-l" x="{x + 2:.1f}" y="60">{E(lab)}</text>'
            x += w
    elif t == 'gap':
        g += (f'<circle cx="12" cy="24" r="7" fill="var(--red)"/><circle cx="{W - 12}" cy="24" r="7" fill="var(--green)"/>'
              f'<line x1="22" x2="{W - 22}" y1="24" y2="24" stroke="var(--amber)" stroke-width="2.5" stroke-dasharray="5 4"/>'
              f'<text class="m-v" x="{W / 2}" y="16" text-anchor="middle">wait {v["minutes"]} min</text>'
              f'<text class="m-l" x="4" y="50">{E(v.get("a", ""))}</text><text class="m-l" x="{W - 4}" y="50" text-anchor="end">{E(v.get("b", ""))}</text>')
    else:
        return ''
    return f'<svg class="mini" viewBox="0 0 {W} {H}" role="img" aria-label="{E(v.get("label", t))}">{g}</svg>'


CHIP = {'done': ('Done', 'ok'), 'open': ('Open', 'bad'), 'none': ('No change', 'skip'), 'leak': ('Leak', 'bad'), 'held': ('Held', 'warn'),
        'pileup': ('Piling up', 'bad'), 'normal': ('Normal', 'ok'), 'waiting': ('Waiting', 'warn')}


def cards(items):
    """items: [{status, name, line, viz, detail?}] -> card grid; open first."""
    order = {'open': 0, 'leak': 0, 'pileup': 0, 'held': 1, 'waiting': 1, 'none': 2, 'normal': 2, 'done': 3}
    out = ''
    for f in sorted(items, key=lambda f: order.get(f.get('status'), 2)):
        lab, k = CHIP.get(f.get('status'), (f.get('status', ''), 'skip'))
        out += (f'<article class="fc fc-{k}"><div class="fc-top"><span class="chip k-{k}">{E(lab)}</span><h3>{E(f["name"])}</h3></div>{mini(f.get("viz"))}'
                f'<p>{E(f.get("line", ""))}</p></article>')
    return f'<div class="fcards">{out}</div>'


def details(title, inner):
    return f'<details class="det"><summary>{E(title)}</summary><div class="det-b">{inner}</div></details>' if inner else ''


def dl(rows):
    """rows: [(bold, text)] -> compact list for Details panels."""
    return '<ul class="dlist">' + ''.join(f'<li><b>{E(a)}</b> {E(b)}</li>' for a, b in rows) + '</ul>'


def section(sid, title, chart, line='', det=''):
    return f'<section id="{E(sid)}"><h2>{E(title)}</h2><figure class="chart">{chart}</figure>' + (f'<p class="line">{E(line)}</p>' if line else '') + det + '</section>'


def decision_cards(open_dec, answered=(), prefix=''):
    """open_dec: [{id,title,why,options,recommended, src?}] -> section with cards, Use recommended / Copy choices / Export / Reset."""
    if not open_dec and not answered: return ''
    cards_h = ''.join(
        f'<article class="dec" data-id="{E(prefix + d["id"])}" data-rec="{E(d["recommended"])}"><div><h3>{E(d["title"])}</h3><p>{E(d.get("why", ""))}</p>'
        + (f'<p class="src"><a href="{E(d["src"])}">{E(d.get("src_label", "Open its page"))}</a></p>' if d.get('src') else '')
        + f'<p class="rec">Recommended: {E(d["recommended"])}</p></div><div class="choice"><label for="c-{E(prefix + d["id"])}">Your choice</label>'
        f'<select id="c-{E(prefix + d["id"])}"><option value="">Undecided</option>' + ''.join(f'<option>{E(x)}</option>' for x in d['options'])
        + f'</select><label for="n-{E(prefix + d["id"])}">Notes</label><textarea id="n-{E(prefix + d["id"])}" rows="2"></textarea></div></article>' for d in open_dec)
    tools = ('<div class="tools"><button type="button" class="use-rec">Use recommended</button><button type="button" id="dec-copy" class="pri">Copy choices</button>'
             '<button type="button" id="dec-json">Export JSON</button><button type="button" id="dec-reset" class="danger">Reset</button><span class="msg" role="status" aria-live="polite"></span></div>')
    ans = details(f'Already decided ({len(answered)})', dl([(d['title'], d['answer']) for d in answered])) if answered else ''
    n = len(open_dec)
    chart = meter(len(answered), len(answered) + n, f'{len(answered)} of {len(answered) + n} decided')
    return (f'<section id="decisions"><h2>Your calls <span class="chip k-bad" id="dec-badge">{n} open</span></h2><figure class="chart">{chart}</figure>'
            + (tools + cards_h if n else '<p class="line">Nothing waiting on you.</p>') + ans + '</section>')


# ---------- page ----------
FAV = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230b0c0e'/%3E"
       "%3Ccircle cx='16' cy='16' r='9' fill='none' stroke='%232fd69c' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='3' fill='%238f8bf0'/%3E%3C/svg%3E")

CSS = r'''
main{max-width:1080px}
.hero{margin:10px 0 30px}.hero .kick{font:12px var(--mono);color:var(--faint);text-transform:uppercase;letter-spacing:.08em;margin:0}
.hero h1{font-size:clamp(24px,3.6vw,34px);line-height:1.2;letter-spacing:-.01em;margin:8px 0 22px;max-width:30ch;text-wrap:balance}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(170px,100%),1fr));gap:12px}
.tile{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:16px 16px 14px;min-width:0}
.tile b .cnum{display:inline;font:inherit;color:inherit;margin:0}.tile b{display:block;font:650 clamp(28px,4vw,40px)/1.05 var(--sans);font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.tile span{display:block;color:var(--muted);font-size:13px;margin-top:6px}
.tile.t-bad b{color:#f08a85}.tile.t-ok b{color:var(--green)}.tile.t-warn b{color:var(--amber)}.tile.t-info b{color:#b9b6ff}
section{margin:30px 0;border-top:1px solid var(--line);padding-top:18px}
section>h2{display:flex;align-items:center;gap:10px}section>h2,.sec-toggle{font-size:13px}
.chart{margin:10px 0 6px;border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:16px}
.chart svg{display:block;width:100%;height:auto;overflow:visible}
.line{color:var(--text);font-size:15px;margin:10px 2px 0;max-width:70ch}
.cap{color:var(--muted);font-size:12px;margin:6px 0 0}
svg .lb,svg .m-l{fill:var(--muted);font:12px var(--sans)}svg .m-l{font-size:10.5px}svg .m-l.b{fill:var(--text)}
svg .vl,svg .m-v{fill:var(--text);font:600 12px var(--mono)}svg .m-v{font-size:10.5px}
svg .fv{fill:var(--text);font:650 22px var(--sans)}svg .fv.sm{font-size:14px}
svg .dn-n{fill:var(--text);font:650 24px var(--sans)}svg .dn-s{fill:var(--faint);font:10px var(--mono)}
.dwrap{display:flex;align-items:center;gap:24px;flex-wrap:wrap}.dwrap svg{width:150px;flex:none}
.leg{list-style:none;padding:0;margin:0;display:grid;gap:6px;color:var(--muted);font-size:13px}.leg.row{display:flex;flex-wrap:wrap;gap:16px;margin-top:8px}
.leg i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:8px;vertical-align:-1px}.leg b{color:var(--text);font-variant-numeric:tabular-nums}
.fcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(250px,100%),1fr));gap:12px;margin-top:12px}
.fc{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:14px;min-width:0;display:flex;flex-direction:column;gap:8px}
.fc-bad{border-color:#e2554f55}.fc-ok{opacity:.92}
.fc-top{display:flex;gap:8px;align-items:flex-start}.fc h3{font-size:14.5px;margin:0;line-height:1.3}
.fc p{margin:0;color:var(--muted);font-size:13px;line-height:1.45}
.fc svg.mini{width:100%;height:auto;display:block;margin:4px 0 0}
.chip{flex:none;display:inline-block;border-radius:999px;padding:2px 9px;font:600 11px var(--sans);border:1px solid var(--line);color:var(--muted)}
.k-ok{color:#86d6b8;border-color:#1fa57a90}.k-bad{color:#f6a19c;border-color:#e2554f90}.k-warn{color:var(--amber);border-color:#e0a84f90}.k-skip{color:var(--faint)}
details.det{margin-top:12px;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
details.det summary{cursor:pointer;padding:10px 14px;color:var(--muted);font-size:13px}details.det[open] summary{border-bottom:1px solid var(--line)}
.det-b{padding:8px 16px 12px;font-size:13px;color:var(--muted)}.det-b p{margin:8px 0}
.dlist{padding-left:18px;margin:6px 0}.dlist li{margin:6px 0}.dlist b{color:var(--text);font-weight:600}
.dec{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:16px;margin-top:12px}
.dec h3{font-size:15.5px}.dec p{margin:4px 0;color:var(--muted);font-size:13.5px}.dec .rec{color:#86d6b8}.dec.decided{border-color:#1fa57a}
.choice label{display:block;color:var(--muted);font-size:12px;margin:6px 0}
.choice select,.choice textarea{width:100%;min-height:44px;border:1px solid var(--line);border-radius:10px;padding:10px;background:var(--panel2);color:var(--text);font:inherit;color-scheme:dark}
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:12px}
.tools button,.rd button{min-height:40px;padding:8px 14px;border:1px solid var(--line);border-radius:10px;background:var(--panel2);color:var(--text);font:600 12.5px var(--sans);cursor:pointer}
.tools button:hover,.rd button:hover{border-color:var(--green)}.tools .pri{background:var(--green);border-color:var(--green);color:#06120d}.tools .danger{color:#f0a19d}
.msg,.rd-st{color:var(--muted);font-size:12.5px}
.rd{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:18px 0 0}
.rdk{margin-left:auto;display:inline-flex;align-items:center;gap:6px;color:var(--faint);font:500 12px var(--sans);text-transform:none;letter-spacing:0;cursor:pointer;flex:none}
.rdk input{accent-color:var(--green);width:16px;height:16px}
section.is-read>h2{opacity:.6}
.newlist{list-style:none;margin:10px 0 0;padding:0;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
.newlist li{display:grid;grid-template-columns:auto 118px minmax(0,1fr);gap:10px;align-items:start;padding:10px 14px;border-top:1px solid var(--line)}
.newlist li:first-child{border-top:0}.newlist li.is-read{opacity:.6}.newlist input{accent-color:var(--green);width:18px;height:18px;margin-top:3px}
.newlist b{display:block;font-size:14px}.newlist span.t{color:var(--muted);font-size:13.5px}.newlist .chip{justify-self:start}
.chip.k-info{background:rgba(160,130,255,.16);color:#c9b8ff;border-color:rgba(160,130,255,.4)}
.nl-g{margin:16px 0 4px;font:600 12px var(--mono);color:var(--faint);text-transform:uppercase;letter-spacing:.08em}
@media(max-width:650px){.newlist li{grid-template-columns:auto minmax(0,1fr)}.newlist li .chip{grid-column:2}.newlist li>div{grid-column:2}}
.rcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:14px}
.rcard{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:16px;min-width:0;display:flex;flex-direction:column;gap:10px;color:inherit;text-decoration:none}
.rcard .dwrap svg{width:120px}.rcard .kick{font:11px var(--mono);color:var(--faint);text-transform:uppercase;letter-spacing:.08em}.rcard:hover{border-color:var(--green)}.rcard h3{margin:0}.rcard p{margin:0;color:var(--muted);font-size:13px}.rcard svg{width:100%;height:auto}
.grow{transform-box:fill-box;transform-origin:left center;transition:transform .45s ease-out,opacity .4s}
.pre .grow{transform:scaleX(0);opacity:.3}
.draw{stroke-dasharray:1;stroke-dashoffset:0;transition:stroke-dashoffset .6s ease-out}.pre .draw{stroke-dashoffset:1}
@media(max-width:650px){.dec{grid-template-columns:minmax(0,1fr)}.chart{padding:12px}.hero h1{font-size:24px}.tile b{font-size:28px}.rdk span{display:none}}
@media(prefers-reduced-motion:reduce){.pre .grow{transform:none;opacity:1}.pre .draw{stroke-dashoffset:0}}
'''

JS = r'''<script>(function(){var d=document,PG=%PAGE%,PRE=%READ%,API='http://127.0.0.1:18990/api/page-read';
/* reveal: charts grow in once, numbers count up */
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches,figs=[].slice.call(d.querySelectorAll('.chart,.fc,.rcard'));
function cnt(n){var to=parseFloat(n.dataset.to),dec=(n.dataset.to.split('.')[1]||'').length,t0=performance.now();(function f(t){var p=Math.min(1,(t-t0)/650);n.textContent=(to*(1-Math.pow(1-p,3))).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});if(p<1)requestAnimationFrame(f)})(t0)}
if(!rm&&'IntersectionObserver' in window){figs.forEach(function(e){e.classList.add('pre')});var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.remove('pre');io.unobserve(e.target)}})},{rootMargin:'0px 0px 5% 0px'});figs.forEach(function(e){io.observe(e)});d.querySelectorAll('.tile .cnum').forEach(cnt)}
/* read marks: one tick per section, saved to the Run Dashboard (and this browser) */
var RK='read:'+PG,S=[];try{S=JSON.parse(localStorage.getItem(RK)||'[]')}catch(e){}PRE.forEach(function(t){if(S.indexOf(t)<0)S.push(t)});
var secs=[].slice.call(d.querySelectorAll('main>section[id]')).filter(function(s){return s.querySelector(':scope>h2')&&s.id!=='decisions'});
function st(m){var e=d.getElementById('rd-st');if(e)e.textContent=m}
/* item ticks (page-update New lists): same read list as the sections */
var its=[].slice.call(d.querySelectorAll('.newlist input[data-t]'));
function title(s){if(s.dataset.title)return s.dataset.title;var h=s.querySelector(':scope>h2').cloneNode(true);h.querySelectorAll('.chip,.rdk,.chev').forEach(function(x){x.remove()});return h.textContent.trim()}
function paint(){secs.forEach(function(s){var on=S.indexOf(title(s))>=0;s.classList.toggle('is-read',on);var b=s.querySelector('.rdk input');if(b)b.checked=on});its.forEach(function(b){var on=S.indexOf(b.dataset.t)>=0;b.checked=on;var li=b.closest('li');if(li)li.classList.toggle('is-read',on)})}
function push(){try{localStorage.setItem(RK,JSON.stringify(S))}catch(e){}fetch(API,{method:'POST',headers:{'content-type':'text/plain'},body:JSON.stringify({page:PG,read:S})}).then(function(r){st(r.ok?'Saved.':'Not saved: Run Dashboard said '+r.status+'. Use Copy read marks.')},function(){st('Not saved: Run Dashboard is not running. Use Copy read marks.')})}
secs.forEach(function(s){s.dataset.title=title(s);var h=s.querySelector(':scope>h2'),l=d.createElement('label');l.className='rdk';l.innerHTML='<input type="checkbox"><span>Read</span>';
 l.querySelector('input').addEventListener('change',function(e){var t=s.dataset.title,i=S.indexOf(t);if(e.target.checked&&i<0)S.push(t);if(!e.target.checked&&i>=0)S.splice(i,1);paint();push()});h.appendChild(l)});
its.forEach(function(b){b.addEventListener('change',function(){var t=b.dataset.t,i=S.indexOf(t);if(b.checked&&i<0)S.push(t);if(!b.checked&&i>=0)S.splice(i,1);paint();push()})});
fetch(API+'?page='+encodeURIComponent(PG)).then(function(r){return r.json()}).then(function(j){(j.read||[]).forEach(function(t){if(S.indexOf(t)<0)S.push(t)});paint()}).catch(function(){});paint();
var ra=d.getElementById('rd-all');if(ra)ra.onclick=function(){secs.forEach(function(s){if(S.indexOf(s.dataset.title)<0)S.push(s.dataset.title)});its.forEach(function(b){if(S.indexOf(b.dataset.t)<0)S.push(b.dataset.t)});paint();push()};
var rc=d.getElementById('rd-copy');if(rc)rc.onclick=function(){var t='Page read marks for '+PG+': '+JSON.stringify({read:S});(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){st('Copied. Paste it to the agent.')},function(){st(t)})};
/* decision cards */
var K='dec:'+PG,decs=[].slice.call(d.querySelectorAll('.dec'));function ld(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return {}}}
function badge(){var b=d.getElementById('dec-badge');var n=decs.filter(function(a){return !a.querySelector('select').value}).length;decs.forEach(function(a){a.classList.toggle('decided',!!a.querySelector('select').value)});if(b)b.textContent=n?n+' open':'all answered'}
function save(){var s={};decs.forEach(function(a){s[a.dataset.id]={choice:a.querySelector('select').value,note:a.querySelector('textarea').value}});try{localStorage.setItem(K,JSON.stringify(s))}catch(e){}badge();return s}
var s0=ld();decs.forEach(function(a){var v=s0[a.dataset.id];if(v){a.querySelector('select').value=v.choice||'';a.querySelector('textarea').value=v.note||''}a.addEventListener('change',save);a.addEventListener('input',save)});badge();
function say(m){d.querySelectorAll('.msg').forEach(function(x){x.textContent=m})}
function md(){var s=save(),o=['# '+d.title+' - decisions','',PG,''];decs.forEach(function(a){var v=s[a.dataset.id];o.push('### '+a.dataset.id+' - '+a.querySelector('h3').textContent,'Choice: '+(v.choice||'Undecided'),'Notes: '+(v.note||'-'),'')});return o.join('\n')}
var c=d.getElementById('dec-copy');if(c)c.onclick=function(){var t=md();(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){say('Copied. Paste it back to the agent.')},function(){say('Copy failed; use Export JSON.')})};
var j=d.getElementById('dec-json');if(j)j.onclick=function(){var b=new Blob([JSON.stringify(save(),null,1)],{type:'application/json'}),u=URL.createObjectURL(b),a=d.createElement('a');a.href=u;a.download=PG.split('/').pop().replace('.html','')+'-decisions.json';a.click();URL.revokeObjectURL(u)};
var r=d.getElementById('dec-reset');if(r)r.onclick=function(){if(!confirm('Clear your answers on this page?'))return;try{localStorage.removeItem(K)}catch(e){}decs.forEach(function(a){a.querySelector('select').value='';a.querySelector('textarea').value=''});badge();say('Cleared.')};
d.querySelectorAll('.use-rec').forEach(function(b){b.onclick=function(){var n=0;decs.forEach(function(a){var sel=a.querySelector('select');if(!sel.value){sel.value=a.dataset.rec;if(sel.value)n++}});save();say(n?'Filled '+n+' recommended answer'+(n==1?'':'s')+'.':'Every question already has an answer.')}});
})();</script>'''


def read_marks(page):
    try: return json.load(open(f'{PROJECTS}/plans/_run-dashboard/data/page-read.json')).get(page, {}).get('read', [])
    except Exception: return []


def page(out, title, kicker, verdict, tiles_items, sections_html, nav, date, summary=None):
    """Write the page. nav: [(href, label)]. summary: dict written to <out>.summary.json for the review-all index."""
    out = os.path.abspath(os.path.expanduser(out)); rel = os.path.relpath(out, PROJECTS)
    theme = subprocess.run(['python3', f'{HOME}/.claude/skills/theme/theme.py', 'css', 'orbit-ledger'], capture_output=True, text=True, check=True).stdout
    coll = re.sub(r'<!--.*?-->', '', open(f'{HOME}/.agents/skills/design-all/collapsible.html').read(), flags=re.S)
    cst = re.search(r'<style id="collapsible">.*?</style>', coll, re.S)[0]; csc = re.search(r'<script>.*?</script>', coll, re.S)[0]
    navh = ''.join(f'<a href="{E(h)}">{E(l)}</a>' for h, l in nav)
    js = JS.replace('%PAGE%', json.dumps(rel)).replace('%READ%', json.dumps(read_marks(rel)))
    rd = ('<div class="rd"><button type="button" id="rd-all">Mark all read</button><button type="button" id="rd-copy">Copy read marks</button>'
          '<span class="rd-st" id="rd-st" role="status" aria-live="polite"></span></div>')
    h = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><link rel="icon" type="image/svg+xml" href="{FAV}">
<style id="theme" data-theme="orbit-ledger">{theme}</style>{cst}<style id="review-kit">{CSS}</style></head><body>
<header><div class="bar"><h1>{E(title)}</h1><span class="stamp">{E(date)}</span></div><nav>{navh}</nav></header>
<main><div class="hero" id="top"><p class="kick">{E(kicker)}</p><h1>{E(verdict)}</h1>{tiles(tiles_items)}{rd}</div>
{sections_html}</main>{csc}{js}</body></html>'''
    os.makedirs(os.path.dirname(out), exist_ok=True); open(out, 'w', encoding='utf-8').write(h)
    home = os.path.relpath(f'{PROJECTS}/plans/index.html', os.path.dirname(out))
    subprocess.run(['node', f'{HOME}/.agents/skills/design-all/scroll-perf.mjs', '--home', home, out], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['python3', f'{HOME}/.claude/skills/theme/theme.py', 'fix-chars', out], check=True, stdout=subprocess.DEVNULL)
    if summary is not None:
        summary = dict(summary, page=rel, title=title, verdict=verdict, date=date)
        json.dump(summary, open(re.sub(r'\.html$', '', out) + '.summary.json', 'w'), indent=1)
    return out
