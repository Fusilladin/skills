#!/usr/bin/env python3
"""build_page.py - weekly handoff review page from <work>/final-review.json + stops.json (review_kit style, owner 2026-11-10).

  python3 build_page.py --work <workdir> --out /path/to/projects/workspace/_reports/handoff-review-YYYY-MM-DD.html

Few words, SVG first: hero verdict + big numbers; sections (one chart + one line each): where rounds ended (funnel),
shutdowns (timeline), retry loop (tick strip), stops per day; fix cards (each with its own viz from fixes[].viz);
decision cards; Details panels hold the technical text. Also writes handoff-review-latest.html and <out>.summary.json.
Needs in final-review.json: fixes[].line + fixes[].viz, and viz {verdict_short, shutdowns[], loop} (see opus-brief.md).
"""
import argparse, json, os, shutil, sys
import review_kit as K
ap = argparse.ArgumentParser(); ap.add_argument('--work', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
fr = json.load(open(f'{a.work}/final-review.json')); st = json.load(open(f'{a.work}/stops.json')).get('stopStats') or {}
nb = fr['numbers']; vz = fr.get('viz', {}); oc = {o['kind']: o for o in fr['outcomes']}; fx = fr['fixes']
openq = [d for d in fr.get('decisions', []) if not d.get('answer')]; answered = [d for d in fr.get('decisions', []) if d.get('answer')]
clean = oc.get('ok', {}).get('n', 0); pct = round(100 * clean / max(nb['rounds'], 1))
tiles = [(nb['rounds'], 'rounds this week', 'n'), (nb['launches'], 'launches', 'n'), (f'{pct}%', 'clean on the first try', 'ok'), (nb['lost_work'], 'lost work, no note', 'bad')]
S = []
S.append(K.section('ended', 'Where rounds ended', K.funnel(('Rounds', nb['rounds']), [
    (oc['ok']['label'], oc['ok']['n'], 'ok', ''), (oc['note']['label'], oc['note']['n'], 'info', ''),
    (oc['warn']['label'], oc['warn']['n'], 'bad', f'{nb["lost_work"]} lost real work')]),
    f'{oc["warn"]["n"]} rounds stopped with no note to pick up from.',
    K.details('Details', K.dl([('Detector:', f'{nb["stops"]} stops after the 11-03 fix ({nb["noted"]} with a note, {nb["unnoted"]} without), {nb["late"]} late.'),
                               ('Notes found:', f'{fr["note_quality"]["good"]} good, {fr["note_quality"]["thin"]} thin, {fr["note_quality"]["wrong"]} wrong.'),
                               ('Retries read the note:', f'{fr["retry_found"]["prompt"]} via the prompt, {fr["retry_found"]["never"]} never.')] + [('', p) for p in fr['summary'][:1]]))))
if vz.get('shutdowns'):
    sd = vz['shutdowns']; lost = sum(s['rounds'] for s in sd)
    S.append(K.section('shutdowns', 'Two shutdowns with jobs running', K.timeline(('11-03', '11-06', 4), [
        (s['pos'], s['when'], s['note'], 'bad' if s['rounds'] else 'ok', s['mins'], s.get('anchor', 'start')) for s in sd]),
        f'{lost} running rounds were killed with no note. Bars show minutes each had run.',
        K.details('Details', K.dl([('', fr['summary'][1])] if len(fr['summary']) > 1 else []))))
if vz.get('loop'):
    lp = vz['loop']
    S.append(K.section('loop', f'One retry loop: plan {lp["plan"]}', K.tickstrip(lp['launches'], lp['limit_hits'], 'launches', cap=3),
        f'{lp["launches"]} cloud launches in {lp["hours"]} h; {lp["limit_hits"]} hit the limit within a minute. Green line: where a cap would stop it.'))
days = st.get('daily', [])[-10:]
if days:
    S.append(K.section('days', 'Stops per day', K.stacked_days(days, [('noted', 'With a note', 'ok'), ('unnoted', 'No note', 'bad'), ('late', 'Late, nothing lost', 'skip')]),
        'From the Run Dashboard detector, which does not see vanished jobs.'))
nd = sum(f['status'] == 'done' for f in fx); no = sum(f['status'] == 'open' for f in fx)
rej = [(f'{r["result"]}:', f'{r["claim"]}. {r["why"]}') for r in fr.get('rejected', [])]
S.append(f'<section id="fixes"><h2>Fixes: {nd} done, {no} open</h2>' + K.cards(fx)
         + K.details('Details', K.dl([(f['name'] + ':', f['text']) for f in fx]) + (f'<p><b>Claims that did not hold</b></p>{K.dl(rej)}' if rej else '')) + '</section>')
S.append(K.decision_cards(openq, answered))
nav = [('#ended', 'Rounds'), ('#shutdowns', 'Shutdowns'), ('#fixes', 'Fixes')] + ([('#decisions', 'Your calls')] if openq else []) + [('../_run-dashboard/index.html', 'Run Dashboard'), ('review-all-' + fr['window'][-10:] + '.html', 'All reviews')]
win = fr['window'].replace('..', ' to ')
out = K.page(a.out, 'Handoff review', f'Round stops and notes, {win}', vz.get('verdict_short', fr['verdict']), tiles, ''.join(S), nav, win,
             summary={'name': 'handoff', 'headline': f'{pct}% of rounds clean on the first try; {nb["lost_work"]} lost work with no note',
                      'chart': K.funnel(('Rounds', nb['rounds']), [(oc['ok']['label'], oc['ok']['n'], 'ok', ''), (oc['note']['label'], oc['note']['n'], 'info', ''), (oc['warn']['label'], oc['warn']['n'], 'bad', '')]),
                      'fixes': {'done': nd, 'open': no}, 'decisions': openq})
shutil.copy(out, os.path.join(os.path.dirname(out), 'handoff-review-latest.html'))
print('wrote', out, '+ handoff-review-latest.html')
