import fs from 'node:fs';
const j = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const m = j.snapshot.meta, nf = m.node_fields, ef = m.edge_fields, N = nf.length, E = ef.length;
const nT = m.node_types[0], eT = m.edge_types[0], S = j.strings, nodes = j.nodes, edges = j.edges;
const iType = nf.indexOf('type'), iName = nf.indexOf('name'), iSize = nf.indexOf('self_size'), iEC = nf.indexOf('edge_count');
const eType = ef.indexOf('type'), eName = ef.indexOf('name_or_index'), eTo = ef.indexOf('to_node');
const cnt = nodes.length / N, first = new Uint32Array(cnt + 1);
for (let i = 0, e = 0; i < cnt; i++) { first[i] = e; e += nodes[i * N + iEC] * E; } first[cnt] = edges.length;
const ret = Array.from({ length: cnt }, () => []);
for (let i = 0; i < cnt; i++) for (let e = first[i]; e < first[i + 1]; e += E) { const t = eT[edges[e + eType]]; if (t === 'weak') continue; ret[edges[e + eTo] / N].push([i, t === 'element' || t === 'hidden' ? '[' + edges[e + eName] + ']' : S[edges[e + eName]]]); }
const desc = i => `${nT[nodes[i * N + iType]]}:${String(S[nodes[i * N + iName]]).slice(0, 60).replace(/\n/g, ' ')}`;
const big = []; let tot = 0, byType = {};
for (let i = 0; i < cnt; i++) { const s = nodes[i * N + iSize]; const t = nT[nodes[i * N + iType]]; byType[t] = (byType[t] || 0) + s; if (s > 1 << 20) big.push(i); tot += s; }
console.log('total MB', (tot / 1048576) | 0, Object.fromEntries(Object.entries(byType).map(([k, v]) => [k, (v / 1048576) | 0])));
big.sort((a, b) => nodes[b * N + iSize] - nodes[a * N + iSize]);
console.log('objects >1MB:', big.length, 'sum MB', (big.reduce((a, i) => a + nodes[i * N + iSize], 0) / 1048576) | 0);
for (const i of big.slice(0, +process.argv[3] || 12)) {
  let path = [], cur = i, seen = new Set();
  for (let d = 0; d < 8; d++) { const r = ret[cur].find(([p]) => !seen.has(p)); if (!r) break; seen.add(r[0]); path.push(`${r[1]} <- ${desc(r[0])}`); cur = r[0]; }
  console.log(((nodes[i * N + iSize]) / 1048576).toFixed(1) + 'MB', desc(i), '\n   ' + path.join('\n   '));
}
