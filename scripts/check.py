from pathlib import Path
import json,urllib.parse
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1];D=R/'dist';errors=[];external=set();count=0
for path in D.rglob('*.html'):
 count+=1;s=BeautifulSoup(path.read_text('utf-8'),'html.parser')
 if not s.title or not s.select_one('link[rel=canonical]') or not s.select_one('meta[name=description]'):errors.append([str(path),'Missing SEO metadata'])
 for tag in s.select('[src],[href],[data-src]'):
  for attr in ['src','href','data-src']:
   url=tag.get(attr,'');u=urllib.parse.urlparse(url)
   if u.netloc:
    if attr in ['src','data-src']:external.add(u.netloc)
    if '/wp-content/themes/' in url or '/wp-includes/' in url:errors.append([str(path),'WordPress runtime dependency',url])
   if not url.startswith('/') or url.startswith('//'):continue
   target=D/urllib.parse.unquote(u.path).lstrip('/')
   if not target.exists() and not (target/'index.html').exists():errors.append([str(path.relative_to(D)),url])
print('Checked HTML files:',count,'; errors:',len(errors),'; external media hosts:',sorted(external))
(R/'docs/validation.json').write_text(json.dumps({'htmlFiles':count,'errors':errors,'externalMediaHosts':sorted(external)},indent=2),encoding='utf-8')
if errors:
 print(json.dumps(errors[:30],indent=2));raise SystemExit(1)
