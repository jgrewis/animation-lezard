"""Plaque de fond : le décor de la vidéo, vidé du personnage, puis prolongé."""
import numpy as np, os, sys, json
from PIL import Image, ImageFilter
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
from scipy_free import border_fill

RAMP=range(104,229)
CROP=(150,0,1050,720)          # la vidéo livrée : le trou doit tenir dedans
CANVAS=(2480,1620); OFF=(300,700)

def hsv(a):
    r,g,b=a[...,0],a[...,1],a[...,2]
    mx=a.max(-1); d=mx-a.min(-1)
    h=np.zeros_like(mx)
    i=(mx==r)&(d>0); h[i]=((g-b)[i]/d[i])%6
    i=(mx==g)&(d>0); h[i]=((b-r)[i]/d[i])+2
    i=(mx==b)&(d>0); h[i]=((r-g)[i]/d[i])+4
    return h*60, np.where(mx>0,d/np.maximum(mx,1e-6),0)

def load(n): return np.asarray(Image.open(f"{SP}/all/{n+1:03d}.png").convert('RGB')).astype(np.float32)/255.

# 1. trou = union des silhouettes (dilatation 20) + bande d'ombre au sol
union=np.zeros((720,1280),bool)
for n in RAMP:
    h,s=hsv(load(n))
    union |= ~border_fill((h>=10)&(h<=32)&(s>0.55))
union[:,1080:]=False
union[560:720,180:1010]=True
union[560:720,1080:1280]=True      # filigrane de génération, en bas à droite
hole=union
for _ in range(5):
    hole=np.asarray(Image.fromarray((hole*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))>100
ys,xs=np.nonzero(hole)
print(f"trou : x {xs.min()}-{xs.max()}  y {ys.min()}-{ys.max()}")
hole_video=hole.copy(); hole_video[:,1060:]=False
yv,xv=np.nonzero(hole_video)
assert xv.min()>=CROP[0] and xv.max()<=CROP[2], "le trou dépasse le cadre vidéo"

# 2. on comble par interpolation horizontale, sur l'image 124 (pose de face)
base=load(124); out=base.copy(); ok=~hole; xr=np.arange(1280)
for y in range(720):
    m=ok[y]
    for c in range(3):
        out[y,:,c]=np.interp(xr,xr[m],base[y,m,c])
soft=np.asarray(Image.fromarray((out*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32)/255.
w=(np.asarray(Image.fromarray((hole*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12))).astype(np.float32)/255.)[...,None]
frame=np.clip(out*(1-w)+soft*w,0,1)
# hors du trou, on remet les pixels d'origine au bit près : c'est ce qui rend
# le raccord avec la vidéo invisible, le flou précédent les avait contaminés
frame[~hole]=base[~hole]

# 3. prolongement : on étire les bords en fondu vers la couleur des coins
W,H=CANVAS; ox,oy=OFF
cy,cx=np.mgrid[0:H,0:W]
# le prolongement part d'une version très floue : étirer les pixels bruts
# du bord produisait des traînées verticales visibles
flou=np.asarray(Image.fromarray((frame*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(34))).astype(np.float32)/255.
sx=np.clip(cx-ox,0,1279); sy=np.clip(cy-oy,0,719)
dedans=(cx>=ox)&(cx<ox+1280)&(cy>=oy)&(cy<oy+720)
plate=np.where(dedans[...,None],frame[sy,sx],flou[sy,sx])
dist=np.sqrt(np.maximum(0,np.maximum(ox-cx,cx-(ox+1279)))**2 +
             np.maximum(0,np.maximum(oy-cy,cy-(oy+719)))**2)
coins=np.concatenate([frame[:40,:40].reshape(-1,3),frame[:40,-40:].reshape(-1,3)])
bord=coins.mean(0)*0.72
f=np.exp(-dist/520.)[...,None]
plate=plate*f+bord*(1-f)
plate=np.asarray(Image.fromarray((np.clip(plate,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))

P="/Users/jeanphilippegrewis/Documents/Claude/Projects/Animation lezard"
Image.fromarray(plate).save(f"{P}/assets/decor.webp",'WEBP',lossless=True,method=6)
Image.fromarray((base[0:720,150:1050]*255).astype(np.uint8)).save(f"{P}/assets/pose-face.webp",'WEBP',quality=82,method=6)
json.dump({"canvas":[W,H],"videoOrigin":[ox+CROP[0],oy+CROP[1]],"videoSize":[CROP[2]-CROP[0],CROP[3]-CROP[1]],
           "edge":[round(float(v),4) for v in bord]},open(f"{SP}/decor.json","w"))
print("couleur de bord :", "#%02x%02x%02x"%tuple(int(v*255) for v in bord))
print("origine vidéo dans la plaque :", (ox+CROP[0], oy+CROP[1]))
for f_ in ("decor.webp","pose-face.webp"):
    print(f"{f_} : {os.path.getsize(P+'/assets/'+f_)/1024:.0f} Ko")
