#!/usr/bin/env python3
"""collect.py - gather every verify run in a date window for /verify-review.

  python3 collect.py --from 2026-10-27 --to 2026-11-03 --out <workdir> [--batch 12]

Sources (read-only):
  - Observatory /api/snapshot agents (pulled in 3 h windows: the API caps agents at 300 rows)
  - _run/driver.log launch/done lines (attempts, rc, missing outputs, minutes)
  - each job dir's meta (provider waits, codex tries, rc 124, queue waits)
Writes <out>/verify-data.json (one row per run) and <out>/batches/batchNN.json (inputs for Haiku agents).
"""
import argparse, json, os, re, urllib.request
from datetime import datetime, timedelta
from collections import defaultdict

PLANS = os.path.expanduser('~/projects/plans')
OBS = 'http://localhost:18990'
ap = argparse.ArgumentParser()
ap.add_argument('--from', dest='frm', required=True); ap.add_argument('--to', required=True)
ap.add_argument('--out', required=True); ap.add_argument('--batch', type=int, default=12)
a = ap.parse_args()
t0, t1 = datetime.fromisoformat(a.frm), datetime.fromisoformat(a.to)
os.makedirs(f'{a.out}/batches', exist_ok=True)
is_verify = lambda step: bool(step) and re.fullmatch(r'(v\d+-)?verify', step)

# 1. Observatory attempts
obs = defaultdict(list); t = t0
while t < t1:
    e = min(t + timedelta(hours=3), t1)
    url = f'{OBS}/api/snapshot?from={int(t.timestamp() * 1000)}&to={int(e.timestamp() * 1000)}'
    try:
        snap = json.load(urllib.request.urlopen(url, timeout=300))
    except Exception as ex:
        raise SystemExit(f'Observatory not reachable ({ex}); start it: systemctl --user start observatory')
    for ag in snap.get('agents', []):
        if is_verify(ag.get('step')):
            k = (ag['project'], ag['step'], ag.get('started'))
            obs[k[:2]] = [x for x in obs[k[:2]] if x.get('started') != ag.get('started')] + [ag]
    t = e

# 2. driver.log
LAUNCH = re.compile(r'^(\S+ \S+) launch (\S+) (\S+) premium')
DONE = re.compile(r'^(\S+ \S+) done (\S+) (\S+) rc=(\S+) missing=\[([^\]]*)\] (\d+)min')
runs = {}
for line in open(f'{PLANS}/_run/driver.log', errors='replace'):
    m = LAUNCH.match(line) or DONE.match(line)
    if not m or not is_verify(m.group(3)): continue
    ts = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    if not (t0 <= ts < t1 + timedelta(days=1)): continue
    k = (m.group(2), m.group(3)); r = runs.setdefault(k, {'launches': [], 'dones': []})
    if 'launch' in line.split()[2]: r['launches'].append(ts)
    else: r['dones'].append({'at': ts, 'rc': m.group(4), 'missing': m.group(5), 'min': int(m.group(6))})
for k in obs:
    runs.setdefault(k, {'launches': [], 'dones': []})

# 3. rows
rows = []
for (proj, step), r in sorted(runs.items()):
    start = min(r['launches'] + [d['at'] for d in r['dones']], default=None)
    if start is None:
        st = [x.get('started') for x in obs[(proj, step)] if x.get('started')]
        start = datetime.fromtimestamp(min(st) / 1000) if st else None
    if start is None or not (t0 <= start < t1): continue
    jd = f'{PLANS}/{proj}/_build/{step}'
    meta = open(f'{jd}/meta', errors='replace').read() if os.path.exists(f'{jd}/meta') else ''
    waits = re.findall(r'unavailable; retrying in (\d+) min', meta)
    ends = [d['at'] for d in r['dones']]
    ag = obs[(proj, step)]
    models = sorted({x.get('model') or '?' for x in ag}) or (['codex-sol'] if 'premium: codex' in meta else ['opus-5-5'])
    n = int(re.search(r'v(\d+)', step).group(1)) if step != 'verify' else 2
    cand = [f'{PLANS}/{proj}/_build/v{n + 1}-final/VERIFY.md', f'{PLANS}/{proj}/_build/VERIFY.md'] if step != 'verify' else \
           [f'{PLANS}/{proj}/_build/v2-final/VERIFY.md', f'{PLANS}/{proj}/_build/VERIFY.md']
    rows.append({
        'project': proj, 'step': step, 'ver': n, 'start': start.strftime('%Y-%m-%d %H:%M'),
        'end': max(ends).strftime('%Y-%m-%d %H:%M') if ends else None,
        'wall': round((max(ends) - start).total_seconds() / 60) if ends else None,
        'attempts': max(1, len(r['dones'])), 'driver_rcs': [d['rc'] for d in r['dones']],
        'model': '+'.join(models), 'codex_in_meta': 'premium: codex' in meta,
        'cost': round(sum(x.get('cost') or 0 for x in ag), 4),
        'cost_state': 'not captured' if any(x.get('costState') == 'not captured' for x in ag) and not any(x.get('cost') for x in ag) else ('priced' if any(x.get('cost') for x in ag) else 'unknown'),
        'calls': sum(x.get('calls') or 0 for x in ag),
        'waits': len(waits), 'wait_min': sum(map(int, waits)),
        'queue_wait_min': sum(x.get('queueWaitMin') or 0 for x in ag),
        'codex_limit': meta.count('usage limit hit'), 'timeout124': len(re.findall(r'rc=124|exited 124', meta)),
        'lost': sum(d['rc'] == 'lost' for d in r['dones']),
        'missing_retry': sum(bool(d['missing']) for d in r['dones'][:-1]),
        'job_dir': jd, 'verify_md_candidates': [c for c in cand if os.path.exists(c)],
        'deferred_md_candidates': [c.replace('VERIFY.md', 'DEFERRED.md') for c in cand if os.path.exists(c.replace('VERIFY.md', 'DEFERRED.md'))],
        'observatory_attempts': [{k: x.get(k) for k in ('provider', 'model', 'rc', 'cost', 'costState', 'started', 'ended', 'queueWaitMin', 'provWaitMin')} for x in ag],
        'driver_log': [f"{d['at']:%m-%d %H:%M} rc={d['rc']} missing=[{d['missing']}] {d['min']}min" for d in r['dones']],
    })
json.dump(rows, open(f'{a.out}/verify-data.json', 'w'), indent=1)
for i in range(0, len(rows), a.batch):
    json.dump(rows[i:i + a.batch], open(f'{a.out}/batches/batch{i // a.batch + 1:02d}.json', 'w'), indent=1)
print(f'{len(rows)} verify runs, {len({r["project"] for r in rows})} plans, {(len(rows) + a.batch - 1) // a.batch} batches -> {a.out}')
