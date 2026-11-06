#!/usr/bin/env python3
"""collect.py - gather every build round launched in a window for /handoff-review.

  python3 collect.py --from 2026-10-27 --to 2026-11-03 --out <workdir> [--batch N] [--max-batches 8] [--fix-since "2026-10-29 15:00"]

Read-only sources: _run/driver.log (launch/done/advance/paused/checkpoint/takeover/late/waiting/lost lines) and
_observatory/blockers.mjs optimizeTips() (the Observatory's own stop detector: stops, stopStats).
Writes <out>/rounds.json (one row per plan+step), <out>/stops.json (detector output) and
<out>/batches/batchNN.json (whole plans per batch, ~18 rounds each; inputs for the Haiku agents).
"""
import argparse, json, os, re, subprocess
from datetime import datetime, timedelta
from collections import defaultdict

PLANS = os.path.expanduser('~/projects/plans')
ap = argparse.ArgumentParser()
ap.add_argument('--from', dest='frm', required=True); ap.add_argument('--to', required=True)
ap.add_argument('--out', required=True); ap.add_argument('--batch', type=int, default=0); ap.add_argument('--max-batches', type=int, default=8)
a = ap.parse_args()
t0, t1 = datetime.fromisoformat(a.frm), datetime.fromisoformat(a.to) + timedelta(days=1)
os.makedirs(f'{a.out}/batches', exist_ok=True)
EV = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (launch|done|advance|paused|checkpoint|takeover|late|waiting|lost|limit|adopt) (\d\d-[\w.-]+) ([\w.-]+?)(?:[: ]|$)(.*)')
rounds = defaultdict(lambda: {'events': [], 'launches': 0})
for line in open(f'{PLANS}/_run/driver.log', errors='replace'):
    m = EV.match(line)
    if not m or m.group(4) == 'p1': continue
    ts = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    if not (t0 <= ts < t1): continue
    r = rounds[(m.group(3), m.group(4))]
    r['events'].append(line.strip()[:240])
    if m.group(2) == 'launch': r['launches'] += 1
rows = []
for (plan, step), r in sorted(rounds.items()):
    if not r['launches']: continue  # only rounds that started in the window
    b = f'{PLANS}/{plan}/_build/{step}'
    rows.append({'plan': plan, 'step': step, 'launches': r['launches'], 'round_dir': b,
                 'notes': [n for n in ('PAUSE.md', 'HANDOFF.md', 'AUDIT.md') if os.path.exists(f'{b}/{n}')],
                 'advanced': any(' advance ' in e for e in r['events']), 'events': r['events'][-40:]})
json.dump(rows, open(f'{a.out}/rounds.json', 'w'), indent=1)
# detector output (same code the Observatory runs)
js = ("import('%s/_observatory/blockers.mjs').then(m=>{const fs=require('fs');const lines=fs.readFileSync('%s/_run/driver.log','utf8').split('\\n').slice(-80000);"
      "const o=m.optimizeTips({lines,plans:[],health:{},speed:{},tally:{},prio:{projects:{}}});"
      "console.log(JSON.stringify({stopStats:o.stopStats,stops:o.stops,tip:o.tips.find(t=>t.kind==='handoff')||null}))})") % (PLANS, PLANS)
det = subprocess.run(['node', '-e', js], capture_output=True, text=True, cwd=PLANS)
try: json.dump(json.loads(det.stdout), open(f'{a.out}/stops.json', 'w'), indent=1)
except Exception: open(f'{a.out}/stops.json', 'w').write('{"error": %s}' % json.dumps(det.stderr[-2000:]))
# batches: whole plans, ~a.batch rounds each
byplan = defaultdict(list)
for r in rows: byplan[r['plan']].append(r)
import math
nb = min(a.max_batches, max(1, math.ceil(len(rows) / (a.batch or 18))))
batches = [[] for _ in range(nb)]
for plan in sorted(byplan, key=lambda p: -len(byplan[p])):  # whole plans, largest first, into the smallest batch
    min(batches, key=len).extend(byplan[plan])
batches = [b for b in batches if b]
for i, bt in enumerate(batches, 1): json.dump(bt, open(f'{a.out}/batches/batch{i:02d}.json', 'w'), indent=1)
print(f'{len(rows)} rounds, {len(byplan)} plans, {sum(r["launches"] for r in rows)} launches, {len(batches)} batches -> {a.out}')
