import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, weld, getBounds, textureCompress, dedup, center, transformMesh, flatten, simplify } from '@gltf-transform/functions';
import { mat4 } from 'gl-matrix';
const [inp, out, R0, targetW] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(inp);
await doc.transform(flatten());
// bake world transforms
for (const n of doc.getRoot().listNodes()) { const m=n.getMesh(); if(!m) continue; const w=n.getWorldMatrix(); for (const p of m.listPrimitives()) { const pos=p.getAttribute('POSITION'); const v=[0,0,0]; for(let i=0;i<pos.getCount();i++){pos.getElement(i,v); const x=v[0],y=v[1],z=v[2]; pos.setElement(i,[w[0]*x+w[4]*y+w[8]*z+w[12], w[1]*x+w[5]*y+w[9]*z+w[13], w[2]*x+w[6]*y+w[10]*z+w[14]]);} const nr=p.getAttribute('NORMAL'); if(nr){for(let i=0;i<nr.getCount();i++){nr.getElement(i,v);const x=v[0],y=v[1],z=v[2];let a=w[0]*x+w[4]*y+w[8]*z,b=w[1]*x+w[5]*y+w[9]*z,c=w[2]*x+w[6]*y+w[10]*z;const l=Math.hypot(a,b,c)||1;nr.setElement(i,[a/l,b/l,c/l]);}} } n.setMatrix([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]); }
// find burger: vertices with y above 25% of height
let ymax=-1e9; const prims=doc.getRoot().listMeshes().flatMap(m=>m.listPrimitives());
for(const p of prims){const a=p.getAttribute('POSITION');const v=[];for(let i=0;i<a.getCount();i++){a.getElement(i,v);ymax=Math.max(ymax,v[1]);}}
let sx=0,sz=0,c=0,minx=1e9,maxx=-1e9,minz=1e9,maxz=-1e9;
for(const p of prims){const a=p.getAttribute('POSITION');const v=[];for(let i=0;i<a.getCount();i++){a.getElement(i,v);if(v[1]>ymax*0.6){sx+=v[0];sz+=v[2];c++;minx=Math.min(minx,v[0]);maxx=Math.max(maxx,v[0]);minz=Math.min(minz,v[2]);maxz=Math.max(maxz,v[2]);}}}
const cx=sx/c, cz=sz/c, bw=Math.max(maxx-minx,maxz-minz);
console.log('burger center',cx.toFixed(2),cz.toFixed(2),'burger width',bw.toFixed(2),'ymax',ymax.toFixed(2));
const R=+R0*bw;
// remove triangles with centroid outside radius
for(const p of prims){const a=p.getAttribute('POSITION');const idx=p.getIndices();const arr=idx.getArray();const keep=[];const v0=[],v1=[],v2=[];
 for(let t=0;t<arr.length;t+=3){a.getElement(arr[t],v0);a.getElement(arr[t+1],v1);a.getElement(arr[t+2],v2);const x=(v0[0]+v1[0]+v2[0])/3-cx,z=(v0[2]+v1[2]+v2[2])/3-cz; if(Math.hypot(x,z)<=R) keep.push(arr[t],arr[t+1],arr[t+2]);}
 idx.setArray(new Uint32Array(keep));}
// scale to target burger width (m), move burger center to origin, floor to y=0
const s=(+targetW)/ymax; let ymin=1e9;
for(const p of prims){const a=p.getAttribute('POSITION');const v=[];for(let i=0;i<a.getCount();i++){a.getElement(i,v);a.setElement(i,[(v[0]-cx)*s,v[1]*s,(v[2]-cz)*s]);}}
await doc.transform(prune({keepAttributes:false}), weld(), dedup());
// drop TEXCOORD_1 unused
for(const p of prims){ if(p.getAttribute('TEXCOORD_1')) p.setAttribute('TEXCOORD_1',null); }
const b=getBounds(doc.getRoot().listScenes()[0]); const dy=-b.min[1];
for(const p of prims){const a=p.getAttribute('POSITION');const v=[];for(let i=0;i<a.getCount();i++){a.getElement(i,v);a.setElement(i,[v[0],v[1]+dy,v[2]]);}}
const sharp = (await import('sharp')).default;
await doc.transform(prune(), textureCompress({encoder: sharp, targetFormat:'jpeg', resize:[2048,2048], quality: 82}));
await io.write(out, doc);
const b2=getBounds(doc.getRoot().listScenes()[0]); console.log('final cm', b2.max.map((v,i)=>((v-b2.min[i])*100).toFixed(1)).join(' x '));
