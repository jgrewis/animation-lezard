import numpy as np
from collections import deque
def largest(al, thr=0.5):
    m=al>thr
    H,W=m.shape
    lab=np.zeros((H,W),np.int32); cur=0; best=(0,0)
    for sy,sx in np.argwhere(m):
        if lab[sy,sx]: continue
        cur+=1; cnt=0; q=deque([(sy,sx)]); lab[sy,sx]=cur
        while q:
            y,x=q.popleft(); cnt+=1
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<H and 0<=nx<W and m[ny,nx] and not lab[ny,nx]:
                    lab[ny,nx]=cur; q.append((ny,nx))
        if cnt>best[0]: best=(cnt,cur)
    keep=(lab==best[1])
    from PIL import Image, ImageFilter
    roi=np.asarray(Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)))>100
    return al*roi

def border_fill(mask):
    """largest background = orange pixels reachable from the image border"""
    H,W=mask.shape
    seen=np.zeros((H,W),bool)
    q=deque()
    for x in range(W):
        for y in (0,H-1):
            if mask[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    for y in range(H):
        for x in (0,W-1):
            if mask[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    while q:
        y,x=q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<H and 0<=nx<W and mask[ny,nx] and not seen[ny,nx]:
                seen[ny,nx]=True; q.append((ny,nx))
    return seen
