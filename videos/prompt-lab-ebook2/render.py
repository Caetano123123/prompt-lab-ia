import math, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT=Path('/workspace/output')
W,H=1080,1920
G='#ADFF32'; WHITE='#F0F4EA'; MUT='#8A9986'
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
M='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
fonts={}
def font(s,b=False,mono=False):
 k=(s,b,mono)
 if k not in fonts: fonts[k]=ImageFont.truetype(M if mono else B if b else F,s)
 return fonts[k]
def txt(d,xy,t,s=40,c=WHITE,b=False,mono=False): d.text(xy,t,font=font(s,b,mono),fill=c)
def ease(v):
 v=max(0,min(1,v)); return 1-(1-v)**3
def panel(d,box,fill='#10190F',outline='#35472B',r=28): d.rounded_rectangle(box,r,fill=fill,outline=outline,width=2)
def header(d,n,label):
 txt(d,(86,148),'PROMPT LAB',27,G,True,True)
 txt(d,(86,207),label,22,MUT,mono=True)
 txt(d,(887,150),n,25,MUT,mono=True)
def footer(d,t):
 d.line((86,1720,994,1720),fill='#263321',width=2)
 d.rectangle((86,1720,86+int(908*t/15),1723),fill=G)
 txt(d,(86,1754),'IA + CRIATIVIDADE',21,MUT,mono=True)
 txt(d,(834,1754),'PDF / 07',21,MUT,mono=True)

rng=np.random.default_rng(42)
cols=[(int(x),float(rng.uniform(0,1900)),float(rng.uniform(30,90)), ''.join(rng.choice(list('01{}<>/;='),18))) for x in range(35,1080,78)]
def background(t):
 im=Image.new('RGB',(W,H),'#050805'); d=ImageDraw.Draw(im)
 if t>.4:
  for x,y,v,st in cols:
   yy=(y+t*v)%2300-350
   for j,ch in enumerate(st): txt(d,(x,yy+j*25),ch,17,(12,29+int(j*.65),9),mono=True)
 return im
def scene(t):
 im=background(t); layer=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(layer)
 if t<3:
  if t>.35:
   p=ease((t-.35)/.48); y=720+int((1-p)*70)
   lines=['Sem ideia para','o próximo post?']
   for i,line in enumerate(lines): txt(d,(86,y+i*112),line,78,G if i else WHITE,True)
   if int(t*2.8)%2==0: d.rectangle((89,y+245,125,y+304),fill=G)
  else: d.rectangle((86,850,122,910),fill=G)
 elif t<7:
  header(d,'01','> DO PROMPT À IDEIA')
  txt(d,(86,345),'Uma tarefa.',69,WHITE,True)
  txt(d,(86,430),'Um ponto de partida.',61,G,True)
  panel(d,(86,600,994,855))
  txt(d,(121,632),'prompt_lab:~$',27,MUT,mono=True)
  st='Crie um post sobre organização.'; count=int(max(0,t-3.08)*43)
  txt(d,(121,703),'> '+st[:count],30,G,mono=True)
  if int(t*3)%2==0: txt(d,(121,754),'_',32,G,mono=True)
  p=ease((t-3.9)/.45)
  if p>0:
   y=945+int((1-p)*150)
   panel(d,(86,y,994,y+580),fill='#152010',outline='#63853B')
   txt(d,(125,y+35),'EXEMPLO ILUSTRATIVO / CARROSSEL',22,G,mono=True)
   txt(d,(125,y+112),'3 formas de guardar',53,WHITE,True)
   txt(d,(125,y+181),'ideias de conteúdo',53,WHITE,True)
   d.line((125,y+278,949,y+278),fill='#3F542C',width=2)
   txt(d,(125,y+312),'LEGENDA',22,G,mono=True)
   for j,s in enumerate(['Uma ideia apareceu? Anote.', 'Separe por tema e escolha uma', 'para desenvolver no próximo post.']): txt(d,(125,y+361+j*48),s,34)
  footer(d,t)
 elif t<11:
  header(d,'02','> ORGANIZE A SEMANA')
  txt(d,(86,350),'7 dias.',91,WHITE,True)
  txt(d,(86,470),'Ideias no calendário.',59,G,True)
  labels=['Ideia','Roteiro','Legenda','Carrossel','Revisão','Post','Planejar']
  for i in range(7):
   row=i//2; col=i%2
   tx=86+col*466 if i<6 else 86
   ty=690+row*222
   p=ease((t-7-i*.055)/.8)
   x=int(tx+(1-p)*([-190,160,120,-150,190,-80,80][i])); y=int(ty+(1-p)*(200-i*58))
   ww=442 if i<6 else 908
   panel(d,(x,y,x+ww,y+196),fill='#111C0D',outline='#769B46' if i==0 else '#35472B')
   txt(d,(x+28,y+24),f'DIA 0{i+1}',23,G,mono=True)
   txt(d,(x+28,y+85),labels[i],37,WHITE,True)
   d.rounded_rectangle((x+ww-54,y+30,x+ww-30,y+54),6,outline=G,width=2)
  footer(d,t)
 else:
  header(d,'03','> SEU GUIA EM PDF')
  p=ease((t-11)/.65)
  # Original typographic ebook cover, with spine and shadow.
  cy=int(335+(1-p)*140); x=262
  d.rounded_rectangle((x+25,cy+26,x+582,cy+786),18,fill='#000000')
  d.polygon([(x-20,cy+23),(x,cy),(x,cy+752),(x-20,cy+775)],fill='#415E26')
  panel(d,(x,cy,x+548,cy+754),fill='#B1FF3B',outline='#D2FF8B',r=8)
  txt(d,(x+35,cy+37),'PROMPT LAB',23,'#142208',True,True)
  txt(d,(x+35,cy+135),'Instagram',49,'#0C1507',True)
  txt(d,(x+35,cy+199),'com IA',60,'#0C1507',True)
  txt(d,(x+29,cy+282),'7',242,'#0C1507',True)
  txt(d,(x+220,cy+399),'DIAS',54,'#0C1507',True)
  d.line((x+35,cy+573,x+509,cy+573),fill='#36521B',width=2)
  txt(d,(x+35,cy+607),'DO PROMPT AO POST',23,'#1B300E',True,True)
  txt(d,(x+35,cy+663),'GUIA EM PDF   >_',23,'#1B300E',mono=True)
  txt(d,(86,1190),'Instagram com IA',64,WHITE,True)
  txt(d,(86,1270),'em 7 dias | Guia em PDF',49,WHITE,True)
  q=ease((t-11.55)/.45)
  yy=int(1438+(1-q)*60)
  d.rounded_rectangle((86,yy,994,yy+144),24,fill=G)
  txt(d,(126,yy+45),'Conheça no link da bio',48,'#0D1806',True)
  footer(d,t)
 # Zoom on entrances; motion blur settles quickly to sharp text.
 dt=t if t<3 else t-3 if t<7 else t-7 if t<11 else t-11
 if 0<dt<.22:
  scale=1+.035*(1-dt/.22); nw,nh=int(W*scale),int(H*scale)
  layer=layer.resize((nw,nh),Image.Resampling.BICUBIC)
  layer=layer.crop(((nw-W)//2,(nh-H)//2,(nw+W)//2,(nh+H)//2))
  layer=layer.filter(ImageFilter.GaussianBlur(3*(1-dt/.22)))
 im.paste(layer,(0,0),layer)
 return im

def music():
 sr=48000; dur=15; a=np.zeros((sr*dur,2),np.float64); r=np.random.default_rng(7)
 def add(start,sig,gain=1,pan=0):
  i=int(start*sr); n=min(len(sig),len(a)-i)
  if n>0: a[i:i+n,0]+=sig[:n]*gain*(1-pan*.4); a[i:i+n,1]+=sig[:n]*gain*(1+pan*.4)
 beat=.5
 for k in range(30):
  t=np.arange(int(sr*.36))/sr
  kick=np.sin(2*np.pi*(48*t+9*(1-np.exp(-t*32))))*np.exp(-t*13)
  add(k*beat,kick,.57)
  if k%2:
   t=np.arange(int(sr*.16))/sr; n=r.normal(0,1,len(t)); n=np.concatenate(([0],np.diff(n)))
   add(k*beat,n*np.exp(-t*30),.085)
 for k in range(60):
  t=np.arange(int(sr*.065))/sr; n=r.normal(0,1,len(t)); n=np.concatenate(([0],np.diff(n)))
  add(k*.25,n*np.exp(-t*75),.026,(-1)**k*.65)
 notes=[45,45,52,55,45,48,52,43]
 for k in range(60):
  t=np.arange(int(sr*.22))/sr; f=440*2**((notes[k%8]-69)/12)
  sig=(np.sin(2*np.pi*f*t)+.23*np.sin(4*np.pi*f*t))*np.exp(-t*17)*np.minimum(t*200,1)
  add(k*.25,sig,.17)
 for k,note in enumerate([69,72,76,79,76,72,67,71]*4):
  t=np.arange(int(sr*.38))/sr; f=440*2**((note-69)/12)
  sig=(np.sin(2*np.pi*f*t)+.2*np.sin(2*np.pi*f*2*t))*np.exp(-t*12)*np.minimum(t*150,1)
  add(k*.5+.125,sig,.07,(-1)**k*.4); add(k*.5+.375,sig,.022,(-1)**(k+1)*.7)
 fade=np.minimum(np.arange(len(a))/sr/.08,1)*np.minimum((len(a)-1-np.arange(len(a)))/sr/.6,1)
 a=np.tanh(a)*fade[:,None]; a*=.88/max(np.max(np.abs(a)),.01)
 with wave.open('/workspace/work/original.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a*32767).astype('<i2').tobytes())

if __name__=='__main__':
 music()
 for t in [2,5.8,9.5,13.5]: scene(t).save(f'/workspace/work/frame_{t}.jpg')
 cmd=['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','60','-i','-','-i','/workspace/work/original.wav','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-t','15','-movflags','+faststart',str(OUT/'prompt-lab-instagram-ia-7-dias.mp4')]
 with open('/workspace/work/render.log','w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for i in range(900):
   p.stdin.write(scene(i/60).tobytes())
   if i%120==0: print(f'{i}/900 frames',flush=True)
  p.stdin.close(); rc=p.wait()
  if rc: raise RuntimeError(f'ffmpeg {rc}')
 print('DONE',flush=True)
