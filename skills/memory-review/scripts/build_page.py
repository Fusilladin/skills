#!/usr/bin/env python3
"""memory-review page builder: findings.json -> self-contained frame-budget HTML.

Usage: python3 build_page.py --work DIR --out PAGE.html
findings.json (in DIR):
{
 "title": "Memory review", "date": "2026-11-10", "lead": "one plain sentence",
 "hero": {"value": 4.2, "unit": "GB", "text": "RAM held up at the worst points measured."},
 "findings": [{"id": "observatory", "name": "Observatory server", "verdict": "leak|held|pileup|normal",
   "worst_mb": 2200, "after_mb": 315, "lede": "...", "stats": [["2.2 GB", "38 s after restart"]],
   "why": "...", "code": "diff text (optional)", "fix": "..."}],
 "context": "optional aside (e.g. Strata 35 GB, expected)",
 "trend": [{"date": "2026-11-03", "available_mb": 46433}],   # optional, from snapshots
 "decisions": [{"id": "snake_case", "title": "...", "why": "plain, non-technical",
   "options": ["Apply now", "Skip"], "recommended": "Apply now", "answer": null}],
 "fixes": [{"title": "...", "state": "done|open", "note": "..."}]
}
Answered decisions fold into a closed panel; the badge hides when nothing is open.
"""
import argparse, html, json, os, re, subprocess

E = html.escape
VERD = {'leak': ('Leak', 'cost'), 'held': ('Held, not freed', 'cost'), 'pileup': ('Piling up', 'cost'), 'normal': ('Normal', 'fast')}

def gb(mb): return f'{mb/1000:.1f} GB' if mb >= 1000 else f'{mb:.0f} MB'

def bars(fs):
    fs = [f for f in fs if f.get('worst_mb')]
    if not fs: return ''
    mx = max(f['worst_mb'] for f in fs) * 1.15
    W, rh, lw = 640, 56, 170
    out = []
    for i, f in enumerate(fs):
        y = 18 + i * rh
        bw = (W - lw - 90) * f['worst_mb'] / mx
        out.append(f'<text class="rl" x="0" y="{y+13}">{E(f["name"])}</text>'
                   f'<rect class="bb" x="{lw}" y="{y}" width="{bw:.1f}" height="14" rx="3"/>'
                   f'<text class="rv" x="{lw+bw+8:.1f}" y="{y+12}">{gb(f["worst_mb"])}</text>')
        if f.get('after_mb') is not None:
            aw = max(3, (W - lw - 90) * f['after_mb'] / mx)
            out.append(f'<rect class="ab" x="{lw}" y="{y+18}" width="{aw:.1f}" height="14" rx="3"/>'
                       f'<text class="rv a" x="{lw+aw+8:.1f}" y="{y+30}">{gb(f["after_mb"])}</text>')
    return (f'<div class="chart"><svg viewBox="0 0 {W} {18+len(fs)*rh}" role="img" aria-label="RAM per finding, worst seen and after fix">{"".join(out)}</svg>'
            '<div class="keyrow"><span><i class="k" style="background:var(--purple)"></i>worst seen</span><span><i class="k" style="background:var(--green)"></i>after fix</span></div></div>')

def trend(t):
    if not t or len(t) < 2: return ''
    W, H, l, b = 640, 170, 52, 26
    mx = max(x['available_mb'] for x in t) * 1.1
    step = (W - l - 20) / (len(t) - 1)
    pts = [(l + i * step, 12 + (H - 12 - b) * (1 - x['available_mb'] / mx)) for i, x in enumerate(t)]
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    lab = ''.join(f'<text class="sx" x="{x:.1f}" y="{H-6}" text-anchor="middle">{E(t[i]["date"][5:])}</text>' for i, (x, y) in enumerate(pts))
    dots = ''.join(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="3.5"><title>{t[i]["date"]}: {gb(t[i]["available_mb"])}</title></circle>' for i, (x, y) in enumerate(pts))
    return (f'<div class="chart"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Available RAM at each weekly check">'
            f'<path class="line" pathLength="1" d="{d}"/>{dots}{lab}</svg></div><p class="cap">Available RAM at each weekly check.</p>')

def main():
    a = argparse.ArgumentParser(); a.add_argument('--work', required=True); a.add_argument('--out', required=True); o = a.parse_args()
    c = json.load(open(os.path.join(o.work, 'findings.json')))
    theme = subprocess.run(['python3', os.path.expanduser('~/.claude/skills/theme/theme.py'), 'css', 'frame-budget'], capture_output=True, text=True, check=True).stdout
    css = open(os.path.join(os.path.dirname(__file__), 'page.css')).read()
    coll = re.sub(r'<!--.*?-->', '', open(os.path.expanduser('~/.agents/skills/design-all/collapsible.html')).read(), flags=re.S)
    cst = re.search(r'<style id="collapsible">.*?</style>', coll, re.S).group(0)
    csc = re.search(r'<script[^>]*>.*?</script>', coll, re.S).group(0)
    open_dec = [d for d in c.get('decisions', []) if not d.get('answer')]
    done_dec = [d for d in c.get('decisions', []) if d.get('answer')]
    fixes = c.get('fixes', [])
    nav = ['<a href="#top">Summary</a>'] + [f'<a href="#{E(f["id"])}">{E(f["name"])}</a>' for f in c['findings']]
    if open_dec: nav.append('<a href="#decisions">Decisions</a>')
    if fixes or done_dec: nav.append('<a href="#done">Done</a>')
    h = c.get('hero') or {}
    secs = []
    for f in c['findings']:
        vl, vc = VERD.get(f.get('verdict', 'normal'), VERD['normal'])
        stats = ''.join(f'<div><b>{E(s[0])}</b><span>{E(s[1])}</span></div>' for s in f.get('stats', []))
        code = f'<pre class="code">{E(f["code"])}</pre>' if f.get('code') else ''
        secs.append(f'<section id="{E(f["id"])}"><h2>{E(f["name"])} <span class="chip {vc}">{vl}</span></h2>'
                    f'<p class="lede">{E(f.get("lede", ""))}</p>' + (f'<div class="stats">{stats}</div>' if stats else '')
                    + (f'<h3>Why</h3><p>{E(f["why"])}</p>' if f.get('why') else '') + code
                    + (f'<h3>The fix</h3><p>{E(f["fix"])}</p>' if f.get('fix') else '') + '</section>')
    dcards = ''.join(
        f'<article class="dec" data-id="{E(d["id"])}" data-rec="{E(d["recommended"])}"><div><h3>{E(d["title"])}</h3><p>{E(d.get("why", ""))}</p>'
        f'<p class="rec"><b>Recommended:</b> {E(d["recommended"])}</p></div><div class="choice"><label for="c-{E(d["id"])}">Your choice</label>'
        f'<select id="c-{E(d["id"])}"><option value="">Undecided</option>' + ''.join(f'<option>{E(x)}</option>' for x in d['options'])
        + f'</select><label for="n-{E(d["id"])}">Notes</label><textarea id="n-{E(d["id"])}" rows="2"></textarea></div></article>' for d in open_dec)
    tools = ('<div class="tools"><button type="button" class="use-rec">Use recommended</button><button type="button" id="copy">Copy choices</button>'
             '<button type="button" id="json">Export JSON</button><button type="button" id="reset" class="danger">Reset</button><span class="msg" role="status" aria-live="polite"></span></div>')
    dec_html = (f'<section id="decisions"><h2>Decisions <span class="chip cost" id="badge">{len(open_dec)} open</span></h2>'
                f'<p class="muted">Pick an answer, then Copy choices and paste it back. Choices save in this browser.</p>{tools}{dcards}'
                '<div class="tools"><button type="button" class="use-rec">Use recommended</button><span class="msg" role="status" aria-live="polite"></span></div></section>') if open_dec else ''
    done_html = ''
    if fixes or done_dec:
        fl = ''.join(f'<li><span class="chip {"fast" if x["state"]=="done" else "cost"}">{"Done" if x["state"]=="done" else "Open"}</span><div><b>{E(x["title"])}</b><p>{E(x.get("note", ""))}</p></div></li>' for x in fixes)
        dl = ''.join(f'<li><span class="chip fast">Done</span><div><b>{E(d["title"])}</b><p>{E(d["answer"])}</p></div></li>' for d in done_dec)
        done_html = ('<section id="done"><h2>Done</h2>'
                     + (f'<details class="fold"><summary>Fixes ({sum(x["state"]=="done" for x in fixes)} done, {sum(x["state"]!="done" for x in fixes)} open)</summary><ul class="list">{fl}</ul></details>' if fixes else '')
                     + (f'<details class="fold"><summary>Decisions already made ({len(done_dec)})</summary><ul class="list">{dl}</ul></details>' if done_dec else '') + '</section>')
    js = r'''<script>(function(){var K='memrev:'+location.pathname;function st(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return {}}}
function save(){var s={};document.querySelectorAll('.dec').forEach(function(a){var id=a.dataset.id;s[id]={c:a.querySelector('select').value,n:a.querySelector('textarea').value}});try{localStorage.setItem(K,JSON.stringify(s))}catch(e){}badge();return s}
function badge(){var b=document.getElementById('badge');if(!b)return;var n=[].filter.call(document.querySelectorAll('.dec select'),function(x){return !x.value}).length;b.textContent=n?n+' open':'all answered'}
var s0=st();document.querySelectorAll('.dec').forEach(function(a){var v=s0[a.dataset.id];if(v){a.querySelector('select').value=v.c||'';a.querySelector('textarea').value=v.n||''}a.addEventListener('change',save);a.addEventListener('input',save)});badge();
function say(m){document.querySelectorAll('.msg').forEach(function(x){x.textContent=m})}
function md(){var s=save(),o=['# '+document.title+' - decisions','','Updated: '+new Date().toISOString(),''];document.querySelectorAll('.dec').forEach(function(a){var v=s[a.dataset.id];o.push('### '+a.dataset.id+' - '+a.querySelector('h3').textContent,'Choice: '+(v.c||'Undecided'),'','Notes: '+(v.n||'-'),'')});return o.join('\n')}
function copy(t){if(navigator.clipboard)navigator.clipboard.writeText(t).then(function(){say('Copied. Paste it back to the agent.')},function(){fb(t)});else fb(t)}
function fb(t){var x=document.createElement('textarea');x.value=t;document.body.appendChild(x);x.select();try{document.execCommand('copy');say('Copied.')}catch(e){say('Copy failed; select the text manually.')}x.remove()}
var c=document.getElementById('copy');if(c)c.onclick=function(){copy(md())};
var j=document.getElementById('json');if(j)j.onclick=function(){var b=new Blob([JSON.stringify(save(),null,1)],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='memory-review-decisions.json';a.click();URL.revokeObjectURL(u)};
var r=document.getElementById('reset');if(r)r.onclick=function(){if(!confirm('Clear your answers on this page?'))return;try{localStorage.removeItem(K)}catch(e){}document.querySelectorAll('.dec select').forEach(function(x){x.value=''});document.querySelectorAll('.dec textarea').forEach(function(x){x.value=''});badge();say('Cleared.')};
document.querySelectorAll('.use-rec').forEach(function(b){b.onclick=function(){var n=0;document.querySelectorAll('.dec').forEach(function(a){var sel=a.querySelector('select');if(!sel.value){sel.value=a.dataset.rec;if(sel.value)n++}});save();say(n?'Applied '+n+' recommended answer'+(n==1?'':'s')+'.':'Every question already has an answer.')}});
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches,ss=[].slice.call(document.querySelectorAll('main section, main .hero'));function go(e){e.classList.add('in');var n=e.querySelector('.num');if(n&&!n.dataset.done){n.dataset.done=1;var to=+n.dataset.to,d=+n.dataset.dec;if(rm)return;var t0=performance.now();(function f(t){var p=Math.min(1,(t-t0)/700);n.textContent=(to*(1-Math.pow(1-p,3))).toFixed(d);if(p<1)requestAnimationFrame(f)})(t0)}}
if(rm||!('IntersectionObserver' in window))ss.forEach(go);else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){go(e.target);io.unobserve(e.target)}})},{rootMargin:'0px 0px 5% 0px'});ss.forEach(function(e){io.observe(e)})}})();</script>'''
    hv = h.get('value', 0); dec = 1 if isinstance(hv, float) else 0
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(c["title"])}</title><link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
<style id="theme" data-theme="frame-budget">{theme}</style>{cst}<style id="memrev">{css}</style></head><body>
<header><div class="bar"><h1>{E(c["title"])}</h1>{f'<span class="chip cost">{len(open_dec)} to decide</span>' if open_dec else ''}<span class="stamp">{E(c.get("date",""))}</span></div>
<nav>{"".join(nav)}<details><summary>Related</summary><div class="menu"><a href="../_observatory/index.html">Run Observatory</a><a href="../index.html">Plans</a></div></details></nav></header>
<main><div class="hero" id="top"><p class="eyebrow">Weekly memory check &middot; {E(c.get("date",""))}</p><h1 class="hero-h">{E(c.get("lead",""))}</h1>
<div class="big"><span class="num" data-to="{hv}" data-dec="{dec}">{hv}</span><span class="unit">{E(h.get("unit","GB"))}</span><p>{E(h.get("text",""))}</p></div></div>
<section id="where"><h2>Where the RAM goes</h2>{bars(c["findings"])}{trend(c.get("trend"))}{f'<p class="aside">{E(c["context"])}</p>' if c.get("context") else ""}</section>
{"".join(secs)}{dec_html}{done_html}</main>{js}{csc}</body></html>'''
    os.makedirs(os.path.dirname(os.path.abspath(o.out)), exist_ok=True)
    open(o.out, 'w').write(page)
    home = os.path.relpath(os.path.expanduser('~/dev/projects/plans/index.html'), os.path.dirname(os.path.abspath(o.out)))
    subprocess.run(['node', os.path.expanduser('~/.agents/skills/design-all/scroll-perf.mjs'), '--home', home, o.out], check=True)
    subprocess.run(['python3', os.path.expanduser('~/.claude/skills/theme/theme.py'), 'fix-chars', o.out], check=True)
    print(o.out)

if __name__ == '__main__':
    main()
