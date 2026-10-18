"""Original pixel masters. Native pixels only; no resampling or external art.
Rebuild: python3 tools/draw-arrival.py (Pillow). All coordinates deliberately authored.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random
random.seed(14)
OUT=Path(__file__).resolve().parents[1]/'preview/arrival/assets'
OUT.mkdir(parents=True,exist_ok=True)
ink='#293c48'; cream='#fff1cf'; teal='#327e83'
font='/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
def label(d,xy,s,size=11,color=cream):
 d.text(xy,s,font=ImageFont.truetype(font,size),fill=color,stroke_width=0)
def sprite(kind):
 im=Image.new('RGBA',(128,192)); d=ImageDraw.Draw(im)
 palettes={'hero':('#422f35','#e9b18a','#df7956','#35566b'),'guide':('#3a3540','#e7b594','#459da0','#304a61'),'grandma':('#d1ccba','#d7a37b','#9c78a6','#5d6073'),'traveler':('#7b4934','#e2ab80','#d8b455','#456975')}
 hair,skin,shirt,pants=palettes[kind]
 for direction in range(4):
  for frame in range(4):
   x=frame*32;y=direction*48; bob=1 if frame in (1,3) else 0
   def r(a,b,w,h,c):d.rectangle((x+a,y+b+ bob,x+a+w-1,y+b+h-1+bob),fill=c)
   def p(points,c):d.polygon([(x+a,y+b+bob) for a,b in points],fill=c)
   # silhouette with individual shoes and alternating legs
   left,right=([0,2,0,-1][frame],[0,-1,0,2][frame])
   r(9,34,6,9+left,pants);r(18,34,6,9+right,pants)
   r(10,35,2,6,'#69828c');r(19,35,2,6,'#69828c')
   r(8,42+left,8,4,ink);r(17,42+right,8,4,ink)
   r(9,43+left,6,1,'#ece0b8');r(18,43+right,6,1,'#ece0b8')
   p([(8,22),(12,19),(21,19),(25,23),(25,35),(8,35)],ink)
   r(9,23,15,11,shirt);r(10,24,3,9,'#f3a56b' if kind=='hero' else '#70b5ac');r(21,25,3,9,'#aa5248' if kind=='hero' else '#39737e')
   r(12,20,8,3,cream);r(14,20,4,4,skin)
   swing=2 if frame==1 else -1 if frame==3 else 0
   r(5,24+swing,4,8,ink);r(6,24+swing,4,5,shirt);r(6,30+swing,4,5,skin);r(7,31+swing,1,2,'#f6ce9d')
   r(25,24-swing,3,8,ink);r(24,24-swing,3,5,shirt);r(24,30-swing,4,5,skin)
   p([(7,7),(11,3),(21,3),(25,7),(25,17),(21,21),(11,21),(7,17)],ink)
   r(8,8,16,9,skin);r(10,17,12,3,skin);r(11,9,3,7,'#f6c99d')
   p([(7,11),(7,6),(10,3),(14,2),(21,3),(25,6),(25,12),(22,10),(20,7),(16,9),(11,7),(9,12)],hair)
   r(11,4,8,1,'#745247' if kind!='grandma' else '#ede6ce');r(9,6,4,2,'#745247' if kind!='grandma' else '#ede6ce')
   if direction==0:
    r(11,12,2,3,ink);r(20,12,2,3,ink);r(11,12,1,1,cream);r(20,12,1,1,cream);r(15,17,3,1,'#a35d54');r(9,16,2,1,'#d78a75');r(22,16,2,1,'#d78a75')
    if kind=='hero':r(11,24,2,10,'#ecce8b');r(13,30,7,4,'#765745');r(14,30,5,2,'#b98c5c')
    if kind=='guide':r(19,25,3,4,cream);r(20,26,2,1,'#d9b45d');r(14,23,3,2,'#eac16d')
    if kind=='grandma':r(10,12,5,4,'#695767');r(18,12,5,4,'#695767');r(15,13,3,1,'#695767');r(11,13,3,2,'#c3d9d3');r(19,13,3,2,'#c3d9d3');r(12,25,2,2,cream);r(20,30,2,2,cream)
   elif direction==3:
    r(8,10,16,9,hair);r(10,17,12,3,hair);r(10,11,2,5,'#654347' if kind!='grandma' else '#e6e0cd')
    if kind=='hero':r(10,23,13,13,ink);r(11,23,11,11,'#b58a55');r(12,24,9,3,'#e6c185');r(12,29,9,4,'#8f694c');r(14,28,5,1,'#efdaa2')
   else:
    rightward=direction==2
    r(9 if rightward else 20,10,4,9,hair);r(22 if rightward else 7,13,3,3,skin);r(20 if rightward else 10,12,2,3,ink);r(20 if rightward else 10,12,1,1,cream)
    if kind=='hero':r(7 if rightward else 23,23,3,11,'#c69a61');r(7 if rightward else 22,28,4,6,'#8f694c')
   if kind=='guide':r(8,5,17,3,'#327b83');r(11,3,11,3,'#4ba5a4');r(15,4,3,1,'#f2d082')
 im.save(OUT/f'{kind}.png')
for kind in ['hero','guide','grandma','traveler']:sprite(kind)
im=Image.new('RGB',(768,640),'#d6d2bb');d=ImageDraw.Draw(im)
def r(x,y,w,h,c):d.rectangle((x,y,x+w-1,y+h-1),fill=c)
def poly(pts,c):d.polygon(pts,fill=c)
def line(pts,c,w=1):d.line(pts,fill=c,width=w)
# terrazzo with deliberate subtle mineral pixels and grout
for y in range(0,640,32):
 for x in range(0,768,32):
  r(x,y,32,32,['#dedbc5','#e3dfcc','#d9d8c2'][(x//32+y//32)%3]);r(x,y,32,1,'#bdc5b6');r(x,y,1,32,'#c3c8b9')
  r(x+2,y+2,27,1,'#eee9d4')
  for i in range(5):
   a=random.randint(3,28);b=random.randint(4,29);r(x+a,y+b,1,1,random.choice(['#c8cbb8','#eee9d6','#d2d1bb']))
# inlaid blue arrival promenade
r(320,96,128,544,'#a6c8c0');r(328,96,112,544,'#b9d4c7');r(334,96,2,544,'#e5dfbf');r(432,96,2,544,'#e5dfbf')
for y in range(112,640,32):r(320,y,128,1,'#8fb6b0')
# rear facade/ceiling
r(0,0,768,112,'#466577');r(0,0,768,10,'#253f51');r(0,12,768,9,'#b2bdb5');r(0,22,768,3,'#ede8ce')
for x in range(16,760,48):
 r(x,30,43,62,'#233f53');r(x+3,33,37,52,'#77b5c4');r(x+4,34,35,14,'#b2dadd');r(x+4,49,35,16,'#99cbd0');r(x+4,67,35,16,'#589994')
 poly([(x+4,62),(x+13,60),(x+20,65),(x+30,61),(x+38,64),(x+38,72),(x+4,72)],'#6faba1')
 line([(x+7,80),(x+31,38)],'#beded7',2);r(x+20,31,3,56,'#45697b');r(x,90,44,6,'#d0cdbb');r(x,97,44,8,'#819a9b')
# arrival doors, two sets
for x in [208,384]:
 r(x-8,23,144,86,'#304c5b');r(x,34,128,67,'#648f9c')
 for a in [x+2,x+65]:
  r(a,36,59,62,'#b4d3ce');r(a+2,39,55,20,'#c8ded1');r(a+2,61,55,32,'#8eb3b2');r(a+27,38,2,58,'#e7e0c3');r(a+4,77,47,4,'#d7dfcb')
 r(x-5,17,138,22,'#254659');label(d,(x+6,20),'到着口  ARRIVALS',10);r(x-8,102,144,7,'#899c94')
# wall plinth and side walls
r(0,110,768,6,'#7a9290');r(0,116,768,3,'#f3e8cc');r(0,120,12,520,'#657f81');r(756,120,12,520,'#657f81')
def plant(x,y):
 # cast shadow, terracotta planter, broad tropical leaves
 d.ellipse((x-22,y-7,x+26,y+8),fill='#9ba99b')
 poly([(x-13,y-23),(x+14,y-23),(x+10,y+2),(x-9,y+2)],'#855744');r(x-15,y-24,31,5,'#cf9d68');r(x-11,y-18,5,15,'#b87c56');r(x-9,y-21,19,2,'#e9b77c');r(x+8,y-18,3,16,'#6f4f41')
 line([(x,y-24),(x,y-63)],'#4d7050',2)
 for dx,dy in [(-24,-51),(21,-56),(-18,-72),(16,-76),(-28,-33),(27,-37),(-5,-82)]:
  poly([(x,y-32),(x+dx,y+dy+7),(x+dx,y+dy),(x+dx//2,y+dy-2)],'#315d4c');line([(x,y-31),(x+dx,y+dy+2)],'#63955a');line([(x+dx//2,y+(dy-32)//2),(x+dx,y+dy+5)],'#88ab68')
for x,y in [(48,207),(723,236),(47,458),(724,570)]:plant(x,y)
# aquarium, display furniture, coral and hand-pixeled tropical fish
r(75,162,181,150,'#9ba99c');r(69,153,180,151,'#3b5661');r(65,150,184,8,'#d8d4b8');r(72,160,170,102,'#204f68');r(77,164,160,93,'#377d95');r(78,166,158,19,'#4e9ca7');r(79,185,157,37,'#388c9b');r(79,222,157,31,'#27657b')
for x in range(82,236,4):
 y=241+random.randint(0,8);r(x,y,4,10,'#baad89');r(x,y,2,1,'#e8d2a0')
for x,y in [(95,230),(126,240),(205,232),(222,240)]:
 for dx,dy in [(-6,-13),(4,-20),(8,-9),(-2,-23)]:line([(x,y),(x+dx,y+dy)],'#bc7c83',3);r(x+dx-1,y+dy,3,2,'#e0a995')
for x,y in [(154,237),(176,244)]:poly([(x-9,y),(x-4,y-12),(x+4,y-14),(x+10,y)],'#709d89');r(x-3,y-11,4,3,'#9ab79a')
for x,y,c in [(103,190,'#edc966'),(171,201,'#edb16c'),(207,183,'#c8d4b0'),(141,219,'#8bc4c1')]:
 poly([(x-6,y),(x-2,y-4),(x+5,y-3),(x+8,y),(x+4,y+4),(x-2,y+3)],c);poly([(x-5,y),(x-10,y-4),(x-10,y+4)],c);r(x+4,y-1,1,1,ink);r(x,y-3,2,6,'#f4e7b6');r(x-3,y-2,2,4,'#3b6676')
for x,y in [(89,177),(186,219),(229,197)]:d.rectangle((x,y,x+2,y+2),outline='#8dcac7')
r(77,164,2,91,'#c1ded4');line([(83,180),(109,166)],'#9ed1cb',2);r(70,258,176,8,'#263f50');r(72,267,172,32,'#9a7956');r(77,270,162,3,'#c1a67a');r(80,278,154,1,'#806446');label(d,(106,281),'沖縄の海へようこそ',10,'#fff0cd')
# Information alcove with roof slats and printed brochures
r(529,200,184,131,'#9da99a');r(521,160,184,149,'#d4c5a2');r(526,168,173,104,'#f1e3bd')
for x in range(529,699,9):r(x,168,2,102,'#d5c39c')
r(514,150,198,29,'#306f75');r(518,152,190,2,'#7daf9e');label(d,(539,157),'観光案内  INFORMATION',11);r(525,183,68,51,'#387479');r(529,187,60,43,'#9cbb9b')
poly([(541,194),(548,196),(546,202),(558,208),(554,217),(566,219),(560,225),(553,222),(549,212),(541,208),(543,202),(537,199)],'#e5d09c');label(d,(598,187),'旅の相談はこちら',10,'#476566')
for x in range(604,692,13):r(x,209,10,17,random.choice(['#739d9c','#d39c76','#87a477']));r(x+2,211,6,2,cream);r(x+2,215,4,6,'#eee0b2')
r(516,262,196,48,'#5f7975');r(512,255,200,9,'#846346');r(515,253,194,5,'#d1b282');r(520,265,187,37,'#b78b59')
for x in range(524,703,8):r(x,267,2,34,'#cba574')
r(530,273,166,20,'#327a7b');label(d,(555,276),'めんそーれ 沖縄',12);r(552,243,21,10,'#324d56');r(554,244,17,6,'#90bcc1');r(560,252,4,3,'#3a545c');r(669,243,20,9,'#f4e3b7')
# escalator/elevator architectural exit at upper right
r(607,32,126,98,'#304f5e');r(614,40,112,71,'#b1c5bd');r(619,43,48,65,'#7798a0');r(670,43,48,65,'#88a7a8');r(663,43,4,65,'#d9dec9');r(678,44,2,61,'#bdd1c7');r(621,104,96,4,'#52717d');r(730,65,6,18,'#d0d0b6');r(731,69,3,3,'#e7c170');r(608,20,125,21,'#304f5e');label(d,(617,24),'2F  連絡通路 ↑',10)
# bench rows with shaped seat backs, metal armrests, legs and shadows
for bx,by,n in [(80,403,4),(480,433,4),(80,560,4),(479,575,4)]:
 r(bx+3,by+29,n*35,7,'#a8b3a0')
 for i in range(n):
  x=bx+i*35;r(x+4,by+25,3,8,'#4c666b');r(x+26,by+25,3,8,'#4c666b');poly([(x+2,by),(x+28,by),(x+30,by+4),(x+28,by+18),(x+2,by+18),(x,by+4)],'#315e6c');r(x+3,by+3,23,11,'#638e96');r(x+4,by+3,21,2,'#87acaa');r(x+4,by+7,20,1,'#739e9f');r(x+1,by+16,28,9,'#325f6d');r(x+3,by+16,24,3,'#77a2a6');r(x,by+12,3,13,'#c8cdbb');r(x+28,by+12,3,13,'#c8cdbb');r(x-1,by+11,5,3,'#e4dfc6')
# vending machine with cans, buttons and payment unit
r(694,329,43,82,'#9caa9b');r(687,317,42,88,'#a85d4b');r(690,319,36,80,'#df9371');r(693,324,30,43,'#3e5c66');r(695,326,26,38,'#e8d8ae')
for y in [330,342,354]:
 for x in [697,705,713]:r(x,y,5,8,'#51979a' if x!=705 else '#d69a54');r(x,y,5,2,cream);r(x+1,y+3,3,2,'#bad2b9')
r(694,370,16,10,'#805443');r(715,369,6,3,'#e8c66f');r(715,375,6,10,'#3b5a5d');r(694,387,26,7,'#503c39');r(699,389,16,3,'#293d47');label(d,(693,319),'DRINK',5,'#fff0ce')
# central wayfinding medallion
for x,y in [(365,341),(365,553)]:
 poly([(x,y),(x+10,y-10),(x+20,y),(x+14,y),(x+14,y+10),(x+6,y+10),(x+6,y)],'#e5edcf')
# travel poster and baggage cart, no generic geometric stand-ins
r(25,269,29,65,'#486a72');r(27,271,25,49,'#e9cf95');label(d,(30,275),'島',17,'#527e7a');poly([(28,310),(36,299),(42,305),(50,299),(50,317),(28,317)],'#59968d');r(29,321,3,15,'#4c6467');r(48,321,3,15,'#4c6467')
for x,y in [(278,154),(281,536)]:
 r(x+1,y+25,25,4,'#697e79');d.ellipse((x+2,y+26,x+8,y+32),fill=ink);d.ellipse((x+21,y+26,x+27,y+32),fill=ink);line([(x+4,y+25),(x+4,y+3),(x+24,y+3),(x+24,y+25)],'#eef0d4',2);r(x+7,y+12,16,12,'#9a7057');r(x+8,y+13,14,2,'#d0a57a');r(x+13,y+9,5,3,'#50686b');r(x+2,y+23,26,3,'#c4d0bb')
# floor plaque
r(324,152,119,30,'#547e80');r(327,155,113,24,'#b9d1bc');label(d,(335,160),'NAHA  /  OKINAWA',10,'#41666c')
# foreground boundary, street facing windows
r(0,621,768,19,'#6a8584');r(12,623,744,3,'#c4ceb8')
for x in range(24,752,48):r(x,628,40,12,'#8bbcb9');r(x+3,629,3,11,'#b7d7c9')
im.save(OUT/'lobby.png')
# tiny collectable postcard authored at native size
im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im);d.polygon([(2,4),(12,2),(15,11),(4,14)],fill=ink);d.polygon([(3,5),(11,3),(13,10),(5,12)],fill='#f4e0b5');d.polygon([(4,6),(10,4),(11,7),(5,9)],fill='#6faaa3');d.line([(6,11),(10,10)],fill='#b18c69');im.save(OUT/'postcard.png')
print('Wrote original lobby, four 128×192 character sheets (32×48 × 16), postcard')
