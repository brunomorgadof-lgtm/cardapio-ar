import cv2, numpy as np
from PIL import Image, ImageOps
im = np.array(ImageOps.exif_transpose(Image.open('fotos/20261124_184842.jpg')).convert('RGB'))[:,:,::-1]
s = 1000/im.shape[1]; im = cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
print(im.shape)
rect=(20,640,880,1040)
mask=np.zeros(im.shape[:2],np.uint8); bg=np.zeros((1,65)); fg=np.zeros((1,65))
cv2.grabCut(im,mask,rect,bg,fg,6,cv2.GC_INIT_WITH_RECT)
m=np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(m); big=1+np.argmax(st[1:,4]); m=np.where(lab==big,255,0).astype(np.uint8)
ff=m.copy(); h,w=m.shape; cv2.floodFill(ff,np.zeros((h+2,w+2),np.uint8),(0,0),255); m=m|cv2.bitwise_not(ff)
cv2.imwrite('mask_184842.png',m); cv2.imwrite('img_184842.png',im)
ov=im.copy(); ov[m==0]=(ov[m==0]*0.25).astype(np.uint8); cv2.imwrite('ov_184842.jpg',cv2.resize(ov[500:1800],None,fx=0.5,fy=0.5))
