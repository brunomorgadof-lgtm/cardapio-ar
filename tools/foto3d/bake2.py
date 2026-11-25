import numpy as np, cv2, json
from common3d import *
c = np.load('rebake_cache.npz'); ok, POS, NRM, base = c['ok'], c['POS'], c['NRM'], c['base']
cams = json.load(open('cams.json'))
# C: mesmo lado da foto A (vista de cima); reajusta só elevação/escala
best=None
for phi in np.radians(np.arange(30,66,3)):
    cc = dict(cams['C']); cc['psi'] = cams['A']['psi']; cc['phi'] = phi
    m = cv2.imread('mask_184842.png',0)>0; ys,xs=np.nonzero(m)
    d,r,u = basis(cc['psi'],phi); pu,pv = V@r, -(V@u)
    s = (xs.max()-xs.min())/(pu.max()-pu.min()); cc['s']=s
    cc['cx']=(xs.max()+xs.min())/2 - s*(pu.max()+pu.min())/2; cc['cy']=ys.min() - s*pv.min()
    iou, cc = refine('184842', cc)
    if best is None or iou>best[0]: best=(iou,cc)
cams['C']=best[1]; print('C', best[0], np.degrees(best[1]['phi']))
def photo_layer(name, cam, gain=1.0, power=2.0, maxcos=1.0):
    img = cv2.imread(f'img_{name}.png'); m = cv2.imread(f'mask_{name}.png',0)
    if name == '184842':  # tira o palito da foto de cima
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); box = np.zeros(m.shape, np.uint8); box[640:860, 395:500] = 1
        pm = ((hsv[...,1] < 150) & (hsv[...,2] > 120) & (box>0)).astype(np.uint8)*255
        pm = cv2.dilate(pm, np.ones((11,11),np.uint8)); img = cv2.inpaint(img, pm, 9, cv2.INPAINT_TELEA); m[pm>0] = 0
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
    m = cv2.erode(m, np.ones((9,9),np.uint8)) > 0
    H, W = m.shape
    P, D = project(V, cam); zb = np.full((H,W), -1e9); raster_depth(P, D, F, W, H, zb)
    d,_,_ = basis(cam['psi'], cam['phi'])
    tp, td = project(POS, cam)
    x = np.clip(tp[:,0],0,W-1.001); y = np.clip(tp[:,1],0,H-1.001)
    xi, yi = x.astype(int), y.astype(int)
    vis = (td >= zb[yi,xi] - 0.0025) & m[yi,xi]
    cosv = np.clip(NRM@d, 0, 1)
    w = gain * cosv**power * vis
    n = len(x); pad = (-n) % 4096
    xx = np.r_[x, np.zeros(pad)].astype(np.float32).reshape(-1,4096); yy = np.r_[y, np.zeros(pad)].astype(np.float32).reshape(-1,4096)
    col = cv2.remap(img, xx, yy, cv2.INTER_LINEAR).reshape(-1,3)[:n]
    return col, w
cA, wA = photo_layer('185010', cams['A'], 1.0, 2.0)
cB, wB = np.zeros_like(cA), np.zeros(len(cA))
cC, wC = photo_layer('184842', cams['C'], 1.0, 2.0)
topo = np.clip((NRM[:,1]-0.45)/0.3,0,1) * np.clip((POS[:,1]-0.6*POS[:,1].max())/(0.1*POS[:,1].max()),0,1)
wC = wC*topo
wA = wA*np.clip(1-topo*0.7,0,1)
print('cobertura A,B,C', (wA>0.05).mean(), (wB>0.05).mean(), (wC>0.05).mean(), 'qualquer', ((wA+wB+wC)>0.05).mean())
# base da IA: tira a sombra "queimada" em 3D (média da luminosidade por vizinhança 3D) e casa a cor com as fotos
lab = cv2.cvtColor(np.clip(base,0,255).astype(np.uint8)[None], cv2.COLOR_RGB2LAB)[0].astype(np.float32)
logL = np.log(lab[:,0]+6)
g = 0.008  # 8 mm
key = np.floor((POS - POS.min(0))/g).astype(np.int64); dims = key.max(0)+1
lin = key[:,0]*dims[1]*dims[2] + key[:,1]*dims[2] + key[:,2]
sm = np.bincount(lin, logL, dims.prod()); ct = np.bincount(lin, None, dims.prod())
grid = (sm/np.maximum(ct,1)).reshape(dims); cnt = ct.reshape(dims)
from scipy.ndimage import gaussian_filter
gs = gaussian_filter(grid*(cnt>0), 1.2); gc = gaussian_filter((cnt>0).astype(float), 1.2)
low = (gs/np.maximum(gc,1e-3)).ravel()[lin]
# referência: luminosidade das fotos onde há foto
wsum = wA+wB+wC
ph = (cA*wA[:,None]+cB*wB[:,None]+cC*wC[:,None])/np.maximum(wsum,1e-6)[:,None]
seen = wsum > 0.3
phlab = cv2.cvtColor(np.clip(ph[seen],0,255).astype(np.uint8)[None], cv2.COLOR_RGB2LAB)[0].astype(np.float32)
logL2 = logL - 0.9*(low - np.median(low))
# casa histograma (L, a, b) da base com as partes vistas nas fotos
out = lab.copy(); out[:,0] = np.exp(logL2)
for ch in range(3):
    q = np.linspace(0.5,99.5,200)
    sq = np.percentile(out[:,ch], q); rq = np.percentile(phlab[:,ch], q)
    sq = np.maximum.accumulate(sq + np.arange(200)*1e-5)
    out[:,ch] = np.interp(out[:,ch], sq, rq)
out[:,1] = 128+(out[:,1]-128)*1.3; out[:,2] = 128+(out[:,2]-128)*1.35; out[:,0] = 255*(out[:,0]/255)**1.15
chroma = np.hypot(out[:,1]-128, out[:,2]-128); t_ = np.clip(1-chroma/28,0,1)*np.clip((out[:,0]-120)/40,0,1)
out[:,1] = out[:,1]*(1-t_)+148*t_; out[:,2] = out[:,2]*(1-t_)+178*t_; out[:,0] = out[:,0]*(1-0.25*t_)
basefix = cv2.cvtColor(np.clip(out,0,255).astype(np.uint8)[None], cv2.COLOR_LAB2RGB)[0].astype(np.float32)
wb = 0.08
col = (ph*wsum[:,None] + basefix*wb) / (wsum+wb)[:,None]
tex = np.zeros((TS,TS,3), np.float32); tex[ok] = col
# preenche fora das ilhas (evita bordas escuras)
u8 = np.clip(tex,0,255).astype(np.uint8)
small = cv2.resize(u8,(512,512)); sm_ = cv2.resize((~ok).astype(np.uint8),(512,512),interpolation=cv2.INTER_NEAREST)
fill = cv2.resize(cv2.inpaint(small, sm_, 3, cv2.INPAINT_TELEA),(TS,TS)); u8[~ok] = fill[~ok]
cv2.imwrite('ia_tex_fix.png', cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
json.dump({k:{kk:float(vv) for kk,vv in c.items()} for k,c in cams.items()}, open('cams.json','w'))
