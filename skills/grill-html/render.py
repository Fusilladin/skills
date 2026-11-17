#!/usr/bin/env python3
"""grill-html renderer: state.json -> a grill section.

Two modes, chosen by state.json:
  * "host": "<path to an existing explainer page, relative to state.json>"
      The grill is embedded INTO that page as <section id="grilling-session">,
      between <!-- grill-html:start --> / <!-- grill-html:end --> markers
      (replaced on every render). First render inserts it after the section
      named by "host_after" (a section id), else before </main>, else before </body>.
      Rounds listed in "host_rounds" are already shown by the host page and are
      not repeated. The host's own owner-answer boxes (textarea.owe with
      data-q/data-title/data-orig) are picked up by Copy answers as CHANGE lines.
  * no "host": a standalone page <state dir>/../grill.html (or "out"), styled
    with assets/theme.css (the bundled page theme).

Usage: python3 render.py <state.json>      prints: <page path>#grilling-session <agreement>%
"""
import json, html, re, sys, pathlib, datetime

E = html.escape
HERE = pathlib.Path(__file__).resolve().parent
START, END = '<!-- grill-html:start -->', '<!-- grill-html:end -->'


def inl(s):
    s = E(s or '')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s


def para(s):
    ps = [p for p in re.split(r'\n\s*\n', (s or '').strip()) if p.strip()]
    return '<br>'.join(inl(p) for p in ps)


ICON = {
    'q': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7"/><circle cx="12" cy="17" r=".6"/>',
    'ok': '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.6 2.5L16 9.5"/>',
    'chg': '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    'tree': '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 8v8M8 6h4a4 4 0 0 1 4 4M8 18h4a4 4 0 0 0 4-4"/>',
    'copy': '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
    'flag': '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    'list': '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4z"/>',
    'coin': '<circle cx="12" cy="12" r="9"/><path d="M14.5 9.5c-.5-1-1.5-1.5-2.5-1.5-1.4 0-2.5.8-2.5 2s1.1 1.6 2.5 2 2.5.8 2.5 2-1.1 2-2.5 2c-1 0-2-.5-2.5-1.5M12 6.5v11"/>',
    'bolt': '<path d="M13 3 5 14h6l-1 7 8-11h-6z"/>',
    'wrench': '<path d="M14.5 6.5a4 4 0 0 0 5 5L12 19a2 2 0 0 1-3-3z"/><path d="M14.5 6.5 17 4l3 3-2.5 2.5"/>',
    'shield': '<path d="M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6z"/>',
    'search': '<circle cx="11" cy="11" r="6"/><path d="m20 20-4.5-4.5"/>',
    'chip': '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    'db': '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>',
    'plug': '<path d="M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0zM12 16v5"/>',
    'star': '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    'wait': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
}


def ic(k):
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ICON.get(k, ICON["list"])}</svg>'


# Grill-only styles. Cards (.qc/.qi/.ans), .note, .legend, .chart, .facts, .more,
# tables and sections come from the bundled theme (host page or assets/theme.css).
GCSS = r'''
#grilling-session .ic{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
#grilling-session .qi .ic{width:24px;height:24px}
#grilling-session .gq{display:grid;gap:14px;margin:14px 0}
#grilling-session .qc.cur{border-color:var(--acc)}
#grilling-session .qc .qn{font:700 13px var(--mono);color:var(--acc)}
#grilling-session .qc h3{margin:2px 0 0;font-size:16.5px;line-height:1.35}
#grilling-session .qc dd.rec{color:var(--ink)}
#grilling-session .ch{display:grid;gap:6px;margin:4px 0 0}
#grilling-session .ch label{display:flex;gap:10px;align-items:flex-start;border:1px solid var(--line);border-radius:8px;padding:8px 12px;cursor:pointer;background:var(--bg);font-size:14.5px}
#grilling-session .ch label:has(input:checked){border-color:var(--acc);background:var(--acc2)}
#grilling-session .ch input{margin-top:5px;accent-color:var(--acc)}
#grilling-session .rtag{font:600 11px var(--mono);color:var(--acc);margin-left:6px}
#grilling-session textarea{width:100%;box-sizing:border-box;font:inherit;font-size:14.5px;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px 10px;resize:vertical;min-height:2.8em;margin-top:8px}
#grilling-session textarea:focus{outline:2px solid var(--acc);outline-offset:1px}
textarea.chd{border-color:var(--warn)!important;background:var(--warn2)!important}
#grilling-session .gx{margin:22px 0 8px;padding-left:14px;border-left:3px solid var(--line)}
#grilling-session .gx>h3{display:flex;gap:8px;align-items:center;margin:0 0 4px;font-size:17px}#grilling-session .gx>h3 .ic{color:var(--acc)}
#grilling-session .gtree{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,220px),1fr));gap:6px;margin:0 0 18px}
#grilling-session .tnode{display:flex;gap:8px;align-items:flex-start;border:1px solid var(--line);border-radius:8px;padding:7px 10px;background:var(--bg2);font-size:13.5px;line-height:1.4}
#grilling-session .tnode i{width:9px;height:9px;border-radius:50%;margin-top:5px;flex:none;background:var(--dim)}
#grilling-session .tnode.settled i{background:var(--acc)}#grilling-session .tnode.open i{background:var(--warn)}
#grilling-session .tnode.assumed{border-style:dashed}#grilling-session .tnode.assumed i{background:none;border:2px solid var(--warn)}#grilling-session .tnode.out{opacity:.55}
#grilling-session .tnode small{display:block;color:var(--dim);font:11.5px var(--mono)}
#grilling-session .qrow{border-bottom:1px solid var(--line)}
#grilling-session .qrow>summary{cursor:pointer;display:grid;grid-template-columns:44px minmax(0,1.2fr) minmax(0,1fr) auto;gap:10px;align-items:baseline;padding:8px 0;list-style:none}
#grilling-session .qrow>summary::-webkit-details-marker{display:none}
#grilling-session .qrow .qn{font:700 12.5px var(--mono);color:var(--acc)}#grilling-session .qrow .qt{font-weight:600;font-size:14.5px}#grilling-session .qrow .qa{color:var(--mut);font-size:14px}
#grilling-session .qrow>.qc{margin:0 0 12px}
#grilling-session .gbar{position:sticky;bottom:12px;z-index:6;display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0 8px;padding:10px 14px;border:1px solid var(--acc);border-radius:var(--r);background:var(--bg2);box-shadow:0 8px 30px rgba(0,0,0,.35)}
#grilling-session .gbar button{display:inline-flex;gap:6px;align-items:center;font:600 14px var(--sans);padding:8px 14px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink);cursor:pointer}
#grilling-session .gbar #g-copy{background:var(--acc);border-color:var(--acc);color:#04110f}
#grilling-session .gbar .m{color:var(--mut);font-size:14px;flex:1 1 220px}
#grilling-session .gdone{border:1px solid var(--acc);background:var(--acc2);border-radius:var(--r);padding:14px 16px;margin:12px 0}
#grilling-session .chart svg{width:100%;height:auto;display:block}
.s-t{fill:var(--ink);font:600 13px var(--sans)}.s-m{fill:var(--mut);font:12px var(--sans)}.s-n{fill:var(--ink);font:700 13px var(--mono)}
.s-trk{fill:#1b2330}.s-fill{fill:var(--acc)}.s-wr{fill:var(--warn)}.s-dim{fill:var(--dim)}.s-tgt{stroke:var(--warn);stroke-width:2;stroke-dasharray:4 3}
@media (max-width:600px){#grilling-session .qrow>summary{grid-template-columns:40px 1fr auto}#grilling-session .qrow .qa{grid-column:2/4}}
#grilling-session .gt{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;font-size:14.5px;margin:10px 0 16px}
#grilling-session .gt th{background:var(--bg2);color:var(--mut);font:600 12px/1.3 var(--mono);letter-spacing:.05em;text-transform:uppercase;text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
#grilling-session .gt th .ic{width:15px;height:15px;vertical-align:-3px;margin-right:5px}
#grilling-session .gt td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:middle}
#grilling-session .gt tr:last-child td{border-bottom:0}
#grilling-session .gt tr.pick td{background:var(--acc2)}
#grilling-session .gt td:first-child{font:600 14.5px var(--sans)}
#grilling-session .tg{display:inline-block;padding:3px 8px;border-radius:99px;font:600 12.5px/1.3 var(--sans);border:1px solid var(--line);white-space:nowrap}
#grilling-session .tg.ok{color:var(--acc);border-color:rgba(111,211,195,.45);background:var(--acc2)}
#grilling-session .tg.wr{color:var(--warn);border-color:rgba(226,179,109,.45);background:var(--warn2)}
#grilling-session .tg.bad{color:#ef8a80;border-color:rgba(239,138,128,.45);background:rgba(239,138,128,.10)}
#grilling-session .dots{display:inline-flex;gap:3px;vertical-align:middle}
#grilling-session .dots i{width:9px;height:9px;border-radius:50%;background:var(--line)}
#grilling-session .dots i.on{background:var(--acc)}
#grilling-session .dots.wr i.on{background:var(--warn)}
#grilling-session .bars{display:grid;gap:10px;margin:12px 0 16px}
#grilling-session .br{display:grid;grid-template-columns:minmax(110px,32%) 1fr auto;gap:10px;align-items:center;font-size:14px}
#grilling-session .br .tk{height:14px;background:var(--bg2);border-radius:99px;overflow:hidden}
#grilling-session .br .fl{height:100%;border-radius:99px;background:var(--acc);transform-origin:left;animation:g-grow .9s cubic-bezier(.2,.8,.2,1) both}
#grilling-session .br .fl.wr{background:var(--warn)}
#grilling-session .br .vl{font:600 13px var(--mono);color:var(--mut)}
#grilling-session .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:12px 0 16px}
#grilling-session .cd{border:1px solid var(--line);border-radius:var(--r);padding:12px;background:var(--bg2);animation:g-in .5s ease both}
#grilling-session .cd .ic{color:var(--acc);width:22px;height:22px}
#grilling-session .cd b{display:block;margin:6px 0 2px}
#grilling-session .cd span{color:var(--mut);font-size:14px}
@keyframes g-grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes g-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){#grilling-session .fl,#grilling-session .cd{animation:none}}
@media (max-width:640px){#grilling-session .gt{display:block;overflow-x:auto;white-space:normal}}
'''


def agreement(st):
    if st.get('agreement') is not None:
        return int(st['agreement'])
    nodes = [n for n in st.get('tree', []) if n.get('status') != 'out']
    return round(100 * sum(1 for n in nodes if n.get('status') == 'settled') / len(nodes)) if nodes else 0


def meter_svg(pct, target):
    w = 760
    x = 20 + (w - 40) * pct / 100
    tx = 20 + (w - 40) * target / 100
    return (f'<svg class="dg" viewBox="0 0 {w} 72" role="img" aria-label="Agreement {pct} percent, target {target} percent"><title>Agreement {pct}%</title>'
            f'<rect class="meter" x="20" y="24" width="{w-40}" height="18" rx="9"/>'
            f'<rect class="meterfill" x="20" y="24" width="{max(0, x-20):.1f}" height="18" rx="9"/>'
            f'<line class="tgt" x1="{tx:.1f}" y1="14" x2="{tx:.1f}" y2="52"/>'
            f'<text class="sh" x="{tx:.1f}" y="68" text-anchor="middle">{target}% target</text>'
            f'<text class="st" x="20" y="16">{pct}% agreed</text></svg>')


def head(q, cls, icon, extra=''):
    return (f'<article class="qc {cls}" id="g{E(q["id"])}"{extra}><header><span class="qi">{ic(icon)}</span>'
            f'<div class="qh"><span class="qn">{E(q["id"])}</span><h3>{inl(q["title"])}</h3></div></header>'
            f'<dl><dt>In plain words</dt><dd>{para(q.get("plain") or q.get("body", ""))}</dd>'
            + (f'<dt>Recommendation</dt><dd class="rec">{para(q["rec"])}</dd>' if q.get('rec') else ''))


def qopen(q):
    qid = E(q['id'])
    ch = [f'<label><input type="radio" name="{qid}" value="yes"><span>Yes, go with the recommendation<span class="rtag">RECOMMENDED</span></span></label>']
    for i, o in enumerate(q.get('options') or []):
        L = chr(65 + i)
        ch.append(f'<label><input type="radio" name="{qid}" value="{L}" data-text="{E(o)}"><span><b>{L}.</b> {inl(o)}</span></label>')
    ch.append(f'<label><input type="radio" name="{qid}" value="other"><span>Something else (write it below)</span></label>')
    return (head(q, 'y cur', q.get('icon', 'q'), f' data-q="{qid}" data-title="{E(q["title"])}"')
            + f'<dt>Your answer</dt><dd><div class="ch">{"".join(ch)}</div>'
            f'<textarea data-note="{qid}" rows="2" placeholder="Optional note, reason or your own answer"></textarea></dd></dl></article>')


def qdone(q, rnd):
    ans, k = q.get('answer') or '-', q.get('kind', 'y')
    badge = '<span class="ans yes">As recommended</span>' if k == 'y' else '<span class="ans chg">Owner changed it</span>'
    return (head(q, 'y' if k == 'y' else 'c', 'ok' if k == 'y' else 'chg')
            + f'<dt>Owner\'s answer (edit to change)</dt><dd class="ow">'
            f'<textarea class="ed" data-q="{E(q["id"])}" data-title="{E(q["title"])}" data-orig="{E(ans)}" rows="2">{E(ans)}</textarea></dd></dl>'
            f'<footer>{badge}<span>Round {rnd}</span>' + (f'<span>Settles {E(q["decisions"])}</span>' if q.get('decisions') else '') + '</footer></article>')


def qrow(q, rnd):
    a = q.get('answer') or '-'
    short = a if len(a) <= 90 else a[:87].rstrip() + '...'
    b = '<span class="ans yes">rec</span>' if q.get('kind', 'y') == 'y' else '<span class="ans chg">changed</span>'
    return (f'<details class="qrow"><summary><span class="qn">{E(q["id"])}</span><span class="qt">{inl(q["title"])}</span>'
            f'<span class="qa">{inl(short)}</span>{b}</summary>{qdone(q, rnd)}</details>')


JS = r'''<script>(()=>{
const S=window.GRILL,K='grill-html:'+S.slug+':r'+S.round,q=s=>document.querySelector(s),qa=s=>[...document.querySelectorAll(s)];
const EDS='#grilling-session textarea.ed, textarea.owe';
let D={};try{D=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
function save(){const o={r:{},n:{},e:{},g:q('#g-note')?q('#g-note').value:''};
 qa('.qc.cur').forEach(c=>{const id=c.dataset.q,r=c.querySelector('input:checked');if(r)o.r[id]=r.value;const n=c.querySelector('textarea').value;if(n)o.n[id]=n});
 qa(EDS).forEach(t=>{const ch=t.value.trim()!==t.dataset.orig.trim();if(ch)o.e[t.dataset.q]=t.value;t.classList.toggle('chd',ch)});
 try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}prog();return o}
function load(){qa('.qc.cur').forEach(c=>{const id=c.dataset.q;if(D.r&&D.r[id]){const r=c.querySelector(`input[value="${D.r[id]}"]`);if(r)r.checked=true}if(D.n&&D.n[id])c.querySelector('textarea').value=D.n[id]});
 qa(EDS).forEach(t=>{if(D.e&&D.e[t.dataset.q]!=null)t.value=D.e[t.dataset.q]});if(D.g&&q('#g-note'))q('#g-note').value=D.g}
function prog(){const c=qa('.qc.cur'),a=c.filter(x=>x.querySelector('input:checked')).length,e=qa(EDS).filter(t=>t.classList.contains('chd')).length;
 const m=q('#g-prog');if(m)m.textContent=(c.length?a+' of '+c.length+' answered':'No open questions')+(e?' · '+e+' earlier answer'+(e>1?'s':'')+' changed':'')}
function out(){const o=save(),L=['GRILL-HTML ANSWERS v1 (grill-html skill: apply to '+S.state+')','topic: '+S.slug,'round: '+S.round,''];
 qa('.qc.cur').forEach(c=>{const id=c.dataset.q,v=o.r[id],n=(o.n[id]||'').trim();let a;
  if(!v)a=n?'other: '+n:'(skipped)';else if(v==='yes')a='yes';else if(v==='other')a='other: '+(n||'(no text)');else a=v+': '+c.querySelector(`input[value="${v}"]`).dataset.text;
  L.push(id+' | '+c.dataset.title,'  answer: '+a);if(n&&v&&v!=='other')L.push('  note: '+n);L.push('')});
 qa(EDS).filter(t=>t.classList.contains('chd')).forEach(t=>L.push('CHANGE Q'+String(t.dataset.q).replace(/^Q/,'')+' | '+t.dataset.title,'  was: '+t.dataset.orig,'  now: '+t.value.trim(),''));
 if(o.g.trim())L.push('GENERAL: '+o.g.trim(),'');L.push('END');return L.join('\n')}
document.addEventListener('input',e=>{if(e.target.closest('#grilling-session')||e.target.matches('textarea.owe'))save()});
document.addEventListener('change',e=>{if(e.target.closest('#grilling-session'))save()});
const msg=t=>{q('#g-msg').textContent=t};
function legacy(t){const a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;top:0;left:0;width:2px;height:2px;opacity:0';document.body.appendChild(a);a.focus();a.select();a.setSelectionRange(0,t.length);let ok=false;try{ok=document.execCommand('copy')}catch(e){}a.remove();return ok}
q('#g-copy').addEventListener('click',()=>{const t=out(),pv=q('#g-prev');pv.value=t;let ok=legacy(t);
 const done=k=>{msg(k?'Copied. Paste it into the chat with the agent.':'Your browser blocked copying. The text is selected below: press Ctrl+C.');q('#g-pv').open=true;if(!k){pv.focus();pv.select()}};
 if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(()=>done(true),()=>done(ok))}else done(ok)});
q('#g-reset').addEventListener('click',()=>{if(!confirm('Clear your answers for this round?'))return;try{localStorage.removeItem(K)}catch(e){}location.reload()});
load();save();})();</script>'''


def cell(c):
    """Table cell: "text", or {"t": text, "tone": ok|wr|bad} (pill), {"dots": 1-5, "tone"} (rating),
    {"bar": 0-100, "t": label} (mini bar)."""
    if not isinstance(c, dict):
        return inl(str(c))
    tone = c.get('tone', '')
    if 'dots' in c:
        n = int(c['dots'])
        return (f'<span class="dots {E(tone)}" title="{n} of 5">' + ''.join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(5)) + '</span>'
                + (f' <span class="muted">{inl(c["t"])}</span>' if c.get('t') else ''))
    if 'bar' in c:
        return (f'<div class="br" style="grid-template-columns:1fr auto"><div class="tk"><div class="fl {E(tone)}" style="width:{max(2, min(100, float(c["bar"])))}%"></div></div>'
                f'<span class="vl">{inl(c.get("t", ""))}</span></div>')
    return f'<span class="tg {E(tone)}">{inl(c.get("t", ""))}</span>' if tone else inl(c.get('t', ''))


def block(b):
    """Explainer blocks: table / bars / cards / note / p / html. See SKILL.md 'Section rubric'."""
    t = b.get('type')
    if t == 'table':
        hd = ''.join(f'<th>{ic(h[1]) if isinstance(h, list) else ""}{inl(h[0] if isinstance(h, list) else h)}</th>' for h in b['cols'])
        pick = set(b.get('pick', []))
        rows = ''.join(f'<tr class="{"pick" if i in pick else ""}">' + ''.join(f'<td>{cell(c)}</td>' for c in r) + '</tr>' for i, r in enumerate(b['rows']))
        cap = f'<p class="muted" style="margin:14px 0 0">{inl(b["caption"])}</p>' if b.get('caption') else ''
        return f'{cap}<table class="gt"><thead><tr>{hd}</tr></thead><tbody>{rows}</tbody></table>'
    if t == 'bars':
        mx = max(float(r[1]) for r in b['rows']) or 1
        return ((f'<p class="muted" style="margin:6px 0 0">{inl(b["title"])}</p>' if b.get('title') else '') + '<div class="bars">' + ''.join(
            f'<div class="br"><span>{inl(r[0])}</span><div class="tk"><div class="fl {E(r[3] if len(r) > 3 else "")}" style="width:{max(1.5, float(r[1]) / mx * 100)}%;animation-delay:{i * .12}s"></div></div><span class="vl">{inl(r[2] if len(r) > 2 else str(r[1]))}</span></div>'
            for i, r in enumerate(b['rows'])) + '</div>')
    if t == 'cards':
        return '<div class="cards">' + ''.join(f'<div class="cd" style="animation-delay:{i * .08}s">{ic(c.get("icon", "list"))}<b>{inl(c["title"])}</b><span>{inl(c.get("text", ""))}</span></div>' for i, c in enumerate(b['items'])) + '</div>'
    if t == 'note':
        return f'<div class="note">{inl(b["text"])}</div>'
    if t == 'p':
        return f'<p>{inl(b["text"])}</p>'
    return b.get('html', '')


def fragment(st, state_path):
    target = int(st.get('target', 95))
    pct = agreement(st)
    rounds = st.get('rounds', [])
    cur = next((r for r in rounds if r.get('status') == 'open'), None)
    skip = set(st.get('host_rounds', [])) if st.get('host') else set()
    past = [r for r in rounds if r is not cur and r['n'] not in skip]
    tree = st.get('tree', [])
    cnt = {k: sum(1 for n in tree if n.get('status') == k) for k in ('settled', 'open', 'assumed', 'out')}
    status = st.get('status', 'grilling')
    rn = (cur or {}).get('n', st.get('round', 0))
    p = [START, f'<section id="grilling-session"><h2>{"Your answers: round " + str(rn) if cur else "Grilling session"}</h2>',
         f'<style>{GCSS}</style>',
         f'<p class="sub">{inl(st.get("round_intro") or "Read the questions, pick an answer for each, then press Copy answers and paste the result into the chat. The agent updates this section with the next round.")}</p>']
    tone = 'pend' if pct < target else ''
    p.append(f'<div class="facts"><div class="fact"><div class="k">Agreement</div><div class="v {tone}">{pct}%</div><p>Target {target}%</p></div>'
             f'<div class="fact"><div class="k">Round</div><div class="v">{rn}</div><p>{"Waiting on you" if cur else ("Done" if status == "done" else "Agent working")}</p></div>'
             f'<div class="fact"><div class="k">Settled</div><div class="v">{cnt["settled"]}</div><p>of {len(tree) - cnt["out"]} branches</p></div>'
             f'<div class="fact"><div class="k">Still open</div><div class="v {"pend" if cnt["open"] + cnt["assumed"] else ""}">{cnt["open"] + cnt["assumed"]}</div><p>{cnt["assumed"]} assumed, not yet asked</p></div></div>')
    p.append(f'<figure class="chart">{meter_svg(pct, target)}</figure>')
    later = bool(cur) and rn > 1 or status == 'done'
    if tree:
        if later:
            p.append(f'<details class="more"><summary>Design tree: {cnt["settled"]} settled, {cnt["open"] + cnt["assumed"]} open</summary><div class="in">')
        p.append('<div class="legend"><span><i class="a"></i>Settled</span><span><i class="b" style="border-style:solid"></i>Open now</span><span><i class="b"></i>Assumed, not yet asked</span><span><i class="c"></i>Out of scope</span></div>'
                 '<div class="gtree">' + ''.join(f'<div class="tnode {E(n.get("status", "open"))}"><i></i><div>{inl(n["label"])}<small>{E(n.get("id", ""))}{" · " + E(n["note"]) if n.get("note") else ""}</small></div></div>' for n in tree) + '</div>')
        if later:
            p.append('</div></details>')
    if status == 'done':
        p.append(f'<div class="gdone"><b>Shared understanding confirmed.</b> {inl(st.get("done_note", ""))}</div>')
    def gx(x):
        return f'<div class="gx" id="{E(x["id"])}"><h3>{ic(x.get("icon", "list"))}{inl(x["title"])}</h3>' + (f'<p class="muted">{inl(x["sub"])}</p>' if x.get('sub') else '') + x.get('html', '') + ''.join(block(b) for b in x.get('blocks', [])) + '</div>'
    # Explainers carry "round" (default 1). From round 2 on, ones from earlier rounds
    # fold into one closed panel so the owner does not scroll past them again.
    exps = st.get('explainer', [])
    old = [x for x in exps if later and int(x.get('round', 1)) < rn]
    new = [x for x in exps if x not in old]
    if old:
        p.append(f'<details class="more"><summary>Background from earlier rounds ({len(old)}): ' + E(', '.join(x['title'] for x in old)) + '</summary><div class="in">' + ''.join(gx(x) for x in old) + '</div></details>')
    if new and old:
        p.append('<h3>New this round</h3>')
    p.extend(gx(x) for x in new)
    if cur:
        p.extend(f'<div class="note"><b>{inl(c.get("title", "Clarification"))}.</b> {inl(c["text"])}</div>' for c in cur.get('clarifications', []))
        p.append('<div class="gq">' + ''.join(qopen(q) for q in cur['questions']) + '</div>'
                 '<h3>Anything else?</h3><textarea id="g-note" rows="2" placeholder="Optional: anything the questions missed"></textarea>')
    for r in sorted(past, key=lambda r: -r['n']):
        qs = r['questions']
        ny = sum(1 for q in qs if q.get('answer') and q.get('kind', 'y') == 'y')
        p.append(f'<details class="more"><summary>Round {r["n"]}: {len(qs)} answered · {ny} as recommended · {len(qs) - ny} changed{(" · " + E(r["date"])) if r.get("date") else ""}</summary><div class="in">'
                 + ''.join(qrow(q, r['n']) for q in qs) + '</div></details>')
    if st.get('decisions') and not st.get('host'):
        p.append('<details class="more"><summary>All decisions</summary><div class="in"><table><thead><tr><th>ID</th><th>Decision</th></tr></thead><tbody>'
                 + ''.join(f'<tr><td>{E(d["id"])}</td><td style="font-family:var(--sans)">{inl(d["text"])}</td></tr>' for d in st['decisions']) + '</tbody></table></div></details>')
    if st.get('transcript'):
        p.append('<details class="more"><summary>Chat transcript</summary><div class="in">' + ''.join(f'<p><b>{E(t["who"])}:</b> {inl(t["text"])}</p>' for t in st['transcript']) + '</div></details>')
    p.append(f'<div class="gbar"><button id="g-copy">{ic("copy")}Copy answers</button><button id="g-reset">Reset</button>'
             '<span class="m"><span id="g-prog"></span> · <span id="g-msg">Answers save in this browser.</span></span></div>'
             '<details class="more" id="g-pv"><summary>Preview of what gets copied</summary><div class="in"><textarea id="g-prev" rows="10" readonly style="font:13px var(--mono)"></textarea></div></details>')
    p.append(f'<script>window.GRILL={json.dumps({"state": state_path, "slug": st["slug"], "round": rn})}</script>{JS}</section>{END}')
    return '\n'.join(p)


def favicon(st):
    """Browser-tab icon: a teal line icon from ICON on a dark rounded tile. state.json "favicon" picks it (default "q")."""
    import urllib.parse
    k = st.get('favicon', 'q')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="5" fill="#121821"/>'
           '<g transform="translate(2.4 2.4) scale(.8)" fill="none" stroke="#6fd3c3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
           + ICON.get(k, ICON['q']) + '</g></svg>')
    return f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{urllib.parse.quote(svg)}">'


def standalone(st, frag):
    theme = (HERE / 'assets/theme.css').read_text()
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(st.get("short_title") or st["title"])}</title>{favicon(st)}<style>{theme}</style></head><body><div class="wrap">'
            f'<header class="top"><div class="eyebrow"><b>GRILL</b> · {E(st.get("plan") or st["slug"])} · updated {E(st.get("updated") or datetime.date.today().isoformat())}</div></header>'
            f'<h1>{inl(st["title"])}</h1><p class="lede">{inl(st.get("goal", ""))}</p><main>{frag}</main></div></body></html>')


def embed(host_html, frag, after):
    if START in host_html and END in host_html:
        i, j = host_html.index(START), host_html.index(END) + len(END)
        return host_html[:i] + frag + host_html[j:]
    if after:
        m = re.search(rf'<section[^>]*\bid="{re.escape(after)}"', host_html)
        if m:
            depth, pos = 1, m.end()
            while depth:
                o, c = host_html.find('<section', pos), host_html.find('</section>', pos)
                if o != -1 and o < c:
                    depth, pos = depth + 1, o + 8
                else:
                    depth, pos = depth - 1, c + 10
            return host_html[:pos] + '\n' + frag + host_html[pos:]
    for tag in ('</main>', '</body>'):
        if tag in host_html:
            k = host_html.rindex(tag)
            return host_html[:k] + frag + '\n' + host_html[k:]
    return host_html + frag


def main(src):
    src = pathlib.Path(src).resolve()
    st = json.loads(src.read_text())
    state_path = str(src).replace(str(pathlib.Path.home()), '~')
    frag = fragment(st, state_path)
    if st.get('host'):
        out = (src.parent / st['host']).resolve()
        page = embed(out.read_text(), frag, st.get('host_after'))
        if 'rel="icon"' not in page and '</head>' in page:  # host pages keep their own icon
            page = page.replace('</head>', favicon(st) + '</head>', 1)
        out.write_text(page)
    else:
        out = (src.parent / st['out']).resolve() if st.get('out') else (src.parent.parent if src.parent.name == 'grill' else src.parent) / 'grill.html'
        out.write_text(standalone(st, frag))
    print(f'{out}#grilling-session', f'{agreement(st)}%')


if __name__ == '__main__':
    main(sys.argv[1])
