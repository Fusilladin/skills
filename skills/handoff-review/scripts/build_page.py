#!/usr/bin/env python3
"""build_page.py - turn <work>/final-review.json + stops.json into the weekly handoff review page.

  python3 build_page.py --work <workdir> --out ~/dev/projects/plans/_reports/handoff-review-YYYY-MM-DD.html

human-summary render (orbit-ledger, decision cards for open owner calls) -> <main> replaced with: verdict +
fix-status donut, stops-per-day chart, round outcomes waffle, fixes board (status, impact, effort), open decisions,
closed panels (answered decisions, rejected claims). Then collapsible, scroll-perf, fix-chars, and a copy to
_reports/handoff-review-latest.html (the Observatory "Handoff review" button opens that).
"""
import argparse, html, json, os, re, shutil, subprocess
ap = argparse.ArgumentParser(); ap.add_argument('--work', required=True); ap.add_argument('--out', required=True)
a = ap.parse_args(); OUT = os.path.expanduser(a.out); PLANS = os.path.expanduser('~/projects/plans'); HERE = os.path.dirname(os.path.abspath(__file__))
fr = json.load(open(f'{a.work}/final-review.json')); st = json.load(open(f'{a.work}/stops.json')).get('stopStats') or {}
E = lambda s: html.escape(str(s), quote=True)
openq = [d for d in fr.get('decisions', []) if not d.get('answer')]; answered = [d for d in fr.get('decisions', []) if d.get('answer')]
content = {'title': f'Handoff review ({fr["window"].replace("..", " to ")})', 'project': 'plans', 'summary': fr['summary'],
           'needs_human': [{'title': d['title'], 'detail': d['why']} for d in openq], 'decisions': openq,
           'artifacts': [{'label': 'Run observatory', 'path': '_observatory/index.html', 'note': 'Optimize tab: the handoff tip.'}]}
json.dump(content, open(f'{a.work}/content.json', 'w'), indent=1)
env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.expanduser('~/projects'))
subprocess.run(['python3', os.path.expanduser('~/.claude/skills/human-summary/render.py'), 'render', f'{a.work}/content.json', '-o', OUT,
                '--theme', 'orbit-ledger', '--root', PLANS], check=True, cwd=PLANS, env=env, stdout=subprocess.DEVNULL)
h = open(OUT, encoding='utf-8').read()
# fix-status donut
fx = fr.get('fixes', []); cnt = {k: sum(f['status'] == k for f in fx) for k in ('done', 'open', 'none')}
C = 2 * 3.14159 * 40; off = 0; arcs = ''
for k, col in (('done', 'var(--green)'), ('open', 'var(--red)'), ('none', 'var(--purple)')):
    L = C * cnt[k] / max(len(fx), 1); arcs += f'<circle r="40" cx="50" cy="50" fill="none" stroke="{col}" stroke-width="14" stroke-dasharray="{L:.1f} {C - L:.1f}" stroke-dashoffset="{-off:.1f}"/>'; off += L
donut = f'<svg viewBox="0 0 100 100" width="120" height="120" role="img" aria-label="{cnt["done"]} done, {cnt["open"]} open" style="transform:rotate(-90deg)"><circle r="40" cx="50" cy="50" fill="none" stroke="var(--panel2)" stroke-width="14"/>{arcs}</svg>'
nb = fr.get('numbers', {})
lead = f'''<section id="verdict"><h2>Verdict</h2><div class="newtop">{donut}<div><p class="big">{E(fr["verdict"])}</p><p class="muted">{nb.get("rounds", "?")} rounds, {nb.get("launches", "?")} launches. {nb.get("stops", 0)} stops: {nb.get("noted", 0)} with a note, {nb.get("unnoted", 0)} without, {nb.get("late", 0)} late. Fixes: {cnt["done"]} done, {cnt["open"]} open.</p></div></div>''' + ''.join(f'<p class="muted">{E(p)}</p>' for p in fr['summary']) + '</section>'
# stops per day
days = st.get('daily', [])[-10:]; mx = max([d['noted'] + d['unnoted'] + d['late'] for d in days] + [1]); cols = ''
for d in days:
    seg = lambda v, c: f'<span class="seg {c}" style="height:{100 * v / mx:.2f}%"></span>' if v else ''
    cols += f'<div class="col"><span class="tot">{d["noted"] + d["unnoted"] + d["late"]}</span><div class="stack">{seg(d["late"], "s-miss")}{seg(d["unnoted"], "s-bad")}{seg(d["noted"], "s-ok")}</div><span class="dl">{d["date"][5:]}</span></div>'
daychart = f'''<section id="days"><h2>Stops per day</h2><figure class="chart daychart"><div class="cols" style="grid-template-columns:repeat({max(len(days), 1)},minmax(0,1fr))">{cols}</div><div class="legend"><span><i class="s-ok"></i>With a note</span><span><i class="s-bad"></i>No note</span><span><i class="s-miss"></i>Late (outputs complete, nothing lost)</span></div><figcaption>One row per round per day, from the Observatory detector (blockers.mjs). The detector looks back 7 days.</figcaption></figure></section>'''
# outcomes waffle
WC = {'ok': 'w-ok', 'note': 'w-note', 'warn': 'w-warn'}
cells = ''.join(f'<span class="{WC.get(o["kind"], "w-ok")}"></span>' for o in fr.get('outcomes', []) for _ in range(o['n']))
wl = ''.join(f'<li><i class="{WC.get(o["kind"], "w-ok")}"></i><b>{o["n"]}</b> {E(o["label"])}</li>' for o in fr.get('outcomes', []))
nq, rf = fr.get('note_quality', {}), fr.get('retry_found', {})
waffle = f'''<section id="rounds"><h2>Every round this week</h2><figure class="chart"><div class="waffle">{cells}</div><ul class="wleg">{wl}</ul><figcaption>One square per round. Notes: {nq.get("good", 0)} good, {nq.get("thin", 0)} thin, {nq.get("wrong", 0)} wrong. Retries found the note: {rf.get("prompt", 0)} through the prompt, {rf.get("chance", 0)} by chance, {rf.get("never", 0)} never.</figcaption></figure></section>'''
CH = {'done': ('Done', 'ch-done'), 'open': ('Open', 'ch-open'), 'none': ('No change', 'ch-none')}
order = sorted(fx, key=lambda f: ({'open': 0, 'none': 1, 'done': 2}[f['status']], -f.get('impact', 0)))
rows = ''.join(f'<div class="fx"><span class="chip {CH[f["status"]][1]}">{CH[f["status"]][0]}</span><div><b>{E(f["name"])}</b><p>{E(f["text"])}</p></div><span class="track"><span class="hb b-acc" style="--w:{f.get("impact", 1) / 10:.2f}"></span></span><span class="chip">{E(f.get("effort", "?"))}</span></div>' for f in order)
fixes = f'<section id="fixes"><h2>Fixes</h2><p class="muted">Open first, then by impact (bar). Last chip is effort.</p><div class="fxbox chart">{rows or "<p>None.</p>"}</div></section>'
m = re.search(r'<main>(.*)</main>', h, re.S); body = m.group(1)
dec = (re.search(r'<section id="decisions">.*?</section>(?:<script>.*?</script>)*', body, re.S) or [''])[0] if openq else ''
rej = ''.join(f'<li><span class="chip ch-none">{E(r["result"])}</span><div><b>{E(r["claim"])}</b> {E(r["why"])}</div></li>' for r in fr.get('rejected', []))
ans = ''.join(f'<li><span class="chip ch-done">Done</span><div><b>{E(d["title"])}</b> {E(d["answer"])}</div></li>' for d in answered)
folded = '<section id="more"><h2>Details</h2>' + (f'<details class="done-dec"><summary>Your decisions ({len(answered)} answered)</summary><ul class="newlist">{ans}</ul></details>' if answered else '') \
    + (f'<details class="done-dec"><summary>Haiku claims that did not hold ({len(fr.get("rejected", []))})</summary><ul class="newlist">{rej}</ul></details>' if rej else '') + '</section>'
h = h[:m.start()] + '<main>' + lead + fixes + dec + daychart + waffle + folded + '</main>' + h[m.end():]
h = re.sub(r'<nav>.*?</nav>', '<nav><a href="#verdict">Verdict</a><a href="#fixes">Fixes</a>' + ('<a href="#decisions">Decide</a>' if openq else '') + '<a href="../_observatory/index.html">Run Observatory</a><a href="../index.html">Plans</a></nav>', h, count=1, flags=re.S)
if not openq: h = re.sub(r'<span class="status" id="dec-badge">.*?</span>', '', h)
coll = open(os.path.expanduser('~/.agents/skills/design-all/collapsible.html')).read()
h = h.replace('</head>', '<style id="page">' + open(f'{HERE}/page.css').read() + '</style>' + re.search(r'<style id="collapsible">.*?</style>', coll, re.S)[0] + '</head>', 1)
reveal = "(()=>{const els=document.querySelectorAll('.chart');if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches){els.forEach(e=>e.classList.add('reveal-on'));return}const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('reveal-on');io.unobserve(e.target)}}),{rootMargin:'0px 0px 5% 0px'});els.forEach(e=>io.observe(e))})();"
h = h.replace('</body>', re.search(r'<script>\(\(\)=>\{.*?</script>', coll, re.S)[0] + f'<script>{reveal}</script></body>', 1)
open(OUT, 'w', encoding='utf-8').write(h)
subprocess.run(['node', os.path.expanduser('~/.agents/skills/design-all/scroll-perf.mjs'), '--home', '../index.html', OUT], cwd=PLANS, check=False, stdout=subprocess.DEVNULL)
subprocess.run(['python3', os.path.expanduser('~/.claude/skills/theme/theme.py'), 'fix-chars', OUT], check=False, stdout=subprocess.DEVNULL)
shutil.copy(OUT, os.path.join(os.path.dirname(OUT), 'handoff-review-latest.html'))
print('wrote', OUT, '+ handoff-review-latest.html')
