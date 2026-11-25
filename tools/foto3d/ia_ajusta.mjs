// Uso: node foto3d/ia_ajusta.mjs entrada.glb textura_corrigida.png saida.glb <largura_m> [giro_graus]
// giro_graus: gira o lanche em volta do eixo vertical para a frente ficar virada para o cliente
// Ajusta o modelo gerado por IA: troca a textura (cor corrigida), tira o brilho metálico,
// suaviza as normais, remove migalhas soltas, centraliza, apoia na mesa e põe em tamanho real.
import { NodeIO } from '@gltf-transform/core';
import { weld, prune, getBounds, textureCompress } from '@gltf-transform/functions';
import sharp from 'sharp'; import fs from 'fs';
const [inp, texPath, out, width, giro = '0'] = process.argv.slice(2);
const g = (+giro) * Math.PI / 180, cg = Math.cos(g), sg = Math.sin(g);
const io = new NodeIO(); const doc = await io.read(inp);
const tex = doc.getRoot().listTextures()[0];
tex.setImage(fs.readFileSync(texPath)).setMimeType('image/png');
for (const m of doc.getRoot().listMaterials()) m.setMetallicFactor(0).setRoughnessFactor(0.62).setDoubleSided(true);
await doc.transform(weld({ tolerance: 1e-5 }));
// remove pedaços pequenos soltos (migalhas)
const prim = doc.getRoot().listMeshes()[0].listPrimitives()[0];
const idx = prim.getIndices().getArray(), pos = prim.getAttribute('POSITION');
const n = pos.getCount(), par = new Int32Array(n).map((_, i) => i);
// vértices na mesma posição (costuras da textura) contam como ligados
const key = new Map(), tmp = [];
for (let i = 0; i < n; i++) { pos.getElement(i, tmp); const k = tmp.map(x => Math.round(x * 1e4)).join(','); if (key.has(k)) par[i] = key.get(k); else key.set(k, i); }
const f = x => { while (par[x] !== x) { par[x] = par[par[x]]; x = par[x]; } return x; };
for (let i = 0; i < idx.length; i += 3) { const a = f(idx[i]), b = f(idx[i+1]), c = f(idx[i+2]); par[b] = a; par[f(c)] = a; }
const cnt = new Map(); for (let i = 0; i < idx.length; i += 3) { const r = f(idx[i]); cnt.set(r, (cnt.get(r) || 0) + 1); }
const keep = [...cnt.entries()].filter(([, c]) => c > 300).map(([r]) => r);
const kept = []; for (let i = 0; i < idx.length; i += 3) if (keep.includes(f(idx[i]))) kept.push(idx[i], idx[i+1], idx[i+2]);
console.log('pedaços', cnt.size, 'mantidos', keep.length, 'triângulos', kept.length / 3, 'de', idx.length / 3);
prim.getIndices().setArray(new Uint32Array(kept));
await doc.transform(prune(), weld());
{ // normais suaves (somadas por posição, para não marcar as costuras da textura)
  const pr = doc.getRoot().listMeshes()[0].listPrimitives()[0];
  const ix = pr.getIndices().getArray(), ps = pr.getAttribute('POSITION'), nv = ps.getCount();
  const p = new Float32Array(nv * 3); for (let i = 0, t = []; i < nv; i++) { ps.getElement(i, t); p.set(t, i * 3); }
  const kmap = new Map(), kid = new Int32Array(nv);
  for (let i = 0; i < nv; i++) { const k = Math.round(p[i*3]*1e5)+','+Math.round(p[i*3+1]*1e5)+','+Math.round(p[i*3+2]*1e5); if (!kmap.has(k)) kmap.set(k, kmap.size); kid[i] = kmap.get(k); }
  const acc = new Float32Array(kmap.size * 3);
  for (let f = 0; f < ix.length; f += 3) {
    const a = ix[f]*3, b = ix[f+1]*3, c = ix[f+2]*3;
    const ux = p[b]-p[a], uy = p[b+1]-p[a+1], uz = p[b+2]-p[a+2], vx = p[c]-p[a], vy = p[c+1]-p[a+1], vz = p[c+2]-p[a+2];
    const nx = uy*vz-uz*vy, ny = uz*vx-ux*vz, nz = ux*vy-uy*vx;
    for (const v of [ix[f], ix[f+1], ix[f+2]]) { const k = kid[v]*3; acc[k] += nx; acc[k+1] += ny; acc[k+2] += nz; }
  }
  const out = new Float32Array(nv * 3);
  for (let i = 0; i < nv; i++) { const k = kid[i]*3, l = Math.hypot(acc[k], acc[k+1], acc[k+2]) || 1; out[i*3] = acc[k]/l; out[i*3+1] = acc[k+1]/l; out[i*3+2] = acc[k+2]/l; }
  pr.setAttribute('NORMAL', doc.createAccessor().setType('VEC3').setArray(out).setBuffer(doc.getRoot().listBuffers()[0]));
}
const scene = doc.getRoot().listScenes()[0];
let b = getBounds(scene);
const s = (+width) / Math.max(b.max[0] - b.min[0], b.max[2] - b.min[2]);
const cx = (b.max[0] + b.min[0]) / 2, cz = (b.max[2] + b.min[2]) / 2, v = [];
const P = doc.getRoot().listMeshes()[0].listPrimitives()[0].getAttribute('POSITION');
for (let i = 0; i < P.getCount(); i++) { P.getElement(i, v); const x = (v[0]-cx)*s, z = (v[2]-cz)*s; P.setElement(i, [x*cg + z*sg, (v[1]-b.min[1])*s, -x*sg + z*cg]); }
const N = doc.getRoot().listMeshes()[0].listPrimitives()[0].getAttribute('NORMAL');
if (N) for (let i = 0; i < N.getCount(); i++) { N.getElement(i, v); N.setElement(i, [v[0]*cg + v[2]*sg, v[1], -v[0]*sg + v[2]*cg]); }
for (const nd of doc.getRoot().listNodes()) nd.setMatrix([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);
await doc.transform(textureCompress({ encoder: sharp, targetFormat: 'jpeg', quality: 88 }));
await io.write(out, doc);
b = getBounds(scene);
console.log(out, b.max.map((x, i) => ((x - b.min[i]) * 100).toFixed(1) + 'cm').join(' x '));
