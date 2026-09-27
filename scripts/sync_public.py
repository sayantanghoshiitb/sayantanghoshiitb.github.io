"""Public JSON APIs used by Raw Composition; undocumented, no login or cookies.
Complete unseen-photo life-list coverage still comes from an official CSV export.
"""
import argparse,datetime,json,urllib.request,urllib.parse,sys,re,os,subprocess,shutil
from pathlib import Path
from import_ebird import atomic_write
ROOT=Path(__file__).resolve().parents[1]

def fetch(url):
 if os.name=='nt' and shutil.which('pwsh'):
  # Windows uses its native HTTP client; no browser cookies or bot-challenge handling.
  command="$ErrorActionPreference='Stop'; $u=[Console]::ReadLine(); (Invoke-WebRequest -Uri $u -TimeoutSec 45).Content"
  result=subprocess.run(['pwsh','-NoProfile','-Command',command],input=url+'\n',capture_output=True,text=True,encoding='utf-8',timeout=60)
  if result.returncode:raise ValueError('eBird HTTP request failed')
  return json.loads(result.stdout)
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 SayantanPortfolio/1.0','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def sync_countries(data):
 raw=fetch('https://ebird.org/prof/count/species?'+urllib.parse.urlencode({'username':data['profileId'],'r':'world'}))
 if not isinstance(raw,list) or not raw:raise ValueError('Empty or invalid country response')
 result=[]
 for row in raw:
  if not isinstance(row,list) or len(row)!=2 or not re.fullmatch('[A-Z]{2}',str(row[0])):raise ValueError('Unexpected country data shape')
  n=int(row[1])
  if n<0:raise ValueError('Negative species count')
  result.append({'code':row[0],'count':n})
 return result

def apply_photos(data,media):
 birds=json.loads(json.dumps(data['species']))
 by_sci={b['scientificName'].casefold():b for b in birds};by_name={b['name'].casefold():b for b in birds}
 for b in birds:b.pop('photo',None)
 accepted=0;unmatched=set()
 for item in media:
  who=str(item.get('userId','')).removeprefix('USER').removeprefix('USR')
  if who!=data['contributorId'] or item.get('mediaType')!='photo' or item.get('restricted') or item.get('exoticCategory')=='escapee':continue
  tax=item.get('taxonomy') or {}
  b=by_sci.get(tax.get('sciName','').casefold()) or by_name.get(tax.get('comName','').casefold())
  if not b:
   unmatched.add(tax.get('comName','Unknown'));continue
  asset=str(item.get('assetId',''))
  if not asset.isdigit():continue
  country=(item.get('location') or {}).get('countryCode')
  if country and re.fullmatch('[A-Z]{2}',country):b['countries']=sorted(set(b['countries']+[country]))
  region=(item.get('location') or {}).get('subnational1Code')
  if region and re.fullmatch('[A-Z]{2}-[A-Za-z0-9]+',region):b['regions']=sorted(set(b.get('regions',[])+[region]))
  if not b.get('photo'):
   location=item.get('location') or {}
   place=next((location.get(k) or item.get(k) for k in ['locName','locationName','name'] if location.get(k) or item.get(k)),None)
   photo={'assetId':asset,'assetUrl':f'https://macaulaylibrary.org/asset/{asset}','imageUrl':f'https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset}/640','credit':data['owner']}
   country=location.get('countryCode');subregion=location.get('subnational1Code')
   if place:photo['locationName']=str(place)
   if country and re.fullmatch('[A-Z]{2}',country):photo['countryCode']=country
   if subregion and re.fullmatch('[A-Z]{2}-[A-Za-z0-9]+',subregion):photo['regionCode']=subregion
   b['photo']=photo;accepted+=1
 if not accepted:raise ValueError('No matching contributor-verified photos; retaining previous snapshot')
 return birds,sorted(unmatched)

def sync_photos(data):
 cursor='';seen=set();media=[]
 for _ in range(100):
  params={'count':100,'unconfirmed':'incl','sort':'rating_rank_desc','mediaType':'photo','birdOnly':'true','userId':'USER'+data['contributorId'],'taxaLocale':'en','initialCursorMark':cursor}
  batch=fetch('https://ebird.org/ml-search-api/v2/search?'+urllib.parse.urlencode(params))
  if not isinstance(batch,list):raise ValueError('Invalid media response')
  media.extend(batch)
  if len(batch)<100:break
  cursor=batch[-1].get('cursorMark')
  if not cursor or cursor in seen:raise ValueError('Invalid media pagination; retaining snapshot')
  seen.add(cursor)
 else:raise ValueError('Media page limit reached')
 return apply_photos(data,media)

def refresh(data,photos=True):
 data=json.loads(json.dumps(data));errors=[];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:data['countries']=sync_countries(data);data['lastCountrySync']=now
 except Exception as e:errors.append('Country sync: '+str(e))
 for country in data.get('countries',[]):
  code=country['code']
  try:
   raw=fetch('https://ebird.org/prof/count/species?'+urllib.parse.urlencode({'username':data['profileId'],'r':code}))
   if not isinstance(raw,list) or any(not isinstance(row,list) or len(row)!=2 or not str(row[0]).startswith(code+'-') for row in raw):raise ValueError('Unexpected regional count response')
   data.setdefault('regions',{})[code]=[[row[0],int(row[1])] for row in raw]
  except Exception as e:errors.append('Region sync '+code+': '+str(e))
 if photos:
  try:
   data['species'],data['unmatchedPhotoTaxa']=sync_photos(data);data['lastPhotoSync']=now;data['photoStatus']='public-api-snapshot'
  except Exception as e:errors.append('Photo sync: '+str(e))
 data['syncWarnings']=errors
 return data,errors

def main():
 p=argparse.ArgumentParser();p.add_argument('--photos',action='store_true');args=p.parse_args();path=ROOT/'data/birds.json'
 data,errors=refresh(json.loads(path.read_text('utf-8')),args.photos);atomic_write(path,data)
 print('Countries:',len(data['countries']),'species:',len(data['species']),'with photos:',sum(bool(b.get('photo')) for b in data['species']))
 if data.get('unmatchedPhotoTaxa'):print('Unmatched photo taxa:',', '.join(data['unmatchedPhotoTaxa']))
 for e in errors:print(e,file=sys.stderr)
 if errors:sys.exit(1)
if __name__=='__main__':main()
