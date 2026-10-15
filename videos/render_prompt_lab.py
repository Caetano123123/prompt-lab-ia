from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, random, subprocess, wave, pathlib, sys
OUT=pathlib.Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
W,H=1080,1920
G=(63,255,137); WHITE=(227,247,236)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
fonts={}
def font(n,b=False):
 k=(n,b)
 if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,n)
 return fonts[k]
def text(d,xy,s,n=32,c=WHITE,b=False): d.text(xy,s,font=font(n,b),fill=c)
def ease(x):
 x=max(0,min(1,x)); return 1-(1-x)**3
def logo(d,x,y,size=110):
 d.rounded_rectangle((x,y,x+size*1.5,y+size),radius=16,outline=G,width=4)
 text(d,(x+size*.14,y+size*.12),'>_',int(size*.58),G,True)
def lines(d,ss,x,y,n=66,c=WHITE,gap=1.24):
 for i,s in enumerate(ss):
  drift=22*math.sin(TIME*0.7+i*.3)
  arrival=100*(1-ease((SCENE_TIME-i*.13)/.7))
  text(d,(x+drift+arrival,y+i*n*gap),s,n,c,True)
random.seed(9)
# Three independent depth planes of scrolling code. Foreground uses defocus.
planes=[]
for z in range(3):
 layer=Image.new('RGB',(1400,2600)); d=ImageDraw.Draw(layer)
 for col in range(0,1400,28+z*15):
  start=random.randrange(2600)
  for j in range(32):
   yy=(start+j*(24+z*8))%2600
   bright=int((1-j/33)*(45+z*22))
   text(d,(col,yy),random.choice('01{}[]<>/;=+AI'),20+z*7,(int(bright*.18),bright,int(bright*.46)))
 if z!=1: layer=layer.filter(ImageFilter.GaussianBlur(1.6 if z==0 else 3.3))
 planes.append(layer)
def frame(t):
 global TIME, SCENE_TIME
 TIME=t
 im=Image.new('RGB',(W,H),(1,5,4))
 from PIL import ImageChops
 for z,p in enumerate(planes):
  xx=int(120+65*math.sin(t*.14+z)); yy=int((t*(45+z*65))%680)
  lay=p.crop((xx,yy,xx+W,yy+H))
  im=ImageChops.add(im,lay,scale=1.0)
 # Vignette / calm legibility field, moving neon orbit
 veil=Image.new('RGBA',(W,H)); vd=ImageDraw.Draw(veil)
 vd.rectangle((0,0,W,H),fill=(0,3,2,125))
 im=Image.alpha_composite(im.convert('RGBA'),veil)
 d=ImageDraw.Draw(im)
 pulse=math.exp(-((t%0.5)/.075)**2)
 for j in range(5):
  r=380+j*110+18*math.sin(t*.7)
  cx=540+140*math.sin(t*.18); cy=960+160*math.cos(t*.23)
  d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(19,80+j*5,48,95),width=2)
 # Scene contents on a continuously moving camera plane
 scene=Image.new('RGBA',(W,H)); q=ImageDraw.Draw(scene)
 bounds=[0,5,10,14,20,26,30]
 idx=next((i for i in range(6) if bounds[i]<=t<bounds[i+1]),5)
 u=t-bounds[idx]; SCENE_TIME=u; dur=bounds[idx+1]-bounds[idx]
 a=ease(u/.8); enter=int(110*(1-a)); exit=-int(130*ease((u-dur+.4)/.4))
 x=90; y=540+enter+exit
 text(q,(90,230),'PROMPT LAB  /  INTELIGÊNCIA APLICADA',25,G)
 text(q,(90,1610),f'0{idx+1} / 06',24,G)
 if idx==0:
  text(q,(x,y-90),'ROTINA EM LOOP_',29,G)
  lines(q,['Você repete','as mesmas','tarefas','todo dia?'],x,y,76)
  # animated task conveyor
  for j,s in enumerate(['> criar conteúdo','> revisar textos','> responder clientes']):
   yy=y+490+j*57
   text(q,(x+int(10*math.sin(t*2+j)),yy),s[:int(max(0,u-.7-j*.4)*25)],29,(124,175,144))
 elif idx==1:
  logo(q,x,y-135,100)
  lines(q,['PROMPT','LAB'],x,y+30,110,G)
  lines(q,['Guias digitais para','usar IA no seu negócio','e no Instagram.'],x,y+340,37,WHITE,1.5)
 elif idx==2:
  text(q,(x,y-70),'MENOS REPETIÇÃO. MAIS DIREÇÃO.',29,G)
  q.rounded_rectangle((x,y+30,990,y+570),radius=22,fill=(2,15,10,245),outline=G,width=2)
  text(q,(x+35,y+58),'●  ●  ●    prompt-lab / terminal',24,G)
  cmds=['> iniciar guia','> organizar ideias','> criar com IA','✓ próximo passo: praticar']
  for j,s in enumerate(cmds):
   n=int(max(0,u-.25-j*.62)*27)
   text(q,(x+35,y+160+j*85),s[:n]+('▌' if n<len(s) else ''),31,G if j==3 else WHITE)
 elif idx in (3,4):
  second=idx==4
  text(q,(x,y-180),'GUIA DIGITAL  /  02' if second else 'GUIA DIGITAL  /  01',29,G)
  # Book cover moves and rotates throughout the shot
  cover=Image.new('RGBA',(650,700)); b=ImageDraw.Draw(cover)
  b.rounded_rectangle((5,5,640,690),radius=12,fill=(3,22,14,255),outline=G,width=3)
  for j in range(10): b.line((30+j*70,680,640,80+j*45),fill=(12,65,37),width=2)
  b.rectangle((20,20,34,675),fill=G)
  logo(b,65,55,60)
  lines(b,['Instagram','com IA','em 7 dias'] if second else ['IA na prática','para o seu','negócio'],65,230,48,G)
  text(b,(65,590),'PROMPT LAB  /  EBOOK',25,WHITE)
  cover=cover.rotate(2.8*math.sin(u*.65),resample=Image.Resampling.BICUBIC,expand=True)
  scene.alpha_composite(cover,(int(205+20*math.sin(u*.7)),int(y-50+13*math.cos(u))))
  text(q,(x,y+730),'R$24,90' if second else 'R$19,90',90,G,True)
  text(q,(x,y+850),'Instagram com IA em 7 dias' if second else 'IA na prática para o seu negócio',27,WHITE)
 else:
  logo(q,90,y-170,135)
  lines(q,['Seu próximo','passo com IA.'],x,y+50,64,WHITE)
  text(q,(x,y+310),'Link na bio',94,G,True)
  q.line((x,y+450,x+int(750*ease(u/1.4)),y+450),fill=G,width=4)
  text(q,(x,y+510),'PROMPT LAB',45,WHITE,True)
  text(q,(x,y+585),'GUIAS DIGITAIS • IA NA PRÁTICA',26,G)
 # slow camera push + drift; text remains moving, never a static slide
 scale=1+.065*(u/dur)+.006*math.sin(t)
 scene=scene.resize((int(W*scale),int(H*scale)),Image.Resampling.BICUBIC)
 dx=int(-(scene.width-W)/2+6*math.sin(t*.8)); dy=int(-(scene.height-H)/2+8*math.cos(t*.65))
 im.alpha_composite(scene,(dx,dy))
 # Light sweep with broad glow and a sharp leading edge
 fx=Image.new('RGBA',(W,H)); f=ImageDraw.Draw(fx)
 sweep=((t*.38)%1)*2600-350
 f.polygon([(sweep-230,0),(sweep-80,0),(sweep-700,H),(sweep-850,H)],fill=(40,255,120,35))
 fx=fx.filter(ImageFilter.GaussianBlur(35)); im=Image.alpha_composite(im,fx)
 d=ImageDraw.Draw(im)
 d.line((80,1710,1000,1710),fill=(20,66,41),width=2)
 d.line((80,1710,80+int(920*t/30),1710),fill=G,width=3)
 # Beat-aligned cut streak and exposure pulse
 if u<.16 and idx>0:
  flash=Image.new('RGBA',(W,H),(50,255,125,int(70*(1-u/.16))))
  im=Image.alpha_composite(im,flash)
 d=ImageDraw.Draw(im); d.rectangle((0,0,6,H),fill=(20,int(95+90*pulse),65))
 return im.convert('RGB')
def audio():
 sr=48000; n=sr*30; tt=np.arange(n)/sr; out=np.zeros(n)
 rng=np.random.default_rng(5)
 for beat in np.arange(0,30,.5):
  start=int(beat*sr); length=min(int(.36*sr),n-start); u=np.arange(length)/sr
  out[start:start+length]+=.6*np.sin(2*np.pi*(48*u+7*(1-np.exp(-u*26))))*np.exp(-u*16)
  if int(beat*2)%2:
   out[start:start+length]+=.15*rng.normal(size=length)*np.exp(-u*32)
 for tick in np.arange(0,30,.25):
  start=int(tick*sr); length=min(2500,n-start); u=np.arange(length)/sr
  out[start:start+length]+=.045*rng.normal(size=length)*np.exp(-u*100)
 for j,at in enumerate(np.arange(0,30,.25)):
  start=int(at*sr); length=min(18000,n-start); u=np.arange(length)/sr
  freq=[164.81,196,246.94,293.66,329.63,293.66,246.94,196][j%8]
  out[start:start+length]+=.055*(np.sin(2*np.pi*freq*u)+.3*np.sin(4*np.pi*freq*u))*np.exp(-u*9)
 out=np.tanh(out*1.2)*np.minimum(tt/0.3,1)*np.minimum((30-tt)/.7,1)
 stereo=np.stack([out,np.roll(out,180)*.94],axis=1)
 with wave.open(str(OUT/'batida.wav'),'wb') as w:
  w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((stereo*24000).astype('<i2').tobytes())
if __name__=='__main__':
 if '--preview' in sys.argv:
  for t in [2.8,7.8,12.7,18,24,28]: frame(t).resize((360,640)).save(f'work/preview-{t}.jpg')
 else:
  audio()
  cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','60','-i','pipe:0','-i',str(OUT/'batida.wav'),'-vf','tmix=frames=2:weights=1 3','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t','30','-movflags','+faststart',str(OUT/'prompt-lab-motion-1080x1920-60fps.mp4')]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for i in range(1800):
   p.stdin.write(frame(i/60).tobytes())
   if i%120==0: print(f'{i}/1800',flush=True)
  p.stdin.close(); assert p.wait()==0
