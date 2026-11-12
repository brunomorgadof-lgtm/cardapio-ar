// Uso: node rotate.mjs entrada.glb saida.glb <eixo x|y|z> <graus>  (gira a geometria; útil para modelos Z-up)
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { flatten, clearNodeTransform } from '@gltf-transform/functions';
const [inp, out, ax, deg] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(inp);
await doc.transform(flatten());
for (const n of doc.getRoot().listNodes()) if (n.getMesh()) clearNodeTransform(n);
const a = (+deg) * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
const rot = ([x, y, z]) => ax === 'x' ? [x, y * c - z * s, y * s + z * c] : ax === 'y' ? [x * c + z * s, y, -x * s + z * c] : [x * c - y * s, x * s + y * c, z];
const seen = new Set();
for (const m of doc.getRoot().listMeshes()) for (const p of m.listPrimitives()) for (const k of ['POSITION', 'NORMAL']) {
  const acc = p.getAttribute(k); if (!acc || seen.has(acc)) continue; seen.add(acc); const v = [];
  for (let i = 0; i < acc.getCount(); i++) { acc.getElement(i, v); acc.setElement(i, rot(v)); }
}
await io.write(out, doc);
