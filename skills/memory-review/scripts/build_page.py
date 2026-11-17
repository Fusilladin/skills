#!/usr/bin/env python3
"""memory-review page builder: <work>/findings.json -> review_kit page (owner 2026-11-10: few words, SVG first).

  python3 build_page.py --work DIR --out /path/to/projects/workspace/_reports/memory-review-YYYY-MM-DD.html

findings.json keys: title, date, lead, verdict_short, hero {value, unit, text}, findings[] {id, name, verdict leak|held|pileup|normal,
worst_mb, after_mb?, line, viz, lede, stats, why, fix}, context, trend[] {date, available_mb}, decisions[] (answer set = folded),
fixes[] {title, state done|open, note, viz}. viz specs: see the adjacent review_kit.py module.
Sections: where RAM goes (bars), free RAM per week (line), findings as cards, fixes as cards, decisions. Writes <out>.summary.json.
"""
import argparse, json, os, sys
import importlib.util
from pathlib import Path

# The documented -I invocation excludes this directory from sys.path.
_kit_spec = importlib.util.spec_from_file_location('review_kit', Path(__file__).resolve().with_name('review_kit.py'))
K = importlib.util.module_from_spec(_kit_spec)
_kit_spec.loader.exec_module(K)
ap = argparse.ArgumentParser(); ap.add_argument('--work', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
c = json.load(open(os.path.join(a.work, 'findings.json')))
gb = lambda mb: round(mb / 1000, 1)
fs = c['findings']; tr = c.get('trend') or []; h = c.get('hero') or {}
openq = [d for d in c.get('decisions', []) if not d.get('answer')]; answered = [d for d in c.get('decisions', []) if d.get('answer')]
fixes = [{'status': x['state'], 'name': x['title'], 'line': x.get('note', ''), 'viz': x.get('viz')} for x in c.get('fixes', [])]
bad = sum(f['verdict'] in ('leak', 'pileup') for f in fs)
tiles = ([(f'{gb(tr[-1]["available_mb"])} GB', 'RAM free', 'ok')] if tr else []) + [(f'{h.get("value")} {h.get("unit", "GB")}', 'stuck in /tmp', 'bad'), (bad, 'need action', 'warn'), (len(openq), 'calls for you', 'info')]
S = []
bars = K.hbars([(f['name'], gb(f['worst_mb']), {'leak': 'bad', 'pileup': 'bad', 'held': 'warn'}.get(f['verdict'], 'ok')) for f in fs if f.get('worst_mb')], ' GB')
S.append(K.section('where', 'Where the RAM goes', bars, 'Worst seen per item. Red needs action, amber is held but stable.',
                   K.details('Details', f'<p>{K.E(c.get("context", ""))}</p>')))
if len(tr) > 1:
    S.append(K.section('trend', 'Free RAM at each weekly check', K.line2([(t['date'][5:], gb(t['available_mb'])) for t in tr], 'GB'), ''))
S.append('<section id="found"><h2>What I found</h2>' + K.cards([{'status': f['verdict'], 'name': f['name'], 'line': f.get('line', f.get('lede', '')), 'viz': f.get('viz')} for f in fs])
         + K.details('Details', ''.join(f'<p><b>{K.E(f["name"])}.</b> {K.E(f.get("lede", ""))} {K.E(f.get("why", ""))} {K.E(f.get("fix", ""))}</p>' for f in fs)) + '</section>')
if fixes:
    nd = sum(f['status'] == 'done' for f in fixes)
    S.append(f'<section id="fixes"><h2>Fixes: {nd} done, {len(fixes) - nd} open</h2>' + K.cards(fixes) + '</section>')
S.append(K.decision_cards(openq, answered))
nav = [('#where', 'RAM'), ('#found', 'Found'), ('#fixes', 'Fixes')] + ([('#decisions', 'Your calls')] if openq else []) + [('../_run-dashboard/index.html', 'Run Dashboard'), (f'review-all-{c["date"]}.html', 'All reviews')]
K.page(a.out, 'Memory review', f'Weekly RAM and /tmp check, {c["date"]}', c.get('verdict_short', c.get('lead', '')), tiles, ''.join(S), nav, c['date'],
       summary={'name': 'memory', 'headline': h.get('text', c.get('lead', '')), 'chart': bars, 'fixes': {'done': sum(f['status'] == 'done' for f in fixes), 'open': sum(f['status'] != 'done' for f in fixes)}, 'decisions': openq})
print('wrote', a.out)
