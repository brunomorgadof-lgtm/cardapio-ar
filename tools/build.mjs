import { NodeIO, Document } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { mergeDocuments, unpartition, dedup, prune, getBounds, weld } from '@gltf-transform/functions';
import fs from 'fs';
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const M = './modelos-origem/';
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });

// item: [model, scale, x, z, rotY(deg), y]
const dishes = {
  'hamburguer-classico': [['burger', .30, 0, 0, 20]],
  'combo-burger': [['plate', .32, 0, 0, 0], ['burger', .28, -.045, .02, 20, .029], ['fries', .30, .07, -.04, -30, .029], ['soda', .30, .2, .07, 0]],
  'pizza-margherita': [['pizza', .42, 0, 0, 0]],
  'pizza-refri': [['pizza', .42, 0, 0, 0], ['soda', .30, .26, -.12, 0]],
  'sanduiche-natural': [['sandwich', .33, 0, 0, 15]],
  'hot-dog': [['hot-dog', .31, 0, 0, 10]],
  'baguete': [['sub', .37, 0, 0, 70]],
  'taco': [['taco', .37, 0, 0, 0]],
  'combinado-8': [['plate', .30, 0, 0, 0],
    ['sushi-salmon', .30, -.06, -.04, 90, .029], ['sushi-salmon', .30, -.06, .0, 90, .029], ['sushi-egg', .30, -.06, .04, 90, .029],
    ['maki-salmon', .30, .03, -.05, 0, .029], ['maki-salmon', .30, .07, -.05, 0, .029], ['maki-roe', .30, .03, -.01, 0, .029],
    ['maki-roe', .30, .07, -.01, 0, .029], ['maki-vegetable', .30, .05, .035, 0, .029]],
  'niguiri-salmao': [['sushi-salmon', .30, -.02, 0, 0], ['sushi-salmon', .30, .02, 0, 0]],
  'uramaki': [['maki-salmon', .30, -.035, 0, 0], ['maki-roe', .30, 0, 0, 0], ['maki-vegetable', .30, .035, 0, 0]],
};
for (const [name, items] of Object.entries(dishes)) {
  const doc = new Document(); doc.createBuffer();
  const scene = doc.createScene(name);
  for (const [m, s, x, z, r = 0, y = 0] of items) {
    const src = await io.read(M + m + '.glb');
    const map = mergeDocuments(doc, src);
    const srcScene = map.get(src.getRoot().listScenes()[0]);
    const g = doc.createNode(m).setScale([s, s, s]).setTranslation([x, y, z])
      .setRotation([0, Math.sin(r*Math.PI/360), 0, Math.cos(r*Math.PI/360)]);
    for (const c of srcScene.listChildren()) { srcScene.removeChild(c); g.addChild(c); }
    srcScene.dispose(); scene.addChild(g);
  }
  doc.getRoot().setDefaultScene(scene);
  for (const s of doc.getRoot().listScenes()) if (s !== scene) s.dispose();
  for (const e of doc.getRoot().listExtensionsUsed()) if (e.extensionName === 'VRM') e.dispose();
  await doc.transform(unpartition(), dedup(), prune());
  const b = getBounds(scene);
  await io.write(`${OUT}/${name}.glb`, doc);
  console.log(name, b.max.map((v,i)=>((v-b.min[i])*100).toFixed(1)+'cm').join(' x '), (fs.statSync(`${OUT}/${name}.glb`).size/1024).toFixed(0)+'KB');
}
