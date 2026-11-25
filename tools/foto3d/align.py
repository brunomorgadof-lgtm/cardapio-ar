import numpy as np, cv2, json, sys
from common3d import *
c = np.load('rebake_cache.npz'); ok, POS, NRM, base = c['ok'], c['POS'], c['NRM'], c['base']
cams = json.load(open('cams.json'))
rng = np.random.default_rng(0); sub = rng.choice(len(POS), 250000, replace=False)
P_, N_, B_ = POS[sub], NRM[sub], base[sub]
def feats(rgb):
    r,g,b = rgb[...,0], rgb[...,1], rgb[...,2]
    return np.stack([g-r, r+g-2*b], -1)
fb = feats(B_)
def score(name, cam, img, m):
    H, W = m.shape
    P, D = project(V, cam); zb = np.full((H,W), -1e9); raster_depth(P, D, F, W, H, zb)
    d,_,_ = basis(cam['psi'], cam['phi'])
    tp, td = project(P_, cam)
    xi = np.clip(tp[:,0].astype(int),0,W-1); yi = np.clip(tp[:,1].astype(int),0,H-1)
    vis = (td >= zb[yi,xi]-0.0025) & m[yi,xi] & ((N_@d) > 0.3)
    if vis.sum() < 2000: return -1
    fp = feats(img[yi[vis], xi[vis]]); fq = fb[vis]
    return np.mean([np.corrcoef(fp[:,k], fq[:,k])[0,1] for k in range(2)])
def search(name, cam, phis, dys, dss, dpsis):
    img = cv2.cvtColor(cv2.imread(f'img_{name}.png'), cv2.COLOR_BGR2RGB).astype(np.float32)
    m = cv2.imread(f'mask_{name}.png',0) > 0
    best = (score(name, cam, img, m), cam)
    for phi in phis:
      for dpsi in dpsis:
        for ds in dss:
          for dy in dys:
            c2 = dict(cam); c2['phi'] = phi; c2['psi'] = cam['psi']+dpsi; c2['s'] = cam['s']*ds; c2['cy'] = cam['cy']+dy
            sc = score(name, c2, img, m)
            if sc > best[0]: best = (sc, c2)
    return best
A = cams['A']; print('A start', score('185010', A, cv2.cvtColor(cv2.imread('img_185010.png'), cv2.COLOR_BGR2RGB).astype(np.float32), cv2.imread('mask_185010.png',0)>0))
b = search('185010', A, np.radians([0,5,10,15,20]), [-60,-30,0,30,60], [0.95,1,1.05], np.radians([-10,0,10]))
print('A', b[0], np.degrees(b[1]['phi']), np.degrees(b[1]['psi']), b[1]['cy']-A['cy'], b[1]['s']/A['s'])
b = search('185010', b[1], b[1]['phi']+np.radians([-3,0,3]), [-15,0,15], [0.98,1,1.02], np.radians([-4,0,4]))
print('A fino', b[0], np.degrees(b[1]['phi']), np.degrees(b[1]['psi']))
cams['A'] = b[1]
C = dict(cams['C']); C['psi'] = cams['A']['psi']
b = search('184842', C, np.radians([35,40,45,50,55]), [-80,-40,0,40,80], [0.95,1,1.05], np.radians([-15,0,15]))
print('C', b[0], np.degrees(b[1]['phi']), np.degrees(b[1]['psi']))
cams['C'] = b[1]
json.dump({k:{kk:float(vv) for kk,vv in c.items()} for k,c in cams.items()}, open('cams.json','w'))
