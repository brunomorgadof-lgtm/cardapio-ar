import trimesh, numpy as np, cv2, numba, sys, json
from numba import njit
TS = 2048
sc = trimesh.load('el-padre-ia-final.glb'); mesh = list(sc.geometry.values())[0]
V = np.asarray(mesh.vertices, np.float64); F = np.asarray(mesh.faces, np.int64)
UV = np.asarray(mesh.visual.uv, np.float64); VN = np.asarray(mesh.vertex_normals, np.float64)
raw = list(trimesh.load('ia.glb').geometry.values())[0].visual.material.baseColorTexture.convert('RGB')
T0 = np.asarray(raw).astype(np.float32)
print('mesh', V.shape, F.shape, V.min(0), V.max(0))

@njit(cache=True)
def raster_uv(UVp, F, TS, fid, bar):
    for f in range(F.shape[0]):
        a, b, c = UVp[F[f,0]], UVp[F[f,1]], UVp[F[f,2]]
        x0 = max(int(np.floor(min(a[0],b[0],c[0]))),0); x1 = min(int(np.ceil(max(a[0],b[0],c[0]))),TS-1)
        y0 = max(int(np.floor(min(a[1],b[1],c[1]))),0); y1 = min(int(np.ceil(max(a[1],b[1],c[1]))),TS-1)
        den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-12: continue
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                px, py = x+0.5, y+0.5
                l1 = ((b[1]-c[1])*(px-c[0]) + (c[0]-b[0])*(py-c[1]))/den
                l2 = ((c[1]-a[1])*(px-c[0]) + (a[0]-c[0])*(py-c[1]))/den
                l3 = 1-l1-l2
                if l1 >= -0.02 and l2 >= -0.02 and l3 >= -0.02:
                    if fid[y,x] < 0:
                        fid[y,x] = f; bar[y,x,0]=l1; bar[y,x,1]=l2; bar[y,x,2]=l3

@njit(cache=True)
def raster_depth(P, D, F, W, H, zb):
    for f in range(F.shape[0]):
        a, b, c = P[F[f,0]], P[F[f,1]], P[F[f,2]]
        da, db, dc = D[F[f,0]], D[F[f,1]], D[F[f,2]]
        x0 = max(int(np.floor(min(a[0],b[0],c[0]))),0); x1 = min(int(np.ceil(max(a[0],b[0],c[0]))),W-1)
        y0 = max(int(np.floor(min(a[1],b[1],c[1]))),0); y1 = min(int(np.ceil(max(a[1],b[1],c[1]))),H-1)
        den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-12: continue
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                px, py = x+0.5, y+0.5
                l1 = ((b[1]-c[1])*(px-c[0]) + (c[0]-b[0])*(py-c[1]))/den
                l2 = ((c[1]-a[1])*(px-c[0]) + (a[0]-c[0])*(py-c[1]))/den
                l3 = 1-l1-l2
                if l1 >= 0 and l2 >= 0 and l3 >= 0:
                    d = l1*da + l2*db + l3*dc
                    if d > zb[y,x]: zb[y,x] = d

# 1) posição/normal de cada texel
UVp = np.c_[UV[:,0]*TS, (1-UV[:,1])*TS]
fid = -np.ones((TS,TS), np.int64); bar = np.zeros((TS,TS,3))
raster_uv(UVp, F, TS, fid, bar)
ok = fid >= 0; fi = fid[ok]; bb = bar[ok]
POS = (V[F[fi,0]]*bb[:,0:1] + V[F[fi,1]]*bb[:,1:2] + V[F[fi,2]]*bb[:,2:3])
NRM = (VN[F[fi,0]]*bb[:,0:1] + VN[F[fi,1]]*bb[:,1:2] + VN[F[fi,2]]*bb[:,2:3]); NRM /= np.linalg.norm(NRM,axis=1,keepdims=True)+1e-9
base = T0[ok]
print('texels', ok.sum())

def basis(psi, phi):
    d = np.array([np.cos(phi)*np.sin(psi), np.sin(phi), np.cos(phi)*np.cos(psi)])
    r = np.cross([0,1,0], d); r /= np.linalg.norm(r); u = np.cross(d, r)
    return d, r, u
def project(X, cam):
    d, r, u = basis(cam['psi'], cam['phi'])
    return np.c_[cam['cx'] + cam['s']*(X@r), cam['cy'] - cam['s']*(X@u)], X@d
def fit(name, psis, phis):
    img = cv2.imread(f'img_{name}.png'); m = cv2.imread(f'mask_{name}.png',0) > 0
    ys, xs = np.nonzero(m); H, W = m.shape
    best = None
    vc = T0[np.clip(((1-UV[:,1])*TS).astype(int),0,TS-1), np.clip((UV[:,0]*TS).astype(int),0,TS-1)].mean(1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    for psi in psis:
        for phi in phis:
            d, r, u = basis(psi, phi)
            pu, pv = V@r, -(V@u)
            s = 0.5*((xs.max()-xs.min())/(pu.max()-pu.min()) + (ys.max()-ys.min())/(pv.max()-pv.min()))
            cx = (xs.max()+xs.min())/2 - s*(pu.max()+pu.min())/2
            cy = (ys.max()+ys.min())/2 - s*(pv.max()+pv.min())/2
            cam = dict(psi=psi, phi=phi, s=s, cx=cx, cy=cy)
            P, D = project(V, cam)
            front = (VN@d) > 0.4
            px = np.clip(P[front,0].astype(int),0,W-1); py = np.clip(P[front,1].astype(int),0,H-1)
            a = gray[py,px]; b = vc[front]
            sel = m[py,px]
            if sel.sum() < 200: continue
            a, b = a[sel], b[sel]
            corr = np.corrcoef(a, b)[0,1]
            if best is None or corr > best[0]: best = (corr, cam)
    return best
def refine(name, cam):
    # ajuste fino de escala/centro pela silhueta (IoU)
    m = cv2.imread(f'mask_{name}.png',0) > 0; H, W = m.shape
    best = None
    for ds in [0.94,0.97,1,1.03,1.06]:
      for dx in [-12,-6,0,6,12]:
        for dy in [-12,-6,0,6,12]:
          c = dict(cam); c['s'] *= ds; c['cx'] += dx; c['cy'] += dy
          P, D = project(V, c); zb = np.full((H,W), -1e9)
          raster_depth(P, D, F, W, H, zb); sil = zb > -1e8
          iou = (sil&m).sum()/(sil|m).sum()
          if best is None or iou > best[0]: best = (iou, c)
    return best
cams = {}
r = fit('185010', np.radians(np.arange(0,360,6)), np.radians([6,10,14,18,22]))
print('A coarse', r[0], {k: float(v) for k,v in r[1].items()})
p0 = r[1]['psi']
r = fit('185010', p0+np.radians(np.arange(-6,7,2)), np.radians(np.arange(4,26,3)))
iou, cams['A'] = refine('185010', r[1]); print('A', r[0], iou, {k: float(v) for k,v in cams['A'].items()})
r = fit('184842', p0+np.radians(np.arange(-40,41,4)), np.radians(np.arange(24,62,4)))
iou, cams['C'] = refine('184842', r[1]); print('C', r[0], iou, {k: float(v) for k,v in cams['C'].items()})
r = fit('185006', p0+np.radians(np.arange(-40,41,4)), np.radians(np.arange(4,26,3)))
iou, cams['B'] = refine('185006', r[1]); print('B', r[0], iou, {k: float(v) for k,v in cams['B'].items()})
np.savez('rebake_cache.npz', ok=ok, POS=POS, NRM=NRM, base=base)
json.dump({k:{kk:float(vv) for kk,vv in c.items()} for k,c in cams.items()}, open('cams.json','w'))
