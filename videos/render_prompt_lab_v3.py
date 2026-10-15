"""V3: changes only five 0.9s transition windows; copies original AAC unchanged.
Run: python render_prompt_lab_v3.py
Requires ffmpeg, Pillow, NumPy and render_prompt_lab.py alongside this file.
"""
from pathlib import Path
import numpy as np, math, subprocess, sys, types
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'prompt-lab-motion-1080x1920-60fps.mp4'
DEST=ROOT/'prompt-lab-motion-v3-particulas-1080x1920-60fps.mp4'
# Derive the original scene drawing without changing the v2 source.
s=(ROOT/'render_prompt_lab.py').read_text().split('def audio():')[0]
s=s.replace('def frame(t):','def components(t, forced=None):')
s=s.replace('u=t-bounds[idx]; SCENE_TIME=u;', 'idx=idx if forced is None else forced\n u=max(0,min(bounds[idx+1]-bounds[idx],t-bounds[idx])); SCENE_TIME=u;')
s=s.replace('im.alpha_composite(scene,(dx,dy))','foreground=Image.new("RGBA",(W,H))\n foreground.alpha_composite(scene,(dx,dy))\n background=im.copy()')
s=s.replace('fx=fx.filter(ImageFilter.GaussianBlur(35)); im=Image.alpha_composite(im,fx)','fx=fx.filter(ImageFilter.GaussianBlur(35)); im=fx')
a=s.index(' # Beat-aligned cut streak'); b=s.index(' d=ImageDraw.Draw(im); d.rectangle',a)
s=s[:a]+s[b:]
s=s.replace("return im.convert('RGB')",'return background,foreground,im')
mod=types.ModuleType('v2'); mod.__file__=str(ROOT/'render_prompt_lab.py'); exec(compile(s,'v2-scenes','exec'),mod.__dict__)
W,H=1080,1920
CUTS=[5,10,14,20,26]
DURATION=.9
rng=np.random.default_rng(481)
# A fixed field causes the actual letter pixels to fragment progressively.
noise=rng.random((H//6,W//6)).astype(np.float32)
noise=np.repeat(np.repeat(noise,6,axis=0),6,axis=1)
cache={}
def smooth(p):
 p=np.clip(p,0,1); return p*p*(3-2*p)
def seeds(layer,key):
 if key not in cache:
  ar=np.asarray(layer)
  yy,xx=np.where((ar[::7,::7,1]>115)&(ar[::7,::7,3]>180))
  if len(xx)>1600:
   pick=np.linspace(0,len(xx)-1,1600).astype(int); xx=xx[pick]; yy=yy[pick]
  rr=np.random.default_rng(100+key)
  cache[key]=(xx*7,yy*7,rr.random(len(xx)),rr.uniform(-1,1,len(xx)))
 return cache[key]
def fragment(layer,progress,incoming,key):
 p=float(np.clip(progress,0,1)); e=float(smooth(p))
 ar=np.array(layer); bright=ar[:,:,1]>115
 # Fractional tile thresholds split the glyphs themselves into tiny fragments.
 threshold=(e*1.14-.07 if incoming else 1.07-e*1.14)
 keep=np.clip((threshold-noise)*15+.5,0,1)
 shell=(float(smooth(p/.65)) if incoming else 1-float(smooth(p/.75)))
 ar[:,:,3]=(ar[:,:,3]*np.where(bright,keep,shell)).astype('uint8')
 result=Image.fromarray(ar)
 pts=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(pts)
 xx,yy,rr,vx=seeds(layer,key)
 for j,(x,y,r,v) in enumerate(zip(xx,yy,rr,vx)):
  # Each fragment has its own release/capture time, with a soft overlap.
  local=float(np.clip((p-r*.35)/.65,0,1))
  if local<=0 or local>=1: continue
  travel=float(smooth(1-local if incoming else local))
  alpha=int(220*math.sin(math.pi*local)**.6)
  # Rain guides each particle toward a column while accelerating downward.
  col=round(x/36)*36
  px=x+(col-x)*travel+v*150*math.sin(travel*math.pi)
  py=y+(-1 if incoming else 1)*(130*travel+500*travel*travel)
  color=(63,255,137,alpha)
  if j%4==0:
   d.text((px,py),'01{}<>/;'[(j+int(p*6))%8],font=mod.font(13+j%3*3),fill=color)
  else:
   d.rectangle((px,py,px+3+j%3,py+4+j%4),fill=color)
  # Directional streaks are a local shutter trail, not a global smear.
  d.line((px,py-4-16*travel,px,py),fill=(45,230,110,alpha//3),width=2)
 glow=pts.filter(ImageFilter.GaussianBlur(3))
 result=Image.alpha_composite(result,glow)
 return Image.alpha_composite(result,pts)
def transition(t,boundary):
 k=CUTS.index(boundary); z=(t-(boundary-.45))/.9
 bg,old,overlay=mod.components(t,k)
 _,new,_=mod.components(t,k+1)
 # Outgoing and incoming overlap; no empty frame, cut, or exposure flash.
 outp=z/.78; inp=(z-.22)/.78
 old=fragment(old,outp,False,k*2)
 new=fragment(new,inp,True,k*2+1)
 bg=Image.alpha_composite(bg,old); bg=Image.alpha_composite(bg,new)
 return Image.alpha_composite(bg,overlay).convert('RGB')
def main():
 if '--preview' in sys.argv:
  folder=ROOT/'preview-v3'; folder.mkdir(exist_ok=True)
  for dt in [-.44,-.22,0,.22,.44]: transition(14+dt,14).resize((360,640)).save(folder/f'transicao-{dt:+.2f}.jpg')
  return
 decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(SRC),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
 encoder=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','60','-i','pipe:0','-i',str(SRC),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-t','30','-movflags','+faststart',str(DEST)],stdin=subprocess.PIPE)
 previous=None
 for i in range(1800):
  raw=decoder.stdout.read(W*H*3)
  assert len(raw)==W*H*3, f'Unexpected end at {i}'
  t=i/60; cut=next((b for b in CUTS if b-.45<=t<b+.45),None)
  if cut is not None:
   im=transition(t,cut)
   # Two temporal samples, same shutter weighting as v2.
   if previous is not None: im=Image.blend(previous,im,.75)
   previous=transition(t,cut) if previous is None else im.copy()
   raw=im.tobytes()
  else: previous=None
  encoder.stdin.write(raw)
  if i%120==0: print(f'{i}/1800',flush=True)
 decoder.stdout.close(); encoder.stdin.close()
 assert decoder.wait()==0 and encoder.wait()==0
 print('Concluído:',DEST,flush=True)
if __name__=='__main__': main()
