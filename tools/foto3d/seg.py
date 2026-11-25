import cv2, numpy as np, sys
name, x0,y0,x1,y1 = sys.argv[1], *map(int, sys.argv[2:6])  # rect in 1600-wide preview coords
im = cv2.imread(f'fotos/20261124_{name}.jpg'); s = 2000/im.shape[1]
im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
k = 2000/1600
rect = (int(x0*k), int(y0*k), int((x1-x0)*k), int((y1-y0)*k))
mask = np.zeros(im.shape[:2], np.uint8); bg=np.zeros((1,65)); fg=np.zeros((1,65))
cv2.grabCut(im, mask, rect, bg, fg, 6, cv2.GC_INIT_WITH_RECT)
m = np.where((mask==1)|(mask==3), 255, 0).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7,7),np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m); big = 1+np.argmax(st[1:,4]); m = np.where(lab==big,255,0).astype(np.uint8)
# fill holes
ff = m.copy(); h,w=m.shape; cv2.floodFill(ff, np.zeros((h+2,w+2),np.uint8), (0,0), 255); m = m | cv2.bitwise_not(ff)
cv2.imwrite(f'mask_{name}.png', m); cv2.imwrite(f'img_{name}.png', im)
ov = im.copy(); ov[m==0] = (ov[m==0]*0.25).astype(np.uint8); cv2.imwrite(f'ov_{name}.jpg', cv2.resize(ov,None,fx=0.6,fy=0.6))
