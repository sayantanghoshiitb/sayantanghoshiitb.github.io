"""Build a portable static website; the resulting dist directory needs no Python or CMS."""
from pathlib import Path
import json,re,html,shutil,hashlib,urllib.parse,datetime
from bs4 import BeautifulSoup,Comment
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'dist'; BASE='https://sayantanghosh.com'
def read(p):return p.read_text(encoding='utf-8-sig')
def esc(s):return html.escape(str(s),quote=True)
def load(p,default):return json.loads(read(p)) if p.exists() else default
IMAGES=load(ROOT/'data/images.json',{}); ASSETS=load(ROOT/'data/assets.json',{}); WARN=[]
ASSET_PATHS={k.split('?')[0]:v for k,v in ASSETS.items()}
def local(url):
 if url in ASSETS:return '/assets/'+ASSETS[url]
 if url.split('?')[0] in ASSET_PATHS:return '/assets/'+ASSET_PATHS[url.split('?')[0]]
 p=urllib.parse.urlparse(url)
 if p.netloc in ['sayantanghosh.com','www.sayantanghosh.com']:
  key='https://sayantanghosh.com'+p.path
  if key in ASSETS:return '/assets/'+ASSETS[key]
  return p.path+('?' +p.query if p.query else '')+('#'+p.fragment if p.fragment else '')
 return url
def clean(markup,title,home=False,travel=False):
 soup=BeautifulSoup(markup,'html.parser')
 if travel:
  for node in soup.select('.entry-meta,.posted-on,.byline,.cat-links,.post-navigation'):
   node.decompose()
  for heading in soup.select('h1,h2,h3'):
   if heading.get_text(' ',strip=True).lower()=='category: travel':heading.string='Travel'
 for x in soup.find_all(string=lambda t:isinstance(t,Comment)):x.extract()
 for t in soup.select('script,style,form'):t.decompose()
 for t in soup.select('.comment-respond'):t.decompose()
 for t in soup.find_all(True):
  for attr in list(t.attrs):
   if attr.startswith('on') or attr in ['srcset','sizes','fetchpriority']:del t[attr]
  for attr in ['href','src','poster']:
   if t.get(attr):t[attr]=local(t[attr])
 for i,img in enumerate(soup.select('img')):
  if 'modernthemes.net' in img.get('src',''):
   placeholder=soup.new_tag('span');placeholder['class']='form-note';placeholder.string='Original theme-demo image unavailable';img.replace_with(placeholder);continue
  src=img.get('src',''); name=src.rsplit('/',1)[-1]; meta=IMAGES.get(name,{})
  if meta.get('variants'):
   sizes=meta['variants'];img['src']='/assets/'+sizes[min(1,len(sizes)-1)]['file'];img['srcset']=', '.join('/assets/'+v['file']+' '+str(v['width'])+'w' for v in sizes)
   img['sizes']='(max-width:480px) 100vw, (max-width:767px) 33vw, (max-width:1400px) 25vw, 20vw' if home else '(max-width:767px) 90vw, 780px'
   img['width']=meta['width'];img['height']=meta['height']
  if not img.get('alt'):
   figure=img.find_parent('figure');caption=figure.find('figcaption') if figure else None
   img['alt']=caption.get_text(' ',strip=True) if caption else f'{title} — photograph {i+1} by Sayantan Ghosh'
  portfolio_image=home and img.find_parent(id='gallery-container') is not None
  img['decoding']='async';img['loading']='eager' if portfolio_image or i==0 else 'lazy'
  if i==0:img['fetchpriority']='high'
  if src.startswith('/wp-content/'):
   WARN.append({'page':title,'missingImage':src})
 for a in soup.select('a[href]'):
  if a['href'].startswith(('/wp-login.php','/wp-admin/')):
   a.unwrap();continue
  if re.search(r'\.(jpg|jpeg|png|webp)$',a['href'],re.I):a['data-lightbox']='true'
  if a.get('target')=='_blank':a['rel']='noopener noreferrer'
 for iframe in soup.select('iframe'):
  iframe['loading']='lazy';iframe['title']=iframe.get('title') or f'{title} video'
 for v in soup.select('video'):v['controls']='';v['preload']='none'
 if home:
  g=soup.select_one('#gallery-container');g['class']='home-gallery';g['aria-label']='Photography portfolio'
 return str(soup)
def navigation():
 s=BeautifulSoup(read(ROOT/'content/menu.html'),'html.parser');ul=s.select_one('ul');ul['class']='nav-menu'
 for a in s.select('a'):
  if a.get_text(' ',strip=True).lower()=='destinations':a.string='Travel'
 for t in s.find_all(True):
  for key in ['id','aria-current']:t.attrs.pop(key,None)
  if t is not ul:t.attrs.pop('class',None)
 for a in s.select('a[href]'):
  a['href']=local(a['href'])
  if a['href']=='#':a.name='button';del a['href'];a['type']='button';a['aria-expanded']='false'
 ul['id']='primary-menu'
 socials=[('https://www.instagram.com/digitalghosh/','Instagram','\uf16d'),('https://www.facebook.com/sayantan.iitb/','Facebook','\uf39e'),('https://500px.com/p/SayantanGhosh3','500px','\uf26e'),('https://www.youtube.com/user/ThePixelatedPictures','YouTube','\uf167')]
 icons=''.join(f'<a href="{u}" aria-label="{n}"><i class="brand-icon" aria-hidden="true">{c}</i></a>' for u,n,c in socials)
 return f'<a class="skip-link" href="#main-content">Skip to content</a><div class="topbar"><nav class="navigation" aria-label="Main navigation"><button class="menu-toggle" aria-label="Open navigation" aria-controls="primary-menu" aria-expanded="false">≡</button>{s}</nav><div class="social">{icons}</div></div>'
NAV=navigation()
def shell(title,path,body,description='',image='',noindex=False,wild=False,home=False):
 canonical=BASE+path;page_title=title+' | Sayantan Ghosh Photography' if title!='Portfolio' else 'Sayantan Ghosh Photography'
 description=description or 'Travel stories, portraits and wildlife photography by Sayantan Ghosh.'
 schema={'@context':'https://schema.org','@type':'CollectionPage' if path in ['/','/wildlife/'] else 'WebPage','name':page_title,'url':canonical,'description':description,'author':{'@type':'Person','name':'Sayantan Ghosh','url':BASE}}
 extra='<link rel="stylesheet" href="/wildlife.css"><script src="/wildlife.js" defer></script>' if wild else ''
 if image:extra+=f'<meta property="og:image" content="{BASE+image if image.startswith("/") else esc(image)}">'
 return f'''<!doctype html><html lang="en" class="page-loading"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><script>try{{if(sessionStorage.getItem('sayantan-loader-seen')==='1')document.documentElement.classList.remove('page-loading')}}catch(e){{}}</script><title>{esc(page_title)}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}"><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}"><meta property="og:title" content="{esc(page_title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="/site.css"><script src="/site.js" defer></script>{extra}<script type="application/ld+json">{json.dumps(schema).replace('<','\\u003c')}</script><noscript><link rel="stylesheet" href="/noscript.css"></noscript></head><body><div id="home-loader" role="status" aria-live="polite"><span class="home-loader-line">Welcome to</span><span class="home-loader-line home-loader-name">Sayantan Ghosh Photography</span></div>{NAV}{body}<footer class="site-footer">© 2026 www.sayantanghosh.com</footer><dialog class="lightbox" aria-label="Photo viewer"><div class="lightbox-tools"><button data-prev aria-label="Previous photo">←</button><button data-close aria-label="Close photo viewer">Close ×</button><button data-next aria-label="Next photo">→</button></div><img alt=""><p class="lightbox-caption"></p></dialog></body></html>'''
def write_page(path,text):
 dest=OUT/path.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
def shape(geometry):
 polys=[geometry['coordinates']] if geometry['type']=='Polygon' else geometry['coordinates'];paths=[]
 for poly in polys:
  for ring in poly:paths.append('M'+' L'.join(f'{(lon+180)*2.5:.2f},{(90-lat)*2.5:.2f}' for lon,lat,*_ in ring)+' Z')
 return ' '.join(paths)

def heat(count,maximum):
 if not count:return '#e3e3e3'
 t=(count/max(maximum,1))**.5;a=(224,224,224);b=(35,35,35)
 return '#'+''.join(f'{round(x+(y-x)*t):02x}' for x,y in zip(a,b))

def world_map(data):
 counts={x['code']:x['count'] for x in data.get('countries',[])};maximum=max(counts.values(),default=1);paths=[];layers=[]
 india_outline=load(ROOT/'data/india-outline.geojson',{})
 world_features=load(ROOT/'data/world.geojson',{'features':[]})['features']
 # Paint the corrected outline after neighboring polygons from the older dataset.
 for f in sorted(world_features,key=lambda f:(f['properties'].get('ISO_A2_EH') or f['properties'].get('ISO_A2'))=='IN'):
  p=f['properties'];code=p.get('ISO_A2_EH') or p.get('ISO_A2');name=p.get('NAME_EN') or p.get('NAME');count=counts.get(code,0)
  # World view uses only the dissolved country exterior, without state borders.
  geometry=shape(india_outline['geometry']) if code=='IN' and india_outline else shape(f['geometry'])
  attrs=f' data-country="{code}" data-name="{esc(name)}" tabindex="0" role="button" aria-label="{esc(name)}: {count} species"' if count else ''
  paths.append(f'<path d="{geometry}" style="fill:{heat(count,maximum)}"{attrs}><title>{esc(name)}: {count} species</title></path>')
 for country in counts:
  regions=dict(data.get('regions',{}).get(country,[]));largest=max(regions.values(),default=1);states=[]
  for f in load(ROOT/'data/states.geojson',{'features':[]})['features']:
   p=f['properties']
   if p['country']!=country:continue
   count=regions.get(p['code'],0)
   states.append(f'<path d="{shape(f["geometry"])}" style="fill:{heat(count,largest)}" data-region="{p["code"]}" data-name="{esc(p["name"])}" tabindex="0" role="button" aria-label="{esc(p["name"])}: {count} species"><title>{esc(p["name"])}: {count} species</title></path>')
  layers.append(f'<g class="state-layer" data-map-country="{country}" hidden>{"".join(states)}</g>')
 return '<svg id="bird-map" class="world-map" viewBox="0 0 900 450" role="group" aria-label="Interactive species map"><g id="world-layer">'+''.join(paths)+'</g>'+''.join(layers)+'</svg>'

def wildlife():
 data=load(ROOT/'data/birds.json',{});species=data.get('species',[]);countries=sorted(data.get('countries',[]),key=lambda c:-c['count']);complete=data.get('observationsComplete',False);names={}
 for f in load(ROOT/'data/world.geojson',{'features':[]})['features']:
  p=f['properties'];names[p.get('ISO_A2_EH') or p.get('ISO_A2')]=p.get('NAME_EN') or p.get('NAME')
 state_names={f['properties']['code']:f['properties']['name'] for f in load(ROOT/'data/states.geojson',{'features':[]})['features']}
 seen=len(species) if complete else '—';photos=sum(bool(b.get('photo')) for b in species)
 stats=[(seen,'Species seen'),(photos,'Species photographed'),(len(countries),'Countries')]
 st=''.join(f'<div class="wild-stat"><strong>{v}</strong><span>{label}</span></div>' for v,label in stats)
 global_total=11000;global_percent=min(100,(len(species)/global_total)*100)
 global_progress=f'<section class="global-progress" aria-label="Global bird species progress"><div class="global-progress-copy"><span>Progress Tracker</span><strong>{len(species):,} <small>/ approximately {global_total:,}</small></strong></div><div class="global-progress-track" role="progressbar" aria-label="Species seen out of approximately 11,000 bird species" aria-valuemin="0" aria-valuemax="{global_total}" aria-valuenow="{len(species)}"><span style="width:{global_percent:.2f}%"></span></div><p>{global_percent:.1f}% recorded</p></section>'
 cl=''.join(f'<li><button data-country="{c["code"]}"><span>{esc(names.get(c["code"],c["code"]))}</span><b>{c["count"]}</b></button></li>' for c in countries)
 opts=''.join(f'<option value="{c["code"]}">{esc(names.get(c["code"],c["code"]))}</option>' for c in countries);cards=[]
 for b in species:
  photo=b.get('photo');media=f'<a href="{esc(photo["assetUrl"])}"><img data-src="{esc(photo["imageUrl"])}" alt="{esc(b["name"])} — photographed by Sayantan Ghosh" width="640" height="480" loading="lazy" decoding="async"></a>' if photo else '<div class="no-photo"><div class="no-photo-art" aria-hidden="true"><span class="no-photo-frame"></span><span class="no-photo-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/></svg></span></div><span>Seen · photo not available</span></div>'
  if photo:
   country_code=photo.get('countryCode') or b.get('firstSeenCountry') or (b.get('countries') or [''])[0]
   region_code=photo.get('regionCode') or b.get('firstSeenRegion','')
   place=photo.get('locationName') or state_names.get(region_code,'')
   country_name=names.get(country_code,country_code)
   where=', '.join(x for x in [place,country_name] if x)
   location=f'<p class="bird-location"><span aria-hidden="true">⌖</span> {esc(where)}</p>' if where else ''
  else:location=''
  hidden='' if photo else ' hidden'
  date_text=b.get('firstSeen','');date_match=re.match(r'^(\d{4})-(\d{2})-',date_text)
  if date_match:
   try:date_text=datetime.date(int(date_match.group(1)),int(date_match.group(2)),1).strftime('%b %Y')
   except ValueError:pass
  cards.append(f'<article class="bird-card"{hidden} data-search="{esc((b["name"]+" "+b.get("scientificName","")).lower())}" data-name="{esc(b["name"])}" data-date="{esc(b.get("firstSeen",""))}" data-photo="{str(bool(photo)).lower()}" data-countries="{esc(",".join(b.get("countries",[])))}" data-regions="{esc(",".join(b.get("regions",[])))}">{media}<div class="bird-info"><h3>{esc(b["name"])}</h3><p class="scientific">{esc(b.get("scientificName",""))}</p>{location}<p>{esc(date_text)}</p></div></article>')
 maximum=max((c['count'] for c in countries),default=0)
 body=f'''<main id="main-content" class="wildlife"><header class="wild-intro"><div><h1>World Birding Stats</h1></div><a class="profile-link" href="https://ebird.org/profile/MjI5NzQ0MA">My eBird profile ↗</a></header>{global_progress}<section class="wild-stats" aria-label="Birding progress">{st}</section><section class="world-section"><div><div class="world-heading"><h2>Life List</h2><label class="photo-toggle"><input id="bird-photo" type="checkbox" role="switch" checked><span class="toggle-track" aria-hidden="true"></span>Images only <span id="photo-count" class="photo-count">({photos} species)</span></label></div><div class="map-controls"><button id="map-world">World</button><button id="map-country" hidden></button><span id="map-place" aria-live="polite"></span><button id="map-back" hidden>← Back</button></div>{world_map(data)}</div><div><h2 id="region-heading">By country</h2><ul id="region-list" class="country-list">{cl}</ul></div></section><section><h2>Image Gallery</h2><div class="bird-toolbar"><label class="sr-only" for="bird-search">Search birds</label><input id="bird-search" type="search" placeholder="Search common or scientific name"><label class="sr-only" for="bird-country">Country</label><select id="bird-country"><option value="">All countries</option>{opts}</select><label class="sr-only" for="bird-sort">Sort birds</label><select id="bird-sort"><option value="name">Alphabetical</option><option value="recent">Latest lifers</option></select><button id="reset-filters" class="filter-reset">Reset</button></div><div class="bird-grid">{''.join(cards)}<div id="no-results" class="bird-empty" hidden>No birds match these filters.</div></div></section><footer>Observation data: <a href="https://ebird.org">eBird</a>, Cornell Lab of Ornithology. Photographs © Sayantan Ghosh, archived in the <a href="https://www.macaulaylibrary.org/">Macaulay Library</a>. Map boundaries: <a href="https://www.naturalearthdata.com/">Natural Earth</a> (public domain); India country outline: <a href="https://www.geoboundaries.org/">geoBoundaries</a> (CC0); Jammu and Kashmir and Ladakh outlines: geoBoundaries / DataMeet India (CC BY 2.5 IN).</footer></main><script id="bird-data" type="application/json">{json.dumps({'observationsComplete':complete,'countryMembershipComplete':data.get('countryMembershipComplete',False),'countries':countries,'regions':data.get('regions',{}),'names':names}).replace('<','\\u003c')}</script>'''
 write_page('/wildlife/',shell('Wildlife','/wildlife/',body,'My birding life list, personal bird photography, and species progress by country.',wild=True))

def main():
 if OUT.exists():
  if OUT.resolve().parent!=ROOT.resolve():raise ValueError('Unexpected output directory')
  shutil.rmtree(OUT)
 OUT.mkdir(exist_ok=True);shutil.copytree(ROOT/'public',OUT,dirs_exist_ok=True)
 for f in (ROOT/'src').iterdir():shutil.copy2(f,OUT/f.name)
 pages=load(ROOT/'content/pages.json',[]);sitemap=[];report=[]
 menu=BeautifulSoup(read(ROOT/'content/menu.html'),'html.parser')
 travel_paths={urllib.parse.urlparse(a.get('href','')).path for a in menu.select('a[href]') if urllib.parse.urlparse(a.get('href','')).netloc in ['sayantanghosh.com','www.sayantanghosh.com'] and urllib.parse.urlparse(a.get('href','')).path}
 for p in pages:
  travel_page=p['path'] in travel_paths or p['path'].startswith('/category/travel-blog/')
  content=clean(read(ROOT/'content/pages'/p['file']),p['title'],p['kind']=='home',travel_page);s=BeautifulSoup(content,'html.parser');text=s.get_text(' ',strip=True)
  description=(text[:157]+'…') if len(text)>160 else text
  img=s.select_one('img');og=img.get('src','') if img else ''
  header='' if p['kind']=='home' else clean(read(ROOT/'content/header.html'),p['title'])
  noindex=p['kind']=='page' and p['path'] not in ['/publications/','/comic-con-mumbai-india/','/saturday-night-market-goa/','/travel-films/','/shorts/']
  if p['kind']=='post':
   for node in s.select('.entry-title,.entry-meta'):node.decompose()
   content=str(s)
   header=f'<header class="site-header"><div class="grid grid-pad"><h1 class="site-title">{esc(p["title"])}</h1></div></header>'
  body=header+f'<div id="main-content">{content}</div>'
  if p['kind']=='home':body='<h1 class="sr-only">Sayantan Ghosh Photography</h1>'+body
  if p['kind']=='post':
   original=BeautifulSoup(read(ROOT/'content/pages'/p['file']),'html.parser');published=original.select_one('time.published');modified=original.select_one('time.updated')
   article={'@context':'https://schema.org','@type':'BlogPosting','headline':p['title'],'mainEntityOfPage':BASE+p['path'],'author':{'@type':'Person','name':'Sayantan Ghosh','url':BASE},'description':description}
   if published:article['datePublished']=published.get('datetime')
   if modified:article['dateModified']=modified.get('datetime')
   if og:article['image']=BASE+og
   body+='<script type="application/ld+json">'+json.dumps(article).replace('<','\\u003c')+'</script>'
  write_page(p['path'],shell(p['title'],p['path'],body,description,og,noindex,home=p['kind']=='home'));report.append({**p,'noindex':noindex})
  if not noindex:sitemap.append(p['path'])
 wildlife();sitemap.append('/wildlife/')
 (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE+p}</loc></url>' for p in sitemap)+'</urlset>',encoding='utf-8')
 (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n',encoding='utf-8')
 redirects=[f'{urllib.parse.urlparse(url).path} /assets/{file} 301' for url,file in ASSETS.items() if urllib.parse.urlparse(url).netloc=='sayantanghosh.com']
 redirects+=['/wp-sitemap.xml /sitemap.xml 301','https://www.sayantanghosh.com/* https://sayantanghosh.com/:splat 301!']
 for url,file in ASSETS.items():
  u=urllib.parse.urlparse(url)
  if u.netloc in ['sayantanghosh.com','www.sayantanghosh.com'] and u.path.startswith('/wp-content/uploads/'):
   alias=OUT/urllib.parse.unquote(u.path).lstrip('/')
   alias.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'public/assets'/file,alias)
 shutil.copy2(OUT/'sitemap.xml',OUT/'wp-sitemap.xml')
 (OUT/'.nojekyll').touch()
 (OUT/'_redirects').write_text('\n'.join(redirects)+'\n',encoding='utf-8')
 (OUT/'404.html').write_text(shell('Page not found','/404/', '<main id="main-content" class="wildlife"><h1>Page not found</h1><p><a href="/">Return to the portfolio</a></p></main>',noindex=True),encoding='utf-8')
 (ROOT/'docs/build-report.json').write_text(json.dumps({'routes':report,'warnings':WARN},indent=2),encoding='utf-8')
 print(f'Built {len(pages)+1} routes. Missing image references: {len(WARN)}')
if __name__=='__main__':main()
