import cv2, numpy as np
exec(open('profile.py').read())
m = cv2.resize(cv2.imread('mask_184842.png',0),None,fx=.25,fy=.25)>127; D=4
sel = (Ys < 300)  # so pao de cima
Rr, Hh = Rs[sel], H[sel]
best=None
for sp in np.arange(0.40,0.80,0.03):
  cp=np.sqrt(1-sp*sp)
  for sc in np.arange(0.90,1.10,0.02):
    for cx in range(440,486,6):
      for yb in range(1500,2100,15):
        img=np.zeros(m.shape,np.uint8)
        for r,h in zip(Rr[::4],Hh[::4]):
          c=(int(cx/D),int((yb-h*cp*sc)/D)); ax=(int(r*sc/D),int(r*sp*sc/D))
          cv2.ellipse(img,c,ax,0,0,360,1,-1)
        p=img>0; lim = p.any(1).nonzero()[0].max()
        mm = m.copy(); mm[lim+1:]=False
        iou=(p&mm).sum()/((p|mm).sum()+1)
        if best is None or iou>best[0]: best=(iou,sp,sc,cx,yb)
print(best)
