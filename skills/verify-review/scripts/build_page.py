#!/usr/bin/env python3
"""build_page.py - turn <work>/final-review.json + verify-data.json into the weekly verify review page.

  python3 build_page.py --work <workdir> --out ~/dev/projects/plans/_reports/verify-review-YYYY-MM-DD.html

Steps: human-summary render (neon-ops, decision cards for open owner calls) -> replace <main> with
data sections (inline SVG charts) -> collapsible sections -> scroll-perf -> theme fix-chars.
Decisions already answered (decisions[].answer set) are folded into a closed "Your decisions" panel.
"""
import argparse, html, json, os, re, subprocess
from collections import Counter

ap = argparse.ArgumentParser(); ap.add_argument('--work', required=True); ap.add_argument('--out', required=True)
a = ap.parse_args()
OUT = os.path.expanduser(a.out); PLANS = os.path.expanduser('~/projects/plans')
fr = json.load(open(f'{a.work}/final-review.json')); rows = json.load(open(f'{a.work}/verify-data.json'))
E = lambda s: html.escape(str(s), quote=True)
N = len(rows); oc = fr['outcomes']
openq = [d for d in fr.get('decisions', []) if not d.get('answer')]
answered = [d for d in fr.get('decisions', []) if d.get('answer')]

# 1. base page from human-summary
fixes_all = [i for g in fr.get('fixes', []) for i in g['items']]
content = {
    'title': f'Verify jobs: weekly review ({fr["window"].replace("..", " to ")})', 'project': 'plans', 'summary': fr['summary'],
    'status': [{'value': str(N), 'label': f'verify runs, {len({r["project"] for r in rows})} plans', 'state': 'info'},
               {'value': f'{oc["built"]} / {oc["partial"]} / {oc["failed"]}', 'label': 'built / partial / failed', 'state': 'info'},
               {'value': str(sum(i['status'] == 'done' for i in fixes_all)), 'label': 'fixes done', 'state': 'done'},
               {'value': str(sum(i['status'] == 'open' for i in fixes_all)), 'label': 'fixes open', 'state': ''}],
    'needs_human': [{'title': d['title'], 'detail': d['why']} for d in openq], 'decisions': openq,
    'artifacts': [{'label': 'Run observatory', 'path': '_observatory/index.html', 'note': 'Where the per-job records came from.'}],
    'nav_groups': [{'label': 'Plans', 'pages': [{'path': 'index.html', 'label': 'Plans home'}, {'path': '_observatory/index.html', 'label': 'Run observatory'}]}],
}
json.dump(content, open(f'{a.work}/content.json', 'w'), indent=1)
env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.expanduser('~/projects'))
subprocess.run(['python3', os.path.expanduser('~/.claude/skills/human-summary/render.py'), 'render', f'{a.work}/content.json',
                '-o', OUT, '--theme', 'neon-ops', '--root', PLANS], check=True, cwd=PLANS, env=env, stdout=subprocess.DEVNULL)
base = open(OUT, encoding='utf-8').read()

# 2. charts
def svg_hbars(items, unit='', label=''):
    mx = max([v for _, v, _ in items] + [1]); g = ''
    for i, (l, v, c) in enumerate(items):
        y = 8 + i * 40; w = max(2, 290 * v / mx)
        g += (f'<text class="sv-l" x="0" y="{y + 10}">{E(l)}</text><rect class="sv-b {c}" x="0" y="{y + 16}" width="{w:.1f}" height="12" rx="3"/>'
              f'<text class="sv-v" x="{w + 6:.1f}" y="{y + 26.5}">{v}{unit}</text>')
    return f'<svg class="sv" viewBox="0 0 360 {8 + len(items) * 40}" role="img" aria-label="{E(label)}">{g}</svg>'
def donut(parts, label, word='runs'):
    tot = sum(v for _, v, _ in parts) or 1; C = 2 * 3.14159265 * 42; off = 0; g = ''
    for n, v, c in parts:
        L = C * v / tot
        g += f'<circle class="dn {c}" cx="60" cy="60" r="42" stroke-dasharray="{max(L - 2, .5):.2f} {C:.2f}" stroke-dashoffset="{-off:.2f}" transform="rotate(-90 60 60)"><title>{E(n)}: {v}</title></circle>'
        off += L
    return (f'<svg class="donut" viewBox="0 0 120 120" role="img" aria-label="{E(label)}"><circle class="dn-bg" cx="60" cy="60" r="42"/>{g}'
            f'<text class="dn-n" x="60" y="62" text-anchor="middle">{sum(v for _, v, _ in parts)}</text><text class="dn-s" x="60" y="77" text-anchor="middle">{word}</text></svg>')
def vcols(items, label):
    n = len(items); bw = 56; gap = (360 - n * bw) / (n + 1); mx = max([v for _, v, _ in items] + [1]); g = ''
    for i, (l, v, c) in enumerate(items):
        x = gap + i * (bw + gap); h = 110 * v / mx; y = 130 - h
        g += (f'<rect class="sv-b {c}" x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="4"/><text class="sv-v" x="{x + bw / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle">{v}</text>'
              f'<text class="sv-x" x="{x + bw / 2:.1f}" y="150" text-anchor="middle">{E(l)}</text>')
    return f'<svg class="sv" viewBox="0 0 360 170" role="img" aria-label="{E(label)}"><line class="axis" x1="0" x2="360" y1="130.5" y2="130.5"/>{g}</svg>'
def spark(proj):
    pts = []
    for r in fr['per_run']:
        if r['project'] == proj:
            v = int(re.search(r'v(\d+)', r['step']).group(1)) if r['step'] != 'verify' else 2
            pts.append((v, 100 * r['pass'] / r['total'] if r.get('total') else None))
    pts.sort()
    if not pts: return ''
    lo, hi = pts[0][0], pts[-1][0]; sx = lambda v: 10 + (v - lo) * 130 / max(hi - lo, 1); sy = lambda p: 52 - p * .44
    line = ' '.join(f'{sx(v):.1f},{sy(p):.1f}' for v, p in pts if p is not None)
    dots = ''.join(f'<circle class="sp" cx="{sx(v):.1f}" cy="{sy(p):.1f}" r="3.6"><title>v{v}: {p:.0f}%</title></circle>' if p is not None
                   else f'<text class="sp-x" x="{sx(v):.1f}" y="40" text-anchor="middle">?</text>' for v, p in pts)
    return f'<svg class="spark" viewBox="0 0 150 64" role="img" aria-label="{E(proj)} pass rate per version"><polyline class="sp-line" points="{line}"/>{dots}<text class="sp-l" x="10" y="63">v{lo}</text><text class="sp-l" x="140" y="63" text-anchor="end">v{hi}</text></svg>'

wall = [r['wall'] for r in rows if r['wall'] is not None]; med = sorted(wall)[len(wall) // 2] if wall else 0
trend = Counter(p['trend'] for p in fr['plans_trend']); regress = sum(1 for p in fr['per_run'] if p.get('regression'))
priced = sum(r['cost'] > 0 for r in rows); nc = sum(r.get('cost_state') == 'not captured' for r in rows); cost = sum(r['cost'] for r in rows)
legend = ''.join(f'<span><i class="dot {k}"></i>{l} <b>{oc[k]}</b></span>' for k, l in (('built', 'Built'), ('partial', 'Partly built'), ('failed', 'Failed or no output')))
hist = vcols([('0-15 min', sum(w <= 15 for w in wall), ''), ('16-60', sum(15 < w <= 60 for w in wall), ''),
              ('61-120', sum(60 < w <= 120 for w in wall), 'warm'), ('120+', sum(w > 120 for w in wall), 'warm')], 'Run length')
lost = svg_hbars([(t['label'], round(t['minutes'] / 60, 1), 'warm') for t in fr.get('time_lost', [])], ' h', 'Hours lost by cause')
issues = svg_hbars([(i['name'], i['count'], '' if i.get('fixed') else 'warm') for i in fr.get('issues', [])], '', 'Harness problems')
costsvg = svg_hbars([('Priced', priced, ''), ('Not captured', nc, 'warm'), ('Other ($0, free or skipped)', N - priced - nc, '')], ' runs', 'Runs by cost record')
down = [p for p in fr['plans_trend'] if p['trend'] == 'down']; why = fr.get('down_why', {})
downrows = ''.join(f'<tr><td><b>{E(p["project"])}</b><br>{spark(p["project"])}</td><td><span class="tag">{E(why.get(p["project"], ["?", ""])[0])}</span><p>{E(why.get(p["project"], ["", "No explanation recorded."])[1])}</p></td></tr>' for p in down)
ST = {'done': 'Done', 'open': 'Open', 'none': 'No change'}
fixhtml = ''.join(f'<div class="fx-g"><h3>{E(g["group"])}</h3><ul class="fx">' + ''.join(
    f'<li class="{i["status"]}"><span class="chip">{ST.get(i["status"], i["status"])}</span><div><b>{E(i["name"])}</b><p>{E(i["text"])}</p></div></li>' for i in g['items']) + '</ul></div>' for g in fr.get('fixes', []))
nd = sum(i['status'] == 'done' for i in fixes_all); no = sum(i['status'] == 'open' for i in fixes_all)
fixdonut = donut([('Done', nd, 'built'), ('No change', len(fixes_all) - nd - no, 'partial'), ('Open', no, 'failed')], f'{nd} done, {no} open', 'fixes')
dec_done = ('<section id="answered"><h2>Decisions already made</h2><details class="done-dec"><summary>' + f'{len(answered)} answered and applied. Show them</summary><ul>'
            + ''.join(f'<li><span class="chip">Done</span><b>{E(d["title"])}</b>: {E(d["answer"])}</li>' for d in answered) + '</ul></details></section>') if answered else ''

sections = f'''
<section id="found"><h2>What verify found</h2><div class="pair"><figure class="fig">{donut([("Built", oc["built"], "built"), ("Partly built", oc["partial"], "partial"), ("Failed", oc["failed"], "failed")], "outcomes")}<div class="legend-row">{legend}</div></figure>
<div class="facts"><p><b>{regress}</b> runs caught a regression the build rounds missed.</p><p><b>{trend["up"]}</b> plans improved, <b>{trend["flat"]}</b> held flat and <b>{trend["down"]}</b> went down.</p></div></div></section>
<section id="time"><h2>Where the time went</h2><p class="lead">Median run <b>{med} min</b>; {round(sum(wall) / 60, 1)} h in total, waits included.</p>
<div class="two"><figure class="fig"><figcaption>Runs by length ({len(wall)} finished)</figcaption>{hist}</figure><figure class="fig"><figcaption>Hours lost, by cause</figcaption>{lost}</figure></div></section>
<section id="issues"><h2>Harness problems around verify</h2><p class="lead">Red bars are still open; green ones are fixed.</p><figure class="fig">{issues}</figure></section>
<section id="cost"><h2>What it cost</h2><p class="lead"><b>${cost:.2f}</b> at API list price for {priced} runs. It tracks usage on your subscriptions, not a bill. {nc} paid runs left no usage record and show "not captured".</p><figure class="fig">{costsvg}</figure></section>
<section id="down"><h2>Plans that went backwards</h2><p class="lead">{trend["down"]} plans ended lower than they started.</p>
<div class="table-wrap"><table><thead><tr><th>Plan</th><th>What I think happened</th></tr></thead><tbody>{downrows or '<tr><td colspan="2">None this week.</td></tr>'}</tbody></table></div></section>
<section id="fixes"><h2>What to fix: status</h2><div class="pair"><figure class="fig small">{fixdonut}</figure><p class="lead">{nd} done, {no} open.</p></div><div class="fxs">{fixhtml}</div></section>
'''
CSS = open(os.path.join(os.path.dirname(__file__), 'page.css'), encoding='utf-8').read()

# 3. assemble: keep the rendered decision cards (open owner calls) and artifacts
m = re.search(r'<main>(.*)</main>', base, re.S); body = m.group(1)
grab = lambda pat: (re.search(pat, body, re.S) or [''])[0]
paras = re.findall(r'<p>(.*?)</p>', grab(r'<section><h2>Summary</h2>.*?</section>'), re.S)
hero = '<section id="top" class="hero"><h2>This week in verify</h2>' + ''.join(f'<p class="lead">{p}</p>' for p in paras) + '</section>'
dec = grab(r'<section id="decisions">.*?</section>(?:<script>.*?</script>)*')
arts = grab(r'<section><h2>Artifacts</h2>.*?</section>')
out = base[:m.start()] + '<main>' + hero + sections + dec + dec_done + arts + '</main>' + base[m.end():]
out = out.replace('</head>', CSS + '\n</head>', 1)
if not openq: out = out.replace('</head>', '<style>#dec-badge{display:none}</style></head>', 1)
out = re.sub(r'<details><summary>(?!Plans<)[^<]*</summary><div class="menu">.*?</div></details>', '', out, flags=re.S)
coll = open(os.path.expanduser('~/.agents/skills/design-all/collapsible.html'), encoding='utf-8').read().split('-->', 1)[1]
out = out.replace('</head>', re.search(r'<style id="collapsible">.*?</style>', coll, re.S)[0] + '\n</head>', 1)
out = out.replace('</body>', re.search(r'<script>.*?</script>', coll, re.S)[0] + '\n</body>', 1)
open(OUT, 'w', encoding='utf-8').write(out)
subprocess.run(['node', os.path.expanduser('~/.agents/skills/design-all/scroll-perf.mjs'), '--home', '../index.html', OUT], cwd=PLANS, check=False)
subprocess.run(['python3', os.path.expanduser('~/.claude/skills/theme/theme.py'), 'fix-chars', OUT], check=False)
print('wrote', OUT)
