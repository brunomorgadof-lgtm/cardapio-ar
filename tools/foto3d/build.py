import cv2, numpy as np, trimesh, sys
from PIL import Image
SIN = 0.22; COS = np.sqrt(1-SIN**2)
YB = 832
def dome(y0, R, H, n=28, e=2.4):
    return [(y0-H*(i/n), R*(1-(i/n)**e)**(1/e)) for i in range(n+1)]
prof = [(YB+6,0),(YB+6,250),(YB+5,340),(YB+2,382),(YB-8,399),(YB-25,405),(760,407),(700,407),(660,405),
        (645,396),(620,390),(590,385),(565,377),(545,368),(525,372),(500,374),(480,378),(466,395),(458,418),
        (445,428),(400,432),(345,432),(322,428),(310,424),(300,421),(294,424),(282,430),(262,433),(240,433)]
prof += dome(232,433,196)[1:]
prof = np.array(prof, float)
d = np.r_[0, np.cumsum(np.hypot(*np.diff(prof,axis=0).T))]
NV = 300; s = np.linspace(0, d[-1], NV)
Ys = np.interp(s, d, prof[:,0]); Rs = np.interp(s, d, prof[:,1])
k = np.array([1,2,1.]); k/=k.sum()
Ys2 = np.convolve(np.pad(Ys,1,mode='edge'),k,'valid'); Rs2 = np.convolve(np.pad(Rs,1,mode='edge'),k,'valid')
Ys2[[0,-1]]=Ys[[0,-1]]; Rs2[[0,-1]]=0; Ys, Rs = Ys2, Rs2
H = (YB+6 - Ys)/COS
dr = np.gradient(Rs); dh = np.gradient(H)
nr, ny = dh, -dr; L = np.hypot(nr,ny)+1e-9; nr/=L; ny/=L

def load(name, cx, yb, sc, sinp, fix=None):
    im = cv2.imread(f'img_{name}.png')
    m = cv2.imread(f'mask_{name}.png',0)
    if fix: im, m = fix(im, m)
    im = im.astype(np.float32)
    m = cv2.erode(m, np.ones((7,7),np.uint8))
    _, lab = cv2.distanceTransformWithLabels((m==0).astype(np.uint8)*255, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    fgm = m!=0; ys, xs = np.nonzero(fgm)
    lut = np.zeros((lab.max()+1,2),int); lut[lab[fgm]] = np.c_[ys,xs]
    ext = im[lut[lab][...,0], lut[lab][...,1]]
    return dict(im=ext, cx=cx, yb=yb, sc=sc, sin=sinp, cos=np.sqrt(1-sinp**2))
def tira_palito(im, m):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    box = np.zeros(m.shape, np.uint8); box[640:860, 395:500] = 1
    pm = ((hsv[...,1] < 150) & (hsv[...,2] > 120) & (box>0)).astype(np.uint8)*255
    pm = cv2.dilate(pm, np.ones((9,9),np.uint8))
    m = m.copy(); m[pm>0] = 0
    m[:700] = np.where(m[:700]>0, 255, 0); m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((15,15),np.uint8))
    return cv2.inpaint(im, pm, 9, cv2.INPAINT_TELEA), m
# A: frente (foto 185010), B: usada para o lado de tras (185006), C: de cima (184842)
A = load('185010', 937, YB+6, 1.0, SIN)
B = load('185006', 948, 852, 1.03, SIN)
C = load('184842', 458, 1545, 1.0, 0.52, tira_palito)
cv2.imwrite('c_fix.jpg', cv2.resize(C['im'][600:1400].astype(np.uint8),None,fx=.4,fy=.4))
TW, TH = 2048, 2048
u = (np.arange(TW)+0.5)/TW; v = (np.arange(TH)+0.5)/TH
th = 2*np.pi*u
vi = v*(NV-1); i0 = np.clip(vi.astype(int),0,NV-2); f = vi-i0
lerp = lambda a: a[i0]*(1-f)+a[i0+1]*f
TT, RR = np.meshgrid(th, lerp(Rs)); _, HH = np.meshgrid(th, lerp(H)); _, NR = np.meshgrid(th, lerp(nr)); _, NY = np.meshgrid(th, lerp(ny)); _, YS = np.meshgrid(th, lerp(Ys))
HHs = np.maximum(HH, (YB+6-792)/COS*np.ones_like(HH))  # base do pao: nao pega a sombra do prato
def sample(P, ang, squeeze=0.96, HH=None):
    HH = HHs if HH is None else HH
    a = np.angle(np.exp(1j*ang))
    x = RR*(0.5*np.sin(a) + 0.5*np.clip(a/(np.pi/2),-1.2,1.2))*squeeze; z = RR*np.cos(a)
    px = P['cx'] + x*P['sc']; py = P['yb'] - HH*P['cos']*P['sc'] + z*P['sin']*P['sc']
    return cv2.remap(P['im'], px.astype(np.float32), py.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
cA = sample(A, TT); cB = sample(B, TT-np.pi)
wA = (0.5+0.5*np.cos(TT))**4; wB = (0.5+0.5*np.cos(TT-np.pi))**4
tex = (cA*wA[...,None] + cB*wB[...,None])/(wA+wB)[...,None]
# topo do pao: foto de cima (vista quase inteira do domo)
cC = sample(C, TT, 1.0, HH)
dotC = NR*np.cos(TT)*C['cos'] + NY*C['sin']
tC = (np.clip((NY-0.2)/0.4,0,1) * np.clip((dotC-0.15)/0.3,0,1) * (YS<240))[...,None]
tex = tex*(1-tC) + cC*tC
fallback = np.array([95,165,215],np.float32)
t = np.clip((NY+0.95)/0.35,0,1)[...,None]
tex = tex*t + fallback*(1-t)
tex = np.clip(tex,0,255).astype(np.uint8)
cv2.imwrite('tex.jpg', tex, [cv2.IMWRITE_JPEG_QUALITY, 90])
g = cv2.cvtColor(tex, cv2.COLOR_BGR2GRAY).astype(np.float32)/255
hgt = g - cv2.GaussianBlur(g, (0,0), 6)
gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3)
st = 2.5; nx, nyy = -gx*st, gy*st; nz = np.ones_like(nx); L = np.sqrt(nx*nx+nyy*nyy+1)
nm = np.dstack([nz/L, nyy/L, nx/L])*0.5+0.5  # BGR -> RGB = (nx, ny, nz)
cv2.imwrite('nrm.jpg', (nm*255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])
DIAM = float(sys.argv[1]) if len(sys.argv)>1 else 0.11
NU = 192
k = DIAM/(2*433)
verts=[]; uvs=[]
for i in range(NV):
    for j in range(NU+1):
        a = 2*np.pi*j/NU
        verts.append((Rs[i]*np.sin(a)*k, H[i]*k, Rs[i]*np.cos(a)*k)); uvs.append((j/NU, 1-i/(NV-1)))
faces=[]; W=NU+1
for i in range(NV-1):
    for j in range(NU):
        a=i*W+j; b=a+1; c=a+W; d2=c+1
        faces += [(a,b,c),(b,d2,c)]
mat = trimesh.visual.material.PBRMaterial(baseColorTexture=Image.open('tex.jpg'), normalTexture=Image.open('nrm.jpg'), roughnessFactor=0.6, metallicFactor=0.0)
mesh = trimesh.Trimesh(np.array(verts), np.array(faces), visual=trimesh.visual.TextureVisuals(uv=np.array(uvs), material=mat), process=False)
top = H[-1]*k
pal = trimesh.creation.box((0.010, 0.05, 0.0022))
pal.apply_transform(trimesh.transformations.rotation_matrix(np.radians(4),(0,0,1)))
pal.apply_translation((0, top+0.023-0.025, -0.003))
pal.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=[214,178,128,255], roughnessFactor=0.85, metallicFactor=0.0))
sc = trimesh.Scene(); sc.add_geometry(mesh, node_name='hamburguer'); sc.add_geometry(pal, node_name='palito')
sc.export('el-padre-burger.glb')
print('altura cm %.1f diam cm %.1f' % (top*100, DIAM*100))
