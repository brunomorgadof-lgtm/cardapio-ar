// Uso: node level.mjs entrada.glb saida.glb
// Nivela escaneamentos tortos: ajusta um plano (PCA) à base e gira para a normal apontar para cima (+Y).
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { flatten, clearNodeTransform } from '@gltf-transform/functions';
const [inp, out] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(inp);
await doc.transform(flatten());
for (const n of doc.getRoot().listNodes()) if (n.getMesh()) clearNodeTransform(n);
const accs = new Set(); for (const m of doc.getRoot().listMeshes()) for (const p of m.listPrimitives()) accs.add(p.getAttribute('POSITION'));
const pts = []; for (const a of accs) { const v = []; for (let i = 0; i < a.getCount(); i++) { a.getElement(i, v); pts.push([...v]); } }
const mean = [0, 1, 2].map(k => pts.reduce((s, p) => s + p[k], 0) / pts.length);
const C = [[0,0,0],[0,0,0],[0,0,0]];
for (const p of pts) for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) C[i][j] += (p[i]-mean[i])*(p[j]-mean[j]);
// Jacobi eigen
let A = C.map(r => [...r]), V = [[1,0,0],[0,1,0],[0,0,1]];
for (let it = 0; it < 50; it++) { let p=0,q=1; for (const [i,j] of [[0,1],[0,2],[1,2]]) if (Math.abs(A[i][j])>Math.abs(A[p][q])) {p=i;q=j;}
  if (Math.abs(A[p][q]) < 1e-12) break; const th=(A[q][q]-A[p][p])/(2*A[p][q]); const t=Math.sign(th||1)/(Math.abs(th)+Math.sqrt(th*th+1)); const c=1/Math.sqrt(t*t+1), s=t*c;
  for (let k=0;k<3;k++){const akp=A[k][p],akq=A[k][q];A[k][p]=c*akp-s*akq;A[k][q]=s*akp+c*akq;} for (let k=0;k<3;k++){const apk=A[p][k],aqk=A[q][k];A[p][k]=c*apk-s*aqk;A[q][k]=s*apk+c*aqk;}
  for (let k=0;k<3;k++){const vkp=V[k][p],vkq=V[k][q];V[k][p]=c*vkp-s*vkq;V[k][q]=s*vkp+c*vkq;} }
const ev=[0,1,2].map(i=>A[i][i]); const mi=ev.indexOf(Math.min(...ev)); let n=[V[0][mi],V[1][mi],V[2][mi]];
if (n[1] < 0) n = n.map(x => -x);
console.log('normal', n.map(x => x.toFixed(3)).join(' '));
// rotação que leva n para (0,1,0): Rodrigues
const up=[0,1,0], ax=[n[1]*up[2]-n[2]*up[1], n[2]*up[0]-n[0]*up[2], n[0]*up[1]-n[1]*up[0]];
const sn=Math.hypot(...ax), cs=n[1]; const k=sn?ax.map(x=>x/sn):[1,0,0];
const R=(v)=>{const d=k[0]*v[0]+k[1]*v[1]+k[2]*v[2]; const cr=[k[1]*v[2]-k[2]*v[1],k[2]*v[0]-k[0]*v[2],k[0]*v[1]-k[1]*v[0]]; return [0,1,2].map(i=>v[i]*cs+cr[i]*sn+k[i]*d*(1-cs));};
const seen=new Set(); for (const m of doc.getRoot().listMeshes()) for (const p of m.listPrimitives()) for (const key of ['POSITION','NORMAL']) { const a=p.getAttribute(key); if(!a||seen.has(a)) continue; seen.add(a); const v=[]; for(let i=0;i<a.getCount();i++){a.getElement(i,v); a.setElement(i,R(v));} }
await io.write(out, doc);
