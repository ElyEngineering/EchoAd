import cv2, json, numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
casc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
MANUAL={'zupec':(512,60,42),'kannas':(617,40,42),'weise':(122,55,52)}
ZOOM={'hornstein':0.8}  # cx,cy,face width (eyeballed; Haar fails on tiny profile faces)
src={
 'omerza':('originals/omerza_kaxe_noframe.png',None),
 'campbell':('originals/campbell_city.jpg',None),
 'forsman':('originals/forsman_city.jpg',None),
 'zupec':('originals/echo_council_forum_group.jpg',(470,0,580,155)),
 'hornstein':('originals/hornstein_kaxe.jpg',None),
 'kannas':('originals/echo_school_forum_group.jpg',(570,0,670,133)),
 'weise':('originals/echo_4day_08.jpg',(80,0,200,120)),
}
FACE_FRAC=0.5   # face box width / square side
CY=0.45          # face center vertical position
OUT=1200
res={}
for k,(f,roi) in src.items():
    img=cv2.imread(f); H,W=img.shape[:2]
    if k in MANUAL:
        cx,cy,w=MANUAL[k]; x,y,h=cx-w/2,cy-w/2,w
    else:
        x=None
    if x is None:
     g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
     ox=oy=0; sub=g
     if roi: ox,oy=roi[0],roi[1]; sub=g[roi[1]:roi[3],roi[0]:roi[2]]
     up=4 if roi else 1
     s2=cv2.resize(sub,None,fx=up,fy=up,interpolation=cv2.INTER_CUBIC) if up>1 else sub
     faces=casc.detectMultiScale(s2,1.05,4,minSize=(30,30))
     if len(faces)==0: print(k,'NO FACE'); continue
     x,y,w,h=max(faces,key=lambda r:r[2]*r[3]); x,y,w,h=[v/up for v in (x,y,w,h)]; x+=ox;y+=oy
    side=w/FACE_FRAC*ZOOM.get(k,1); cx=x+w/2; cy=y+h/2
    x0=int(round(cx-side/2)); y0=int(round(cy-CY*side)); s=int(round(side))
    if 0 < -y0 < 0.06*s: y0=0
    if 0 < -x0 < 0.06*s: x0=0
    if 0 < x0+s-W < 0.06*s: x0=W-s
    pad=max(0,-x0,-y0,x0+s-W,y0+s-H)
    if pad:
        im=cv2.copyMakeBorder(img,pad,pad,pad,pad,cv2.BORDER_REFLECT)
        bl=cv2.GaussianBlur(im,(0,0),max(8,pad/6))
        m=np.ones(im.shape[:2],np.float32); m[pad:pad+H,pad:pad+W]=0
        m=cv2.GaussianBlur(m,(0,0),max(4,pad/12))[...,None]
        im=(im*(1-m)+bl*m).astype(np.uint8)
    else: im=img
    crop=im[y0+pad:y0+pad+s,x0+pad:x0+pad+s]
    pil=Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB)).resize((OUT,OUT),Image.LANCZOS)
    # COLOR normalization (no grayscale): partial gray-world white balance on the face region,
    # then match L* mean/std in LAB so brightness/contrast agree across all 7 headshots.
    arr=np.asarray(pil).astype(np.float32)
    face=arr[int(OUT*0.25):int(OUT*0.65),int(OUT*0.3):int(OUT*0.7)].reshape(-1,3)
    means=face.mean(0); target=means.mean()
    gain=1+0.5*(target/means-1)          # 50% correction keeps natural skin warmth
    arr=np.clip(arr*gain,0,255).astype(np.uint8)
    lab=cv2.cvtColor(arr,cv2.COLOR_RGB2LAB).astype(np.float32)
    L=lab[...,0]; L=(L-L.mean())/(L.std()+1e-6)*48+135; lab[...,0]=np.clip(L,0,255)
    out=Image.fromarray(cv2.cvtColor(lab.astype(np.uint8),cv2.COLOR_LAB2RGB))
    out=ImageEnhance.Color(out).enhance(1.05)
    if s<375: out=out.filter(ImageFilter.UnsharpMask(radius=2,percent=60,threshold=2))
    out.save(f'square/{k}.jpg',quality=92,dpi=(300,300))
    res[k]={'source_file':f,'face_box':[round(x),round(y),round(w),round(h)],'crop_box':[x0,y0,x0+s,y0+s],'edge_padding_px':int(pad),
            'native_square_px':s,'print_ready_1.25in_300dpi':s>=375}
    print(k,res[k])
json.dump(res,open('square/crops.json','w'),indent=1)
c=Image.new('RGB',(7*200,200),'white')
for i,k in enumerate(src):
    try: c.paste(Image.open(f'square/{k}.jpg').resize((200,200)),(i*200,0))
    except: pass
c.save('/workspace/tmpn/sq.jpg')
