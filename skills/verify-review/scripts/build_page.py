#!/usr/bin/env python3
"""build_page.py - weekly verify review page from <work>/final-review.json + verify-data.json (review_kit style, owner 2026-11-10).

  python3 build_page.py --work <workdir> --out /path/to/projects/workspace/_reports/verify-review-YYYY-MM-DD.html

Few words, SVG first: hero verdict + big numbers; sections (one chart + one line): outcomes donut, pass rate per plan
(small multiples), time lost waiting, harness problems; fix cards (each with its own viz from fixes[].items[].viz);
decision cards; Details panels hold the technical text. Also writes <out>.summary.json for /review-all.
Needs in final-review.json: items[].line + items[].viz (+ optional short), viz {verdict_short, waits[[label,min]]}.
"""
import argparse, json, os, re, sys
import review_kit as K
ap = argparse.ArgumentParser(); ap.add_argument('--work', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
fr = json.load(open(f'{a.work}/final-review.json')); rows = json.load(open(f'{a.work}/verify-data.json'))
oc = fr['outcomes']; vz = fr.get('viz', {}); N = len(rows); plans = len({r['project'] for r in rows})
regress = sum(1 for p in fr['per_run'] if p.get('regression')); cost = sum(r['cost'] for r in rows)
openq = [d for d in fr.get('decisions', []) if not d.get('answer')]; answered = [d for d in fr.get('decisions', []) if d.get('answer')]
items = [dict(i, name=i.get('short', i['name'])) for g in fr.get('fixes', []) for i in g['items']]
tiles = [(N, f'checks across {plans} plans', 'n'), (oc['built'], 'plans fully built', 'bad'), (regress, 'checks found something broken', 'warn'), (f'${cost:.2f}', 'API list price', 'info')]
S = []
dn = K.donut([('Built', oc['built'], 'ok'), ('Partly built', oc['partial'], 'warn'), ('No verdict', oc['failed'], 'bad')], str(N), 'checks')
S.append(K.section('found', 'What the checks found', dn, f'{oc["partial"]} partly built, {oc["failed"]} gave no verdict.',
                   K.details('Details', K.dl([('', p) for p in fr['summary']]))))
TK = {'up': 'ok', 'down': 'bad', 'flat': 'info'}; tr = {p['project']: p['trend'] for p in fr['plans_trend']}; ser = {}
for r in fr['per_run']:
    m = re.search(r'v(\d+)', r['step']); v = int(m[1]) if m else 2
    ser.setdefault(r['project'], []).append((v, f'v{v}', 100 * r['pass'] / r['total'] if r.get('total') else None))
mult = K.smallmult([(p, [(l, x) for _, l, x in sorted(s)], TK.get(tr.get(p), 'info')) for p, s in ser.items()])
why = fr.get('down_why', {})
S.append(K.section('trend', 'Pass rate per plan, by version', mult, 'Green rising, red falling, purple flat. Compare the measured trends across projects.',
                   K.details('Details', K.dl([(p + ':', f'{w[0]}. {w[1]}') for p, w in why.items()] + [(f'{r["project"]} {r["step"]}:', r['note']) for r in fr['per_run']]))))
if vz.get('waits'):
    S.append(K.section('time', 'Time spent waiting for a model', K.hbars([(l, m, 'warn') for l, m in vz['waits']], ' min'),
                       f'{sum(m for _, m in vz["waits"])} min waiting. No queue waits, no runs lost at restarts.',
                       K.details('Details', K.dl([(t['label'] + ':', f'{t["minutes"]} min') for t in fr.get('time_lost', [])]))))
S.append(K.section('issues', 'Problems around the checks', K.hbars([(lab, i['count'], 'ok' if i.get('fixed') else 'bad') for lab, i in zip(vz.get('issue_labels') or [i['name'] for i in fr.get('issues', [])], fr.get('issues', []))], '', W=720),
                   'Count of runs hit by each. All still open.', K.details('Details', K.dl([('', i['name']) for i in fr.get('issues', [])]))))
nd = sum(i['status'] == 'done' for i in items); no = sum(i['status'] == 'open' for i in items)
S.append(f'<section id="fixes"><h2>Fixes: {nd} done, {no} open</h2>' + K.cards(items) + K.details('Details', K.dl([(i['name'] + ':', i['text']) for i in items])) + '</section>')
S.append(K.decision_cards(openq, answered))
win = fr['window'].replace('..', ' to ')
nav = [('#found', 'Results'), ('#trend', 'Per plan'), ('#fixes', 'Fixes')] + ([('#decisions', 'Your calls')] if openq else []) + [('../_run-dashboard/index.html', 'Run Dashboard'), ('review-all-' + fr['window'][-10:] + '.html', 'All reviews')]
K.page(a.out, 'Verify review', f'Verify jobs, {win}', vz.get('verdict_short', fr['summary'][0]), tiles, ''.join(S), nav, win,
       summary={'name': 'verify', 'headline': f'{oc["built"]} of {N} checks fully built; {regress} found something broken', 'chart': dn,
                'fixes': {'done': nd, 'open': no}, 'decisions': openq})
print('wrote', a.out)
