from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, subprocess, wave, pathlib, shutil
W,H,FPS,DUR=1080,1920,60,18
OUT=pathlib.Path(__file__).resolve().parent
pathlib.Path('work').mkdir(exist_ok=True)
TARGET=OUT/'kind_to_rich.mp4'
if TARGET.exists(): raise SystemExit('Refusing to overwrite existing output')
rng=np.random.default_rng(44)
G=(206,163,85); WHITE=(246,244,235)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ease(x):
 x=np.clip(x,0,1); return x*x*(3-2*x)
def textmask(lines,size):
 im=Image.new('L',(W,H)); d=ImageDraw.Draw(im); f=ImageFont.truetype(font,size)
 for j,s in enumerate(lines): d.text((W/2,H/2+(j-(len(lines)-1)/2)*size*1.23),s,font=f,fill=255,anchor='mm',stroke_width=0)
 return im
masks=[textmask(['what u wanna','be'],112),textmask(['when u','grownup?'],136),textmask(['kind'],245),textmask(['rich'],270)]
pts=[]
for m in masks:
 yy,xx=np.where(np.array(m)[::5,::5]>120); sel=rng.choice(len(xx),min(4200,len(xx)),replace=False)
 pts.append(np.c_[xx[sel]*5,yy[sel]*5,rng.normal(0,210,len(sel)),rng.normal(0,160,len(sel)),rng.uniform(.5,1.5,len(sel))])
y,x=np.mgrid[0:480,0:270]; glow=np.exp(-(((x-205)/140)**2+((y-180)/180)**2))*0.9+np.exp(-(((x-20)/110)**2+((y-400)/150)**2))*.3
bg=Image.fromarray(np.uint8(np.stack([glow*22+2,glow*15+2,glow*7+3],2))).resize((W,H),Image.Resampling.BICUBIC)
dust=np.c_[rng.uniform(0,W,140),rng.uniform(0,H,140),rng.uniform(.3,1.6,140)]
def asset(kind):
 im=Image.new('RGBA',(1100,1100)); d=ImageDraw.Draw(im)
 if kind=='cash':
  for k in range(5):
   a=Image.new('RGBA',(850,410)); q=ImageDraw.Draw(a)
   q.rounded_rectangle((12,12,838,398),28,fill=(21,28,24),outline=G,width=4)
   for n in range(7): q.rounded_rectangle((28+n*5,28+n*5,822-n*5,382-n*5),20,outline=(72+n*8,67+n*6,43+n*3),width=1)
   q.ellipse((320,65,530,345),outline=G,width=3)
   for z in range(24):
    yy=55+z*13; q.line((70,yy,275,yy+10*math.sin(z)),fill=(86,94,68),width=2); q.line((570,yy,775,yy-10*math.sin(z)),fill=(86,94,68),width=2)
   q.polygon([(425,105),(475,205),(425,305),(375,205)],outline=G,width=3)
   a=a.rotate(-19+k*8,resample=Image.Resampling.BICUBIC,expand=True); im.alpha_composite(a,((1100-a.width)//2,100+k*85))
 elif kind=='coins':
  for k in range(10):
   cx=210+(k%3)*280; cy=790-(k//3)*155
   for j in range(8): d.ellipse((cx-130,cy-65-j*13,cx+130,cy+65-j*13),fill=(72+j*8,48+j*6,20+j*3),outline=(185,139,62),width=2)
   d.ellipse((cx-109,cy-144,cx+109,cy-48),outline=G,width=3)
   d.polygon([(cx,cy-132),(cx+33,cy-96),(cx,cy-61),(cx-33,cy-96)],fill=G)
 elif kind=='watch':
  d.rounded_rectangle((420,0,680,1100),45,fill=(21,22,21),outline=(125,103,64),width=5)
  for yy in range(0,1100,45): d.line((430,yy,670,yy),fill=(96,77,44),width=3)
  d.ellipse((235,235,865,865),fill=(151,118,62),outline=(239,205,140),width=5)
  d.ellipse((264,264,836,836),fill=(8,11,12),outline=(65,60,43),width=10)
  for j in range(60):
   th=j*math.tau/60; r=247; rr=218 if j%5==0 else 235
   d.line((550+r*math.sin(th),550-r*math.cos(th),550+rr*math.sin(th),550-rr*math.cos(th)),fill=G,width=7 if j%5==0 else 2)
  d.line((550,550,425,420),fill=WHITE,width=14); d.line((550,550,715,360),fill=G,width=10); d.ellipse((537,537,563,563),fill=G)
  d.rounded_rectangle((860,495,900,595),8,fill=G)
 elif kind=='car':
  d.ellipse((70,720,1030,850),fill=(12,13,14))
  for cx in [280,830]:
   d.ellipse((cx-98,620,cx+98,816),fill=(4,5,7),outline=(105,96,75),width=8)
   d.ellipse((cx-62,656,cx+62,780),outline=G,width=5)
   for j in range(10):
    a=j*math.tau/10; d.line((cx,718,cx+58*math.sin(a),718+58*math.cos(a)),fill=(138,128,106),width=4)
  d.polygon([(70,670),(120,555),(330,510),(465,380),(680,370),(840,510),(1015,565),(1040,695),(935,720),(900,650),(800,620),(740,720),(380,720),(350,635),(235,620),(185,715),(80,715)],fill=(25,28,30),outline=(162,141,98),width=4)
  d.polygon([(370,510),(490,404),(670,400),(790,510)],fill=(7,12,16),outline=(113,110,94),width=3)
  d.line((600,405,620,510),fill=G,width=3); d.line((130,565,970,576),fill=(194,169,117),width=3)
  d.polygon([(95,601),(205,580),(190,610),(90,625)],fill=(239,229,195)); d.line((962,592,1020,610),fill=(166,45,25),width=9)
 return im
assets={k:asset(k) for k in ['cash','coins','watch','car']}
def frame(t):
 im=bg.copy(); d=ImageDraw.Draw(im)
 for xx,yy,r in dust:
  yy=(yy-t*(10+r*7))%H; xx=xx+18*math.sin(t*.3+yy*.01); c=int(55+35*math.sin(t+yy))
  d.ellipse((xx,yy,xx+r*2,yy+r*2),fill=(c,int(c*.74),int(c*.39)))
 if t<10:
  idx=0 if t<3 else 1 if t<6 else 2 if t<8 else 3
  start=[0,3,6,8][idx]; end=[3,6,8,10][idx]; u=t-start
  entering=u<.7; exiting=t>end-.6
  a=ease(u/.7) if entering else 1-ease((t-(end-.6))/.6) if exiting else 1
  if a>0:
   mask=masks[idx].point(lambda v:int(v*a)); im.paste(G if idx==3 else WHITE,(0,0,W,H),mask)
  if entering or exiting:
   p=(1-ease(u/.7)) if entering else ease((t-(end-.6))/.6)
   dd=ImageDraw.Draw(im)
   for xx,yy,vx,vy,r in pts[idx]:
    px=xx+vx*p; py=yy+vy*p+80*p*p; c=int(225*(1-p*.85)); rr=1+r*p
    dd.ellipse((px,py,px+rr*2,py+rr*2),fill=(c,int(c*.88),int(c*.68)))
 else:
  beat=int((t-10)/.5); local=((t-10)%.5)/.5
  seq=['cash','coins','watch','car','cash','watch','car','coins','watch','cash','coins','car','watch','coins','cash','car']
  k=seq[min(beat,15)]; a=assets[k]
  scale=1.03+.09*local; sz=int(1100*scale); a=a.resize((sz,sz),Image.Resampling.BICUBIC)
  a=a.rotate((-3+6*local) if k=='cash' else (1.5*math.sin(t*2)),Image.Resampling.BICUBIC)
  im.paste(a,((W-sz)//2+int(18*math.sin(t)),(H-sz)//2),a)
  dd=ImageDraw.Draw(im)
  # moving specular slashes and golden shower on the musical downbeats
  for j in range(26):
   xx=(j*137+local*190)%W; yy=(j*283+local*530)%H; v=int((1-local)*100+30)
   dd.line((xx,yy,xx+3,yy+12),fill=(v,int(v*.77),int(v*.4)),width=2)
  flare=Image.new('RGB',(W,H),(85,57,20)); im=Image.blend(im,flare,.13*math.exp(-local*14))
 fade=ease(t/.35)*(1-ease((t-17.5)/.5))
 if fade<1: im=Image.blend(Image.new('RGB',(W,H)),im,fade)
 return im
# Original synthesized score, 120 BPM, no samples or recordings.
sr=48000; tt=np.arange(sr*DUR)/sr; music=np.zeros(len(tt)); rg=np.random.default_rng(9)
def add(at,sig,gain=1):
 i=int(at*sr); n=min(len(sig),len(music)-i)
 if n>0: music[i:i+n]+=sig[:n]*gain
for b in np.arange(0,DUR,.5):
 s=np.arange(int(.42*sr))/sr; phase=2*np.pi*(46*s+95*.027*(1-np.exp(-s/.027))); kick=np.sin(phase)*np.exp(-s*10)
 add(b,kick,.7 if b>=8 else .38)
 s=np.arange(int(.09*sr))/sr; noise=rg.normal(0,1,len(s)); hp=noise-np.roll(noise,1); add(b+.25,hp*np.exp(-s*65),.055 if b>=8 else .022)
 if int(b*2)%2:
  s=np.arange(int(.18*sr))/sr; add(b,rg.normal(0,1,len(s))*np.exp(-s*29),.105)
 if b>=8:
  s=np.arange(int(.46*sr))/sr; hz=[46.249,46.249,41.203,43.654][int(b//2)%4]; bass=np.tanh(2.2*np.sin(2*np.pi*hz*s)+.5*np.sin(2*np.pi*hz*2*s)); add(b,bass*np.exp(-s*5)*(1-np.exp(-s*80)),.22)
for hz in [92.499,110,138.591]: music+=.018*np.sin(2*np.pi*hz*tt+2*np.sin(tt*.2))*np.minimum(tt/3,1)
for at in [2.4,5.4,7.4,9.4]:
 s=np.arange(int(.6*sr))/sr; add(at,rg.normal(0,1,len(s))*(s/.6)**3,.07)
music=np.tanh(music*1.3); music*=np.minimum(tt/.2,1)*np.minimum((DUR-tt)/.4,1); music*=.88/max(abs(music))
stereo=np.stack([music,music*.97+.015*np.sin(tt*math.tau*55)*np.minimum(tt,1)],1)
with wave.open('work/score.wav','wb') as wf: wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((stereo*32767).astype('<i2').tobytes())
cmd=['ffmpeg','-hide_banner','-loglevel','warning','-n','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','work/score.wav','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','4','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(TARGET)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for i in range(FPS*DUR):
 f=frame(i/FPS); p.stdin.write(f.tobytes())
 if i%120==0: print(f'{i/FPS:.0f}/{DUR}s',flush=True)
p.stdin.close()
if p.wait(): raise SystemExit('Encode failed')
# Source stays beside the rendered video.
print(TARGET,flush=True)
