#!/usr/bin/env python3
"""memory-review collector: one read-only snapshot of where RAM and /tmp go.

Writes <out>/snapshot.json (and prints a short table). Read-only: no kills, no deletes.
Usage: python3 collect.py --out DIR [--prev PREV_snapshot.json] [--top 25]
"""
import argparse, glob, json, os, re, subprocess, time
from collections import Counter

def rd(p, default=''):
    try:
        with open(p) as f: return f.read()
    except Exception: return default

def status(pid):
    d = {}
    for ln in rd(f'/proc/{pid}/status').splitlines():
        k, _, v = ln.partition(':')
        if k in ('VmRSS', 'VmHWM', 'RssAnon', 'RssFile', 'RssShmem'):
            d[k] = int(v.split()[0]) // 1024  # MB
    return d

def procs(top):
    rows = []
    for p in glob.glob('/proc/[0-9]*'):
        pid = int(p[6:])
        st = status(pid)
        if not st.get('VmRSS'): continue
        cmd = rd(f'{p}/cmdline').replace('\0', ' ').strip()[:220]
        comm = rd(f'{p}/comm').strip()
        try: age_s = time.time() - os.stat(p).st_mtime
        except Exception: age_s = 0
        etime = subprocess.run(['ps', '-o', 'etimes=', '-p', str(pid)], capture_output=True, text=True).stdout.strip()
        rows.append({'pid': pid, 'comm': comm, 'cmd': cmd, 'etime_s': int(etime or 0), **{k.lower(): v for k, v in st.items()}})
    rows.sort(key=lambda r: -r['vmrss'])
    return rows[:top]

def meminfo():
    m = {}
    for ln in rd('/proc/meminfo').splitlines():
        k, _, v = ln.partition(':')
        m[k] = int(v.split()[0]) // 1024
    return {k: m.get(k) for k in ('MemTotal', 'MemAvailable', 'Shmem', 'SwapTotal', 'SwapFree', 'Cached')}

def sysv_shm():
    out = subprocess.run(['ipcs', '-mp'], capture_output=True, text=True).stdout
    cp = {}
    for ln in out.splitlines():
        f = ln.split()
        if len(f) >= 4 and f[0].isdigit(): cp[f[0]] = int(f[2])
    segs = []
    for ln in subprocess.run(['ipcs', '-m'], capture_output=True, text=True).stdout.splitlines():
        f = ln.split()
        if len(f) >= 6 and f[1].isdigit() and int(f[4]) >= 16 << 20:
            pid = cp.get(f[1])
            segs.append({'shmid': f[1], 'mb': int(f[4]) >> 20, 'creator_pid': pid, 'creator': rd(f'/proc/{pid}/cmdline').replace('\0', ' ')[:120] if pid else ''})
    return segs

def tmp_usage():
    df = subprocess.run(['df', '-m', '--output=fstype,used,size', '/tmp'], capture_output=True, text=True).stdout.split('\n')[1].split()
    ents = []
    for e in os.scandir('/tmp'):
        try:
            if e.is_dir(follow_symlinks=False):
                sz = int(subprocess.run(['du', '-sm', e.path], capture_output=True, text=True).stdout.split()[0] or 0)
            else:
                sz = e.stat(follow_symlinks=False).st_size >> 20
            ents.append({'name': e.name, 'mb': sz, 'mtime': int(e.stat(follow_symlinks=False).st_mtime)})
        except Exception: pass
    ents.sort(key=lambda x: -x['mb'])
    so = [e for e in os.scandir('/tmp') if re.fullmatch(r'\.[0-9a-f]{16}-00000000\.so', e.name)]
    hours = Counter(time.strftime('%m-%d %H', time.localtime(e.stat().st_mtime)) for e in so)
    so_mb = sum(e.stat().st_size for e in so) >> 20
    return {'fstype': df[0], 'used_mb': int(df[1]), 'size_mb': int(df[2]), 'top': ents[:20],
            'opencode_so': {'count': len(so), 'mb': so_mb, 'per_hour': dict(sorted(hours.items()))}}

def services():
    out = {}
    for unit in ('observatory',):
        pid = subprocess.run(['systemctl', '--user', 'show', '-p', 'MainPID', '--value', unit], capture_output=True, text=True).stdout.strip()
        if pid and pid != '0':
            out[unit] = {'pid': int(pid), **{k.lower(): v for k, v in status(pid).items()}}
    return out

def zen_probes():
    log = os.path.expanduser('~/dev/projects/plans/_run/flags/free_heartbeat.log')
    days = {}
    for ln in rd(log).splitlines():
        m = re.match(r'(\d{4}-\d\d-\d\d) \S+ zen \S+ (ok|down|skipped)', ln)
        if m:
            d = days.setdefault(m.group(1), {'ok': 0, 'down': 0, 'skipped': 0})
            d[m.group(2)] += 1
    return dict(sorted(days.items())[-10:])

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--out', required=True); a.add_argument('--prev'); a.add_argument('--top', type=int, default=25)
    o = a.parse_args()
    os.makedirs(o.out, exist_ok=True)
    snap = {'taken': time.strftime('%Y-%m-%d %H:%M'), 'uptime_s': int(float(rd('/proc/uptime', '0').split()[0])),
            'meminfo': meminfo(), 'procs': procs(o.top), 'sysv_shm': sysv_shm(), 'tmp': tmp_usage(),
            'services': services(), 'zen_probes': zen_probes(),
            'archives': [{'path': p, 'mb': int(subprocess.run(['du', '-sm', p], capture_output=True, text=True).stdout.split()[0])}
                         for p in glob.glob(os.path.expanduser('~/tmp-archive*'))]}
    if o.prev and os.path.exists(o.prev):
        prev = json.load(open(o.prev))
        pm = {(r['comm'], r['cmd'][:80]): r['vmrss'] for r in prev.get('procs', [])}
        for r in snap['procs']:
            r['prev_rss'] = pm.get((r['comm'], r['cmd'][:80]))
        snap['prev_taken'] = prev.get('taken')
    json.dump(snap, open(f'{o.out}/snapshot.json', 'w'), indent=1)
    m = snap['meminfo']
    print(f"RAM available {m['MemAvailable']} / {m['MemTotal']} MB, shmem {m['Shmem']} MB; /tmp {snap['tmp']['used_mb']} MB ({snap['tmp']['fstype']})")
    print(f"opencode .so in /tmp: {snap['tmp']['opencode_so']['count']} files, {snap['tmp']['opencode_so']['mb']} MB")
    for r in snap['procs'][:15]:
        prev = f" (prev {r['prev_rss']})" if r.get('prev_rss') else ''
        print(f"{r['vmrss']:>7} MB  anon {r.get('rssanon',0):>6}  shm {r.get('rssshmem',0):>6}  up {r['etime_s']//3600:>4}h  {r['comm']:<16} {r['cmd'][:70]}{prev}")
    print(f"wrote {o.out}/snapshot.json")

if __name__ == '__main__':
    main()
