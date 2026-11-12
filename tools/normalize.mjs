// Uso: node normalize.mjs entrada.glb saida.glb <largura_m> [texturaPx]
// Aplica transformações, centraliza, apoia no chão, escala para a largura real e comprime texturas.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, weld, getBounds, textureCompress, dedup, flatten, clearNodeTransform, metalRough } from '@gltf-transform/functions';
import sharp from 'sharp';
const [inp, out, width, px = '2048'] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(inp);
// Materiais antigos (specular/glossiness) não são suportados pelo model-viewer: converte para metal/rough
if (doc.getRoot().listExtensionsUsed().some(e => e.extensionName === 'KHR_materials_pbrSpecularGlossiness')) await doc.transform(metalRough());
await doc.transform(flatten());
for (const n of doc.getRoot().listNodes()) if (n.getMesh()) clearNodeTransform(n);
const scene = doc.getRoot().listScenes()[0];
const b = getBounds(scene);
const s = (+width) / Math.max(b.max[0] - b.min[0], b.max[2] - b.min[2]);
const cx = (b.max[0] + b.min[0]) / 2, cz = (b.max[2] + b.min[2]) / 2;
const done = new Set();
for (const m of doc.getRoot().listMeshes()) for (const p of m.listPrimitives()) {
  const a = p.getAttribute('POSITION'); if (done.has(a)) continue; done.add(a); const v = [];
  for (let i = 0; i < a.getCount(); i++) { a.getElement(i, v); a.setElement(i, [(v[0] - cx) * s, (v[1] - b.min[1]) * s, (v[2] - cz) * s]); }
}
const big = +px;
await doc.transform(prune(), weld(), dedup(),
  textureCompress({ encoder: sharp, targetFormat: 'jpeg', resize: [big, big], quality: 82, slots: /^(baseColor|emissive)/ }),
  textureCompress({ encoder: sharp, targetFormat: 'jpeg', resize: [big / 2, big / 2], quality: 85, slots: /^(normal|metallicRoughness|occlusion)/ }),
  textureCompress({ encoder: sharp, resize: [512, 512], slots: /^specular/ }));
await io.write(out, doc);
const b2 = getBounds(scene);
console.log(out, b2.max.map((v, i) => ((v - b2.min[i]) * 100).toFixed(1) + 'cm').join(' x '));
