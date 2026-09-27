"""Generate responsive WebP variants once, preserving originals for downloads."""
from pathlib import Path
from PIL import Image,ImageOps
import json,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
def one(p):
 try:
  with Image.open(p) as raw:
   im=ImageOps.exif_transpose(raw).convert('RGB'); w,h=im.size; sizes=[]
   for size in [480,960,1600]:
    width=min(w,size); target=p.with_name(p.stem+f'-{width}.webp')
    if not target.exists():
     out=im.copy();out.thumbnail((width,round(h*width/w)));out.save(target,'WEBP',quality=84,method=4)
    if not any(v['width']==width for v in sizes):sizes.append({'width':width,'file':target.name,'bytes':target.stat().st_size})
   return p.name,{'width':w,'height':h,'originalBytes':p.stat().st_size,'variants':sizes}
 except Exception as e:return p.name,{'error':str(e)}
if __name__=='__main__':
 paths=[p for p in (ROOT/'public/assets').iterdir() if p.suffix.lower() in ['.jpg','.jpeg','.png']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=dict(pool.map(one,paths))
 (ROOT/'data/images.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 print('Optimized',len(results),'images')
