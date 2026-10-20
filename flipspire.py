#!/usr/bin/env python3
"""Original offline solo pinball for SSH terminals."""
import curses,json,math,os,time
from pathlib import Path
from ui import put,run

try:
    import pi18n
except ImportError:
    pi18n = None

# English UI strings; the Translations app owns every language via ~/pi-translations.
DEFAULT_STRINGS = {'TITLE': 'FLIPSPIRE | SOLO PINBALL | 3 BALLS', 'HUD': 'SCORE {score} | balls used {used}/3', 'BEST': 'LOCAL BEST {best}', 'LAUNCH': 'Up launches ball {n} of 3', 'IN_PLAY': 'Ball in play. Left / Right flippers.', 'GAME_OVER': 'GAME OVER | Score {score}', 'OVER_TAIL': ' | R restart', 'SAVED': 'Record saved locally.', 'NOT_SAVED': 'Record not saved (storage unavailable).', 'DRAIN': 'DRAIN', 'RESIZE': 'Resize to 70x26. Physics paused. Q quits.', 'PAUSED': 'PAUSED', 'CONTROLS': '↑ launch | ← left flipper | → right flipper | Space pause | R restart | Q quit', 'NOTE': 'Taps activate for 0.18s. Solo pinball; no network or paid unlocks.'}
VERSION='1.0.0'
RECORDS=Path.home()/'.local/share/flipspire/records.json'
class Table:
 W=60;H=40
 def __init__(self,S=None):
  self.S=S or DEFAULT_STRINGS
  self.scores=[0];self.used=[0];self.ball=False;self.over=False;self.x=56;self.y=35;self.vx=self.vy=0;self.bumper_cool=[0,0,0];self.target_cool=[0,0,0,0];self.combo=0;self.message=self.S['LAUNCH'].format(n=1);self.balls=0;self.elapsed=0
 def launch(self):
  if self.ball or self.over:return False
  self.ball=True;self.used[0]+=1;self.balls+=1;self.x=56;self.y=35;self.vx=-12;self.vy=-40;self.combo=0;self.message=self.S['IN_PLAY'];return True
 def drain(self):
  self.ball=False;self.combo=0
  if self.used[0]>=3:self.over=True;self.message=self.S['GAME_OVER'].format(score=self.scores[0]);return
  self.x=56;self.y=35;self.vx=self.vy=0;self.message=self.S['LAUNCH'].format(n=self.used[0]+1)
 def score(self,points):self.scores[0]+=points
 @staticmethod
 def segment_hit(x,y,ax,ay,bx,by,radius=.85):
  dx=bx-ax;dy=by-ay;t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)));px=ax+t*dx;py=ay+t*dy
  return math.hypot(x-px,y-py)<=radius
 def step(self,dt,left=False,right=False):
  dt=min(.06,max(0,dt));self.elapsed+=dt
  self.bumper_cool=[max(0,v-dt) for v in self.bumper_cool];self.target_cool=[max(0,v-dt) for v in self.target_cool]
  if not self.ball:return
  steps=max(1,math.ceil(max(abs(self.vx),abs(self.vy))*dt/.3));tick=dt/steps
  for _ in range(steps):
   self.vy+=18*tick;self.x+=self.vx*tick;self.y+=self.vy*tick
   # Closed outer walls and rounded top. Bottom is the drain.
   if self.x<2:self.x=4-self.x;self.vx=abs(self.vx)*.9
   if self.x>58:self.x=116-self.x;self.vx=-abs(self.vx)*.9
   if self.y<2:self.y=4-self.y;self.vy=abs(self.vy)*.9
   for i,(bx,by) in enumerate(((19,12),(41,12),(30,20))):
    dx=self.x-bx;dy=self.y-by;distance=math.hypot(dx,dy)
    if distance<3.2 and distance>.001:
     nx=dx/distance;ny=dy/distance;self.x=bx+nx*3.3;self.y=by+ny*3.3;dot=self.vx*nx+self.vy*ny
     if dot<0:self.vx-=2*dot*nx;self.vy-=2*dot*ny
     self.vx+=nx*5;self.vy+=ny*5
     if self.bumper_cool[i]==0:self.score(50);self.combo+=1;self.bumper_cool[i]=.18;self.message='Bumper +50 | hits '+str(self.combo)
   for i,tx in enumerate((12,24,36,48)):
    if abs(self.x-tx)<2 and self.y<5 and self.target_cool[i]==0:
     self.score(100);self.vy=abs(self.vy)+2;self.target_cool[i]=.7;self.message='Top target +100'
   # Guide rails slope down toward the flippers, reflection based on segment normals.
   for ax,ay,bx,by in ((2,27,18,34),(58,27,42,34)):
    if self.segment_hit(self.x,self.y,ax,ay,bx,by,.7):
     dx=bx-ax;dy=by-ay;length=math.hypot(dx,dy);nx=-dy/length;ny=dx/length
     if ny>0:nx=-nx;ny=-ny
     dot=self.vx*nx+self.vy*ny
     if dot<0:self.vx-=1.6*dot*nx;self.vy-=1.6*dot*ny;self.x+=nx*.8;self.y+=ny*.8
   # Flippers: resting slopes or upward-facing activated bats; pulse adds energy.
   for active,ax,ay,bx,by,sign in ((left,18,34,28,31 if left else 37,1),(right,42,34,32,31 if right else 37,-1)):
    if self.vy>0 and self.segment_hit(self.x,self.y,ax,ay,bx,by,1.15):
     self.y=min(self.y,by)-1;self.vy=-30 if active else -8;self.vx=sign*(10 if active else 4);self.message='Flipper!'
   speed=math.hypot(self.vx,self.vy)
   if speed>50:self.vx*=50/speed;self.vy*=50/speed
   if self.y>40:self.drain();break

def load_records():
 try:
  if RECORDS.is_symlink():return {}
  data=json.loads(RECORDS.read_text());return data if isinstance(data,dict) else {}
 except (OSError,ValueError):return {}
def save_records(table):
 try:
  if any(p.is_symlink() for p in [RECORDS]+list(RECORDS.parents)):return False
  RECORDS.parent.mkdir(parents=True,exist_ok=True,mode=0o700);old=load_records();data={'best':max(max(table.scores),int(old.get('best',0))),'matches':int(old.get('matches',0))+1}
  tmp=RECORDS.with_suffix('.tmp');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:json.dump(data,f)
  tmp.replace(RECORDS);return True
 except (OSError,ValueError,TypeError):return False

def loop(s):
 S=pi18n.load('flipspire',DEFAULT_STRINGS) if pi18n else DEFAULT_STRINGS
 s.timeout(16);g=Table(S);last=time.monotonic();paused=False;left_until=right_until=0;recorded=False;trail=[];note=''
 if curses.has_colors():
  curses.start_color();curses.use_default_colors()
  for i,c in enumerate((curses.COLOR_CYAN,curses.COLOR_MAGENTA,curses.COLOR_YELLOW,curses.COLOR_WHITE,curses.COLOR_GREEN),1):curses.init_pair(i,c,-1)
 def color(i):return curses.color_pair(i) if curses.has_colors() else 0
 while True:
  h,w=s.getmaxyx();key=s.getch();now=time.monotonic();dt=now-last;last=now;s.erase()
  if key in (27,ord('q'),ord('Q')):return
  if key in (ord('r'),ord('R')):g=Table(S);paused=False;recorded=False;note='';trail=[]
  if key==ord(' '):paused=not paused;left_until=right_until=0
  if key==curses.KEY_UP and not paused:g.launch();trail=[]
  if key==curses.KEY_LEFT:left_until=now+.18
  if key==curses.KEY_RIGHT:right_until=now+.18
  left=now<left_until;right=now<right_until
  if w<70 or h<26:put(s,2,2,S['RESIZE']);s.refresh();continue
  if not paused and not g.over:g.step(dt,left,right);trail=(trail+[(g.x,g.y)])[-6:]
  if g.over and not recorded:note=S['SAVED'] if save_records(g) else S['NOT_SAVED'];recorded=True
  boardw=min(w-6,(h-8)*3);boardh=h-8;ox=(w-boardw)//2;oy=4
  def pos(x,y):return oy+round(y/40*(boardh-1)),ox+round(x/60*(boardw-1))
  def draw(x,y,text,attr=0):yy,xx=pos(x,y);put(s,yy,xx,text,attr)
  def line(ax,ay,bx,by,char,attr):
   steps=max(1,round(max(abs(bx-ax)/60*boardw,abs(by-ay)/40*boardh)))
   for n in range(steps+1):draw(ax+(bx-ax)*n/steps,ay+(by-ay)*n/steps,char,attr)
  put(s,0,2,S['TITLE'],color(1)|curses.A_BOLD)
  put(s,1,2,S['HUD'].format(score=g.scores[0],used=g.used[0]),color(3)|curses.A_BOLD)
  put(s,2,2,S['BEST'].format(best=load_records().get('best',0)),color(2))
  line(1,1,59,1,'═',color(1));line(1,1,1,39,'║',color(1));line(59,1,59,39,'║',color(1))
  for i,x in enumerate((12,24,36,48)):draw(x,3,'▼',color(5) if g.target_cool[i]>0 else color(3))
  for i,(x,y) in enumerate(((19,12),(41,12),(30,20))):draw(x-1,y,'(●)',color(5) if g.bumper_cool[i]>0 else color(2)|curses.A_BOLD)
  line(2,27,18,34,'╲',color(1));line(58,27,42,34,'╱',color(1))
  line(18,34,28,31 if left else 37,'━',color(3) if left else color(4));line(42,34,32,31 if right else 37,'━',color(3) if right else color(4))
  for x,y in trail[:-1]:draw(x,y,'·',color(4)|curses.A_DIM)
  draw(g.x,g.y,'●',color(3)|curses.A_BOLD)
  draw(28,39,S['DRAIN'],color(2));draw(54,37,'↑',color(5))
  if paused:put(s,3,max(2,w//2-6),S['PAUSED'],color(3)|curses.A_BOLD)
  if g.over:put(s,h//2,max(2,w//2-15),g.message+S['OVER_TAIL'],color(3)|curses.A_BOLD)
  put(s,h-3,2,note or g.message,color(3))
  put(s,h-2,2,S['CONTROLS'])
  put(s,h-1,2,S['NOTE'],color(1));s.refresh()
if __name__=='__main__':
 import sys
 if '--version' in sys.argv:print(VERSION)
 else:raise SystemExit(run(loop))
