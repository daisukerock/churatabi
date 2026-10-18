from PIL import Image
from pathlib import Path
import json
assets=Path('preview/arrival/assets');result={}
for name in ['hero','guide','grandma','traveler']:
 im=Image.open(assets/f'{name}.png');assert im.size==(128,192);assert im.mode=='RGBA'
 directions=[]
 for row in range(4):
  frames=[im.crop((col*32,row*48,(col+1)*32,(row+1)*48)) for col in range(4)]
  assert all(f.size==(32,48) and f.getbbox() for f in frames)
  assert len({f.tobytes() for f in frames})>=3
  directions.append(frames[0].tobytes())
 assert len(set(directions))==4
 result[name]={'sheet':[128,192],'cell':[32,48],'directions':4,'framesPerDirection':4,'alpha':True}
im=Image.open(assets/'lobby.png');assert im.size==(768,640)
result['lobby']={'size':[768,640],'colors':len(im.getcolors(1000000))}
Path('docs/qa/assets-result.json').write_text(json.dumps({'passed':True,'assets':result},indent=2))
print('Asset dimensions, distinct directions, animation frames, alpha: PASS')
